from sqlmodel import Session

from app.agents.blog_brain_state_agent import BlogBrainStateAgent
from app.agents.fragment_analysis_agent import FragmentAnalysisAgent
from app.agents.research_agent import ResearchAgent
from app.agents.research_planner_agent import ResearchPlannerAgent
from app.agents.qa_guardrails_agent import QaGuardrailsAgent
from app.agents.transcription_agent import TranscriptionAgent
from app.agents.writing_agent import WritingAgent
from app.core.events import event_hub
from app.repositories.blog_repository import BlogRepository


class OrchestrationService:
    """Coordinate only the fragment-understanding steps available in stage 3."""

    def __init__(self, session: Session) -> None:
        self.repo = BlogRepository(session)
        self.transcription_agent = TranscriptionAgent()
        self.analysis_agent = FragmentAnalysisAgent()
        self.blog_brain_agent = BlogBrainStateAgent()
        self.research_planner_agent = ResearchPlannerAgent()
        self.research_agent = ResearchAgent()
        self.writing_agent = WritingAgent()
        self.qa_agent = QaGuardrailsAgent()

    async def process_fragment(self, fragment_id: str) -> str | None:
        # Agents run synchronously in this MVP; async is used here for non-blocking event publication.
        fragment = self.repo.get_fragment(fragment_id)
        if fragment is None:
            return None
        if fragment.status == "validated":
            return fragment.status

        await self._event(fragment.blog_id, "fragment.received", {"fragment_id": fragment.id})

        if not fragment.transcript:
            transcription = self.transcription_agent.run(fragment.id, fragment.audio_url)
            if transcription["status"] != "completed":
                fragment.status = transcription["status"]
                self.repo.session.add(fragment)
                self.repo.session.commit()
                await self._event(
                    fragment.blog_id,
                    "fragment.transcription_failed",
                    {"fragment_id": fragment.id, "status": fragment.status},
                    status="failed",
                )
                return fragment.status
            fragment.transcript = transcription["transcript"]
            fragment.status = "transcribed"

        analysis = self.analysis_agent.run(fragment.transcript or "")
        self.repo.save_fragment_analysis(fragment.id, analysis)
        await self._event(fragment.blog_id, "fragment.analyzed", {"fragment_id": fragment.id})

        current = self.repo.get_latest_blog_brain(fragment.blog_id)
        guardrail = self.repo.get_guardrail(fragment.blog_id)
        guardrails = {
            "tone": guardrail.tone if guardrail else "conversational",
            "length": guardrail.length if guardrail else "1200-1800",
            "preserve_voice": guardrail.preserve_voice if guardrail else True,
            "citation_required": guardrail.citation_required if guardrail else True,
            "banned_topics": guardrail.banned_topics if guardrail else [],
        }
        updated = self.blog_brain_agent.run(current.payload if current else {}, analysis, guardrails)
        self.repo.save_blog_brain(fragment.blog_id, updated)
        await self._event(fragment.blog_id, "blog_brain.updated", {"fragment_id": fragment.id})
        claims = self.repo.upsert_claims(fragment.blog_id, analysis["claims"])
        existing_questions = [item.question for item in self.repo.list_research_questions(fragment.blog_id)]
        plans = self.research_planner_agent.run(analysis["claims"], existing_questions)
        self.repo.create_research_questions(fragment.blog_id, plans)
        if plans:
            await self._event(fragment.blog_id, "research.queued", {"count": len(plans)})

        if any(claim.source_required for claim in claims):
            completed = self.run_research(fragment.blog_id)
            if completed:
                fragment.status = "researched"
                await self._event(fragment.blog_id, "research.completed", {"count": completed})

        if fragment.status != "researched":
            fragment.status = "analyzed"
        self.repo.session.add(fragment)
        self.repo.session.commit()

        draft_payload = self.generate_draft(fragment.blog_id)
        if draft_payload is not None:
            await self._event(
                fragment.blog_id,
                "draft.updated",
                {"draft_id": draft_payload["id"], "version": draft_payload["version"]},
            )
            qa = self.validate_draft(str(draft_payload["id"]))
            fragment.status = "validated"
            self.repo.session.add(fragment)
            self.repo.session.commit()
            await self._event(
                fragment.blog_id,
                "draft.validated",
                {"draft_id": draft_payload["id"], "passed": qa["passed"] if qa else False},
            )
        return fragment.status

    async def _event(
        self,
        blog_id: str,
        event_type: str,
        payload: dict[str, object],
        *,
        status: str = "ok",
    ) -> None:
        self.repo.add_event(blog_id, event_type, payload, status=status)
        await event_hub.publish(event_type, blog_id, payload)

    def run_research(self, blog_id: str, *, deep: bool = False) -> int:
        completed = 0
        claims = [claim for claim in self.repo.list_claims(blog_id) if claim.source_required]
        for question in self.repo.list_research_questions(blog_id):
            if question.status != "pending":
                continue
            finding = self.research_agent.run(question.question, deep=deep)
            sources_by_url = {
                item["url"]: self.repo.add_source(blog_id, item)
                for item in finding["sources"]
            }
            matching_claims = [
                claim
                for claim in claims
                if self.repo.normalize_claim(claim.text) in self.repo.normalize_claim(question.question)
            ]
            for evidence in finding["evidence"]:
                source = sources_by_url.get(evidence.get("source_url"))
                if source is None:
                    continue
                for claim in matching_claims:
                    self.repo.add_evidence(
                        claim.id,
                        source.id,
                        evidence["supporting_text"],
                        evidence["confidence"],
                    )
            sufficient = finding["status"] == "completed"
            self.repo.mark_research_complete(question.id, sufficient=sufficient)
            for claim in matching_claims:
                claim.research_status = "completed" if sufficient else "insufficient"
                if sufficient:
                    claim.origin_type = "RESEARCH_FACT"
                self.repo.session.add(claim)
            self.repo.session.commit()
            completed += int(sufficient)
        return completed

    def generate_draft(self, blog_id: str) -> dict[str, object] | None:
        blog = self.repo.get_blog(blog_id)
        brain = self.repo.get_latest_blog_brain(blog_id)
        if blog is None or brain is None:
            return None
        sources = self.repo.list_sources(blog_id)
        findings = [{"sources": [{"title": source.title, "url": source.url}]} for source in sources]
        latest = self.repo.get_latest_draft(blog_id)
        output = self.writing_agent.run(blog.title, brain.payload, findings, latest.content if latest else None)
        draft = self.repo.save_draft(blog_id, output["draft_content"], output["provenance_map"])
        return self._draft_payload(draft)

    def revise_draft(self, draft_id: str, revision_prompt: str) -> dict[str, object] | None:
        draft = self.repo.get_draft(draft_id)
        if draft is None:
            return None
        content = f"{draft.content}\n\nRevision request applied: {revision_prompt}"
        return self._draft_payload(self.repo.save_draft(draft.blog_id, content, draft.provenance_map))

    def validate_draft(self, draft_id: str) -> dict[str, object] | None:
        draft = self.repo.get_draft(draft_id)
        if draft is None:
            return None
        brain = self.repo.get_latest_blog_brain(draft.blog_id)
        guardrail = self.repo.get_guardrail(draft.blog_id)
        guardrails = {
            "tone": guardrail.tone,
            "length": guardrail.length,
            "preserve_voice": guardrail.preserve_voice,
            "citation_required": guardrail.citation_required,
            "banned_topics": guardrail.banned_topics,
        } if guardrail else None
        result = self.qa_agent.run(
            draft.content,
            brain.payload if brain else {},
            citation_required=guardrail.citation_required if guardrail else True,
            guardrails=guardrails,
        )
        self.repo.save_qa_result(draft.id, result)
        return result

    def sentence_why(self, draft_id: str, sentence_id: str) -> dict[str, object] | None:
        draft = self.repo.get_draft(draft_id)
        if draft is None:
            return None
        provenance = draft.provenance_map.get(sentence_id, {})
        lines = [line for line in draft.content.splitlines() if line.strip()]
        try:
            index = max(int(sentence_id.removeprefix("s_")) - 1, 0)
        except ValueError:
            index = 0
        sentence_text = lines[index] if index < len(lines) else ""
        evidence = self.repo.list_evidence(draft.blog_id)
        confidence = max((item.confidence for item, _ in evidence), default=0.75)
        return {
            "sentence_id": sentence_id,
            "sentence_text": sentence_text,
            "user_basis": [provenance["basis"]] if provenance.get("basis") == "blog_brain" else [],
            "ai_interpretation": f"Origin: {provenance.get('origin', 'AI_GENERATED')}.",
            "source_evidence": [
                {
                    "sourceTitle": source.title,
                    "sourceUrl": source.url,
                    "supportText": item.supporting_text,
                }
                for item, source in evidence
            ],
            "confidence": confidence,
        }

    @staticmethod
    def _draft_payload(draft) -> dict[str, object]:
        return {
            "id": draft.id,
            "blog_id": draft.blog_id,
            "version": draft.version,
            "content": draft.content,
            "word_count": len(draft.content.split()),
            "updated_at": draft.created_at,
        }
