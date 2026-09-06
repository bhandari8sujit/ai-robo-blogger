from datetime import datetime, UTC
from typing import Any

from sqlmodel import Session, desc, select

from app.models import (
    Blog,
    BlogBrainSnapshot,
    Claim,
    Draft,
    Evidence,
    Fragment,
    FragmentAnalysis,
    Guardrail,
    ProcessingEvent,
    QaResult,
    ResearchQuestion,
    Source,
)


class BlogRepository:
    def __init__(self, session: Session) -> None:
        # The request-scoped SQLModel session is injected rather than created by the repository.
        self.session = session

    def create_blog(self, user_id: str, title: str) -> Blog:
        blog = Blog(user_id=user_id, title=title, status="draft")
        self.session.add(blog)
        self.session.commit()
        # `refresh` reloads database-generated values such as defaults after commit.
        self.session.refresh(blog)

        guardrail = Guardrail(blog_id=blog.id)
        self.session.add(guardrail)

        snapshot = BlogBrainSnapshot(
            blog_id=blog.id,
            version=1,
            payload={
                "thesis": "",
                "arguments": [],
                "sentiment": {"primary": "curious", "secondary": None, "intensity": 0.5},
                "intent": "exploration",
                "open_questions": [],
                "contradictions": 0,
            },
        )
        self.session.add(snapshot)
        self.session.commit()
        return blog

    def get_blog(self, blog_id: str) -> Blog | None:
        # Session.get performs a primary-key lookup and returns None instead of raising when absent.
        return self.session.get(Blog, blog_id)

    def list_fragments(self, blog_id: str) -> list[Fragment]:
        # SQLModel statements are composed first and executed explicitly through the session.
        statement = select(Fragment).where(Fragment.blog_id == blog_id).order_by(Fragment.created_at)
        return list(self.session.exec(statement))

    def create_fragment(self, blog_id: str, audio_url: str, duration_seconds: float, transcript: str | None = None) -> Fragment:
        fragment = Fragment(
            blog_id=blog_id,
            audio_url=audio_url,
            duration_seconds=duration_seconds,
            transcript=transcript,
            status="uploaded",
        )
        self.session.add(fragment)
        self.session.commit()
        self.session.refresh(fragment)
        return fragment

    def get_fragment(self, fragment_id: str) -> Fragment | None:
        return self.session.get(Fragment, fragment_id)

    def save_fragment_analysis(self, fragment_id: str, analysis: dict[str, Any]) -> FragmentAnalysis:
        item = FragmentAnalysis(
            fragment_id=fragment_id,
            summary=analysis["summary"],
            topics=analysis["topics"],
            claims=analysis["claims"],
            questions=analysis["questions"],
            personal_experiences=analysis["personal_experiences"],
            sentiment=analysis["sentiment"],
            intent=analysis["intent"],
        )
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def get_latest_blog_brain(self, blog_id: str) -> BlogBrainSnapshot | None:
        # `desc` sorts newest version first, making `.first()` the latest snapshot.
        statement = (
            select(BlogBrainSnapshot)
            .where(BlogBrainSnapshot.blog_id == blog_id)
            .order_by(desc(BlogBrainSnapshot.version))
        )
        return self.session.exec(statement).first()

    def save_blog_brain(self, blog_id: str, payload: dict[str, Any]) -> BlogBrainSnapshot:
        current = self.get_latest_blog_brain(blog_id)
        next_version = 1 if current is None else current.version + 1
        snapshot = BlogBrainSnapshot(blog_id=blog_id, version=next_version, payload=payload)
        self.session.add(snapshot)

        blog = self.get_blog(blog_id)
        if blog is not None:
            blog.thesis = payload.get("thesis") or blog.thesis
            blog.updated_at = datetime.now(UTC)
            self.session.add(blog)

        self.session.commit()
        self.session.refresh(snapshot)
        return snapshot

    def upsert_claims(self, blog_id: str, claims: list[dict[str, Any]]) -> list[Claim]:
        # This currently inserts each extracted claim; the name leaves room for future deduplication.
        created: list[Claim] = []
        for claim_data in claims:
            claim = Claim(
                blog_id=blog_id,
                text=claim_data["text"],
                source_required=claim_data.get("requires_research", True),
                research_status="pending" if claim_data.get("requires_research", True) else "completed",
                confidence=claim_data.get("confidence", 0.6),
                origin_type="AI_INFERENCE",
            )
            self.session.add(claim)
            created.append(claim)
        self.session.commit()
        return created

    def list_claims(self, blog_id: str) -> list[Claim]:
        statement = select(Claim).where(Claim.blog_id == blog_id).order_by(Claim.id)
        return list(self.session.exec(statement))

    def create_research_questions(self, blog_id: str, questions: list[dict[str, str]]) -> list[ResearchQuestion]:
        output: list[ResearchQuestion] = []
        for question_data in questions:
            item = ResearchQuestion(
                blog_id=blog_id,
                question=question_data["question"],
                status="pending",
                priority=question_data.get("priority", "medium"),
            )
            self.session.add(item)
            output.append(item)
        self.session.commit()
        return output

    def list_research_questions(self, blog_id: str) -> list[ResearchQuestion]:
        statement = select(ResearchQuestion).where(ResearchQuestion.blog_id == blog_id).order_by(ResearchQuestion.id)
        return list(self.session.exec(statement))

    def mark_research_complete(self, question_id: str) -> None:
        question = self.session.get(ResearchQuestion, question_id)
        if question is not None:
            question.status = "completed"
            self.session.add(question)
            self.session.commit()

    def add_source(self, blog_id: str, source_data: dict[str, Any]) -> Source:
        source = Source(
            blog_id=blog_id,
            title=source_data["title"],
            url=source_data["url"],
            publisher=source_data.get("publisher"),
            published_at=source_data.get("published_at"),
            credibility=source_data.get("credibility", 0.6),
        )
        self.session.add(source)
        self.session.commit()
        self.session.refresh(source)
        return source

    def list_sources(self, blog_id: str) -> list[Source]:
        statement = select(Source).where(Source.blog_id == blog_id).order_by(Source.retrieved_at)
        return list(self.session.exec(statement))

    def add_evidence(self, claim_id: str, source_id: str, supporting_text: str, confidence: float) -> Evidence:
        evidence = Evidence(claim_id=claim_id, source_id=source_id, supporting_text=supporting_text, confidence=confidence)
        self.session.add(evidence)
        self.session.commit()
        self.session.refresh(evidence)
        return evidence

    def save_draft(self, blog_id: str, content: str, provenance_map: dict[str, Any]) -> Draft:
        # Versions are computed per blog so draft history is append-only.
        statement = select(Draft).where(Draft.blog_id == blog_id).order_by(desc(Draft.version))
        latest = self.session.exec(statement).first()
        version = 1 if latest is None else latest.version + 1

        draft = Draft(blog_id=blog_id, content=content, version=version, provenance_map=provenance_map)
        self.session.add(draft)
        self.session.commit()
        self.session.refresh(draft)
        return draft

    def get_draft(self, draft_id: str) -> Draft | None:
        return self.session.get(Draft, draft_id)

    def get_latest_draft(self, blog_id: str) -> Draft | None:
        statement = select(Draft).where(Draft.blog_id == blog_id).order_by(desc(Draft.version))
        return self.session.exec(statement).first()

    def save_qa_result(self, draft_id: str, payload: dict[str, Any]) -> QaResult:
        item = QaResult(
            draft_id=draft_id,
            passed=payload["passed"],
            issues=payload["issues"],
            voice_score=payload["voice_score"],
            factuality_score=payload["factuality_score"],
            publish_blocked=payload["publish_blocked"],
        )
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def get_guardrail(self, blog_id: str) -> Guardrail | None:
        statement = select(Guardrail).where(Guardrail.blog_id == blog_id)
        return self.session.exec(statement).first()

    def add_event(self, blog_id: str, event_type: str, payload: dict[str, Any], status: str = "ok", attempt: int = 1) -> ProcessingEvent:
        event = ProcessingEvent(blog_id=blog_id, event_type=event_type, payload=payload, status=status, attempt=attempt)
        self.session.add(event)
        self.session.commit()
        self.session.refresh(event)
        return event

    def timeline(self, blog_id: str) -> list[ProcessingEvent]:
        statement = select(ProcessingEvent).where(ProcessingEvent.blog_id == blog_id).order_by(ProcessingEvent.created_at)
        return list(self.session.exec(statement))
