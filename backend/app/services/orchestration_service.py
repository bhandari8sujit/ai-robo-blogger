from __future__ import annotations

from datetime import datetime, UTC
from typing import Any

from langchain_core.runnables import RunnableLambda
from sqlmodel import Session

from app.agents.blog_brain_state_agent import BlogBrainStateAgent
from app.agents.fragment_analysis_agent import FragmentAnalysisAgent
from app.agents.qa_guardrails_agent import QaGuardrailsAgent
from app.agents.research_agent import ResearchAgent
from app.agents.research_planner_agent import ResearchPlannerAgent
from app.agents.transcription_agent import TranscriptionAgent
from app.agents.writing_agent import WritingAgent
from app.core.events import event_hub
from app.repositories.blog_repository import BlogRepository


class OrchestrationService:
    def __init__(self, session: Session) -> None:
    # Agents are lightweight collaborators; the injected session scopes persistence to this request.
        self.repo = BlogRepository(session)
        self.transcription_agent = TranscriptionAgent()
        self.fragment_analysis_agent = FragmentAnalysisAgent()
        self.blog_brain_agent = BlogBrainStateAgent()
        self.research_planner_agent = ResearchPlannerAgent()
        self.research_agent = ResearchAgent()
        self.writing_agent = WritingAgent()
        self.qa_agent = QaGuardrailsAgent()

    async def process_fragment(self, fragment_id: str) -> None:
        # The public method is async because it publishes events, though agent runnables invoke synchronously.
        fragment = self.repo.get_fragment(fragment_id)
        if fragment is None:
            return

        blog = self.repo.get_blog(fragment.blog_id)
        if blog is None:
            return

        self.repo.add_event(blog.id, "fragment.received", {"fragment_id": fragment.id})

        if not fragment.transcript:
            # RunnableLambda adapts a normal callable to LangChain's `.invoke()` interface.
            transcription = RunnableLambda(
                lambda _: self.transcription_agent.run(fragment.id, fragment.audio_url)
            ).invoke({})
            if transcription["status"] != "completed":
                fragment.status = transcription["status"]
                self.repo.session.add(fragment)
                self.repo.session.commit()
                self.repo.add_event(blog.id, "fragment.transcription_failed", transcription, status="failed")
                await event_hub.publish(
                    "fragment_processing_failed",
                    blog.id,
                    {"fragmentId": fragment.id, "status": fragment.status},
                )
                return
            fragment.transcript = transcription["transcript"]
            fragment.status = "transcribed"
            self.repo.session.add(fragment)
            self.repo.session.commit()
            self.repo.add_event(blog.id, "fragment.transcribed", transcription)

        analysis = RunnableLambda(
            lambda _: self.fragment_analysis_agent.run(fragment.transcript or "")
        ).invoke({})
        self.repo.save_fragment_analysis(fragment.id, analysis)
        fragment.status = "analyzed"
        self.repo.session.add(fragment)
        self.repo.session.commit()
        self.repo.add_event(blog.id, "fragment.analyzed", {"fragment_id": fragment.id})

        current = self.repo.get_latest_blog_brain(blog.id)
        current_payload = current.payload if current else {}

        guardrail = self.repo.get_guardrail(blog.id)
        guardrail_payload = {
            "tone": guardrail.tone if guardrail else "conversational",
            "length": guardrail.length if guardrail else "1200-1800",
            "citation_required": guardrail.citation_required if guardrail else True,
            "preserve_voice": guardrail.preserve_voice if guardrail else True,
            "banned_topics": guardrail.banned_topics if guardrail else [],
        }

        updated_state = RunnableLambda(
            lambda _: self.blog_brain_agent.run(current_payload, analysis, guardrail_payload)
        ).invoke({})
        self.repo.save_blog_brain(blog.id, updated_state)
        self.repo.add_event(blog.id, "blog_brain.updated", {"fragment_id": fragment.id})

        created_claims = self.repo.upsert_claims(blog.id, analysis["claims"])
        existing_questions = [question.question for question in self.repo.list_research_questions(blog.id)]
        queued_questions = RunnableLambda(
            lambda _: self.research_planner_agent.run(analysis["claims"], existing_questions)
        ).invoke({})
        if queued_questions:
            self.repo.create_research_questions(blog.id, queued_questions)
            self.repo.add_event(blog.id, "research.queued", {"count": len(queued_questions)})

        # The comprehension retains only claims that need evidence gathering.
        pending_claims = [claim for claim in created_claims if claim.source_required]
        findings: list[dict[str, Any]] = []
        if pending_claims:
            for question in self.repo.list_research_questions(blog.id):
                if question.status != "pending":
                    continue
                finding = RunnableLambda(lambda _: self.research_agent.run(question.question)).invoke({})
                findings.append(finding)
                for source_data in finding["sources"]:
                    source = self.repo.add_source(blog.id, source_data)
                    for claim in pending_claims:
                        for evidence in finding["evidence"]:
                            self.repo.add_evidence(claim.id, source.id, evidence["supporting_text"], evidence["confidence"])
                self.repo.mark_research_complete(question.id)

            for claim in pending_claims:
                claim.research_status = "completed"
                claim.origin_type = "RESEARCH_FACT"
                self.repo.session.add(claim)
            self.repo.session.commit()

            self.repo.add_event(blog.id, "research.completed", {"questions": len(findings)})
            fragment.status = "researched"
            self.repo.session.add(fragment)
            self.repo.session.commit()

        latest_draft = self.repo.get_latest_draft(blog.id)
        draft_output = RunnableLambda(
            lambda _: self.writing_agent.run(
                blog.title,
                updated_state,
                findings,
                latest_draft.content if latest_draft else None,
            )
        ).invoke({})

        draft = self.repo.save_draft(blog.id, draft_output["draft_content"], draft_output["provenance_map"])
        self.repo.add_event(blog.id, "draft.updated", {"draft_id": draft.id, "version": draft.version})
        fragment.status = "drafted"
        self.repo.session.add(fragment)
        self.repo.session.commit()

        qa = RunnableLambda(
            lambda _: self.qa_agent.run(
                draft.content,
                updated_state,
                citation_required=guardrail_payload["citation_required"],
                guardrails=guardrail_payload,
            )
        ).invoke({})
        self.repo.save_qa_result(draft.id, qa)
        fragment.status = "validated"
        self.repo.session.add(fragment)
        self.repo.session.commit()
        self.repo.add_event(blog.id, "draft.validated", {"draft_id": draft.id, "passed": qa["passed"]})

        await event_hub.publish("fragment_processed", blog.id, {"fragmentId": fragment.id, "status": fragment.status})
        await event_hub.publish("draft_updated", blog.id, {"draftId": draft.id, "version": draft.version})

    async def run_research(self, blog_id: str) -> int:
        questions = self.repo.list_research_questions(blog_id)
        completed = 0

        for question in questions:
            if question.status != "pending":
                continue
            finding = RunnableLambda(
                lambda _: self.research_agent.run(question.question, deep=True)
            ).invoke({})
            for source_data in finding["sources"]:
                self.repo.add_source(blog_id, source_data)
            self.repo.mark_research_complete(question.id)
            completed += 1

        self.repo.add_event(blog_id, "research.manual_run", {"completed": completed})
        await event_hub.publish("research_completed", blog_id, {"completed": completed})
        return completed

    def generate_draft(self, blog_id: str) -> dict[str, Any] | None:
        blog = self.repo.get_blog(blog_id)
        if blog is None:
            return None

        brain = self.repo.get_latest_blog_brain(blog_id)
        if brain is None:
            return None

        sources = self.repo.list_sources(blog_id)
        findings = [
            {
                "research_summary": f"Source: {source.title}",
            }
            for source in sources
        ]

        latest = self.repo.get_latest_draft(blog_id)
        draft_output = RunnableLambda(
            lambda _: self.writing_agent.run(blog.title, brain.payload, findings, latest.content if latest else None)
        ).invoke({})
        draft = self.repo.save_draft(blog_id, draft_output["draft_content"], draft_output["provenance_map"])
        self.repo.add_event(blog_id, "draft.manual_generate", {"draft_id": draft.id, "version": draft.version})

        return {
            "id": draft.id,
            "blog_id": draft.blog_id,
            "version": draft.version,
            "content": draft.content,
            "word_count": len(draft.content.split()),
            "updated_at": draft.created_at,
        }

    def revise_draft(self, draft_id: str, revision_prompt: str) -> dict[str, Any] | None:
        draft = self.repo.get_draft(draft_id)
        if draft is None:
            return None

        revised_content = f"{draft.content}\n\nRevision request applied: {revision_prompt}"
        new_draft = self.repo.save_draft(draft.blog_id, revised_content, draft.provenance_map)
        self.repo.add_event(draft.blog_id, "draft.revised", {"draft_id": new_draft.id, "version": new_draft.version})

        return {
            "id": new_draft.id,
            "blog_id": new_draft.blog_id,
            "version": new_draft.version,
            "content": new_draft.content,
            "word_count": len(new_draft.content.split()),
            "updated_at": new_draft.created_at,
        }

    def validate_draft(self, draft_id: str) -> dict[str, Any] | None:
        draft = self.repo.get_draft(draft_id)
        if draft is None:
            return None

        brain = self.repo.get_latest_blog_brain(draft.blog_id)
        guardrail = self.repo.get_guardrail(draft.blog_id)
        payload = RunnableLambda(
            lambda _: self.qa_agent.run(
                draft.content,
                brain.payload if brain else {},
                citation_required=guardrail.citation_required if guardrail else True,
                guardrails={
                    "tone": guardrail.tone,
                    "length": guardrail.length,
                    "preserve_voice": guardrail.preserve_voice,
                    "citation_required": guardrail.citation_required,
                    "banned_topics": guardrail.banned_topics,
                }
                if guardrail
                else None,
            )
        ).invoke({})
        self.repo.save_qa_result(draft.id, payload)

        self.repo.add_event(draft.blog_id, "draft.revalidated", {"draft_id": draft.id, "passed": payload["passed"]})
        return payload

    def sentence_why(self, draft_id: str, sentence_id: str) -> dict[str, Any] | None:
        draft = self.repo.get_draft(draft_id)
        if draft is None:
            return None

        provenance = draft.provenance_map.get(sentence_id, {})
        return {
            "sentence_id": sentence_id,
            "sentence_text": draft.content.splitlines()[0] if draft.content else "",
            "user_basis": ["Derived from spoken fragment summary."],
            "ai_interpretation": f"Origin: {provenance.get('origin', 'AI_GENERATED')}.",
            "source_evidence": [
                {
                    "sourceTitle": "Example Publisher",
                    "sourceUrl": "https://example.com/research",
                    "supportText": "Evidence indicates variation by task.",
                }
            ],
            "confidence": 0.84,
        }

    def blog_state(self, blog_id: str) -> dict[str, Any] | None:
        blog = self.repo.get_blog(blog_id)
        if blog is None:
            return None

        brain = self.repo.get_latest_blog_brain(blog_id)
        claims = self.repo.list_claims(blog_id)
        fragment_list = self.repo.list_fragments(blog_id)
        last_status = fragment_list[-1].status if fragment_list else "uploaded"

        now = datetime.now(UTC)
        payload = brain.payload if brain else {}

        def card(value: Any, origin: str) -> dict[str, Any]:
            # A nested helper captures `now`, ensuring all cards in one response share one timestamp.
            return {
                "value": value,
                "confidence": 0.8,
                "originType": origin,
                "updatedAt": now,
            }

        return {
            "blog_id": blog.id,
            "title": blog.title,
            "thesis": card(payload.get("thesis", ""), "AI_INFERENCE"),
            "arguments": card(payload.get("arguments", []), "AI_INFERENCE"),
            "sentiment": card(payload.get("sentiment", {"primary": "curious", "secondary": None, "intensity": 0.5}), "AI_INFERENCE"),
            "intent": card(payload.get("intent", "exploration"), "AI_INFERENCE"),
            "open_questions": card(payload.get("open_questions", []), "AI_INFERENCE"),
            "claims": [
                {
                    "id": claim.id,
                    "text": claim.text,
                    "requires_research": claim.source_required,
                    "confidence": claim.confidence,
                    "origin_type": claim.origin_type,
                    "research_status": claim.research_status,
                }
                for claim in claims
            ],
            "contradiction_count": payload.get("contradictions", 0),
            "processing_status": last_status,
        }
