from sqlmodel import Session

from app.agents.blog_brain_state_agent import BlogBrainStateAgent
from app.agents.fragment_analysis_agent import FragmentAnalysisAgent
from app.agents.transcription_agent import TranscriptionAgent
from app.repositories.blog_repository import BlogRepository


class OrchestrationService:
    """Coordinate only the fragment-understanding steps available in stage 3."""

    def __init__(self, session: Session) -> None:
        self.repo = BlogRepository(session)
        self.transcription_agent = TranscriptionAgent()
        self.analysis_agent = FragmentAnalysisAgent()
        self.blog_brain_agent = BlogBrainStateAgent()

    def process_fragment(self, fragment_id: str) -> str | None:
        fragment = self.repo.get_fragment(fragment_id)
        if fragment is None:
            return None

        if not fragment.transcript:
            transcription = self.transcription_agent.run(fragment.id, fragment.audio_url)
            if transcription["status"] != "completed":
                fragment.status = transcription["status"]
                self.repo.session.add(fragment)
                self.repo.session.commit()
                return fragment.status
            fragment.transcript = transcription["transcript"]
            fragment.status = "transcribed"

        analysis = self.analysis_agent.run(fragment.transcript or "")
        self.repo.save_fragment_analysis(fragment.id, analysis)

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
        self.repo.upsert_claims(fragment.blog_id, analysis["claims"])

        fragment.status = "analyzed"
        self.repo.session.add(fragment)
        self.repo.session.commit()
        return fragment.status
