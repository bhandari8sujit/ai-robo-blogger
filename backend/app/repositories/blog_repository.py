from datetime import UTC, datetime
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
    QaResult,
    ResearchQuestion,
    Source,
)


class BlogRepository:
    def __init__(self, session: Session) -> None:
        # FastAPI owns the request-scoped session; the repository only uses it.
        self.session = session

    def create_blog(self, user_id: str, title: str) -> Blog:
        blog = Blog(user_id=user_id, title=title, status="draft")
        self.session.add(blog)
        self.session.commit()
        # Refresh reloads database-generated defaults after the insert.
        self.session.refresh(blog)
        self.session.add(Guardrail(blog_id=blog.id))
        self.session.add(BlogBrainSnapshot(blog_id=blog.id, version=1, payload=self.empty_brain()))
        self.session.commit()
        return blog

    @staticmethod
    def empty_brain() -> dict[str, Any]:
        return {
            "thesis": "",
            "arguments": [],
            "sentiment": {"primary": "curious", "secondary": None, "intensity": 0.5},
            "intent": "exploration",
            "open_questions": [],
            "contradictions": 0,
        }

    def get_blog(self, blog_id: str) -> Blog | None:
        return self.session.get(Blog, blog_id)

    def get_owned_blog(self, blog_id: str, user_id: str) -> Blog | None:
        statement = select(Blog).where(Blog.id == blog_id, Blog.user_id == user_id)
        return self.session.exec(statement).first()

    def get_latest_blog_brain(self, blog_id: str) -> BlogBrainSnapshot | None:
        statement = (
            select(BlogBrainSnapshot)
            .where(BlogBrainSnapshot.blog_id == blog_id)
            .order_by(desc(BlogBrainSnapshot.version))
        )
        return self.session.exec(statement).first()

    def save_blog_brain(self, blog_id: str, payload: dict[str, Any]) -> BlogBrainSnapshot:
        current = self.get_latest_blog_brain(blog_id)
        snapshot = BlogBrainSnapshot(
            blog_id=blog_id,
            version=1 if current is None else current.version + 1,
            payload=payload,
        )
        self.session.add(snapshot)
        blog = self.get_blog(blog_id)
        if blog is not None:
            blog.thesis = payload.get("thesis") or blog.thesis
            blog.updated_at = datetime.now(UTC)
            self.session.add(blog)
        self.session.commit()
        self.session.refresh(snapshot)
        return snapshot

    def get_guardrail(self, blog_id: str) -> Guardrail | None:
        return self.session.exec(select(Guardrail).where(Guardrail.blog_id == blog_id)).first()

    def create_fragment(
        self,
        blog_id: str,
        audio_url: str,
        duration_seconds: float,
        transcript: str | None = None,
    ) -> Fragment:
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

    def get_owned_fragment(self, fragment_id: str, user_id: str) -> Fragment | None:
        statement = (
            select(Fragment)
            .join(Blog, Blog.id == Fragment.blog_id)
            .where(Fragment.id == fragment_id, Blog.user_id == user_id)
        )
        return self.session.exec(statement).first()

    def list_fragments(self, blog_id: str) -> list[Fragment]:
        statement = select(Fragment).where(Fragment.blog_id == blog_id).order_by(Fragment.created_at)
        return list(self.session.exec(statement))

    def save_fragment_analysis(self, fragment_id: str, analysis: dict[str, Any]) -> FragmentAnalysis:
        item = FragmentAnalysis(fragment_id=fragment_id, **analysis)
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    @staticmethod
    def normalize_claim(text: str) -> str:
        return " ".join(text.casefold().split()).rstrip(".!?")

    def upsert_claims(self, blog_id: str, claims: list[dict[str, Any]]) -> list[Claim]:
        output: list[Claim] = []
        for claim_data in claims:
            normalized = self.normalize_claim(claim_data["text"])
            statement = select(Claim).where(Claim.blog_id == blog_id, Claim.normalized_text == normalized)
            claim = self.session.exec(statement).first()
            requires_research = claim_data.get("requires_research", True)
            if claim is None:
                claim = Claim(
                    blog_id=blog_id,
                    text=claim_data["text"].strip(),
                    normalized_text=normalized,
                    source_required=requires_research,
                    research_status="pending" if requires_research else "completed",
                    confidence=claim_data.get("confidence", 0.6),
                )
            else:
                claim.source_required = claim.source_required or requires_research
                claim.confidence = max(claim.confidence, claim_data.get("confidence", 0.6))
                if claim.source_required and claim.research_status == "completed":
                    claim.research_status = "pending"
            self.session.add(claim)
            output.append(claim)
        self.session.commit()
        return output

    def list_claims(self, blog_id: str) -> list[Claim]:
        return list(self.session.exec(select(Claim).where(Claim.blog_id == blog_id).order_by(Claim.id)))

    def create_research_questions(self, blog_id: str, questions: list[dict[str, Any]]) -> list[ResearchQuestion]:
        output: list[ResearchQuestion] = []
        for question_data in questions:
            normalized = " ".join(question_data["question"].casefold().split()).rstrip(".!?")
            statement = select(ResearchQuestion).where(
                ResearchQuestion.blog_id == blog_id,
                ResearchQuestion.normalized_question == normalized,
            )
            item = self.session.exec(statement).first()
            if item is None:
                item = ResearchQuestion(
                    blog_id=blog_id,
                    question=question_data["question"],
                    normalized_question=normalized,
                    priority=question_data.get("priority", "medium"),
                )
                self.session.add(item)
            output.append(item)
        self.session.commit()
        return output

    def list_research_questions(self, blog_id: str) -> list[ResearchQuestion]:
        statement = select(ResearchQuestion).where(ResearchQuestion.blog_id == blog_id).order_by(ResearchQuestion.id)
        return list(self.session.exec(statement))

    def mark_research_complete(self, question_id: str, *, sufficient: bool) -> None:
        question = self.session.get(ResearchQuestion, question_id)
        if question is not None:
            question.status = "completed" if sufficient else "insufficient"
            self.session.add(question)
            self.session.commit()

    def add_source(self, blog_id: str, source_data: dict[str, Any]) -> Source:
        statement = select(Source).where(Source.blog_id == blog_id, Source.url == source_data["url"])
        source = self.session.exec(statement).first()
        if source is None:
            source = Source(blog_id=blog_id, **source_data)
            self.session.add(source)
            self.session.commit()
            self.session.refresh(source)
        return source

    def list_sources(self, blog_id: str) -> list[Source]:
        return list(self.session.exec(select(Source).where(Source.blog_id == blog_id).order_by(Source.retrieved_at)))

    def add_evidence(self, claim_id: str, source_id: str, supporting_text: str, confidence: float) -> Evidence:
        statement = select(Evidence).where(
            Evidence.claim_id == claim_id,
            Evidence.source_id == source_id,
            Evidence.supporting_text == supporting_text,
        )
        item = self.session.exec(statement).first()
        if item is None:
            item = Evidence(
                claim_id=claim_id,
                source_id=source_id,
                supporting_text=supporting_text,
                confidence=confidence,
            )
            self.session.add(item)
            self.session.commit()
            self.session.refresh(item)
        return item

    def list_evidence(self, blog_id: str) -> list[tuple[Evidence, Source]]:
        statement = (
            select(Evidence, Source)
            .join(Source, Source.id == Evidence.source_id)
            .join(Claim, Claim.id == Evidence.claim_id)
            .where(Claim.blog_id == blog_id)
        )
        return list(self.session.exec(statement))

    def save_draft(self, blog_id: str, content: str, provenance_map: dict[str, Any]) -> Draft:
        latest = self.get_latest_draft(blog_id)
        draft = Draft(
            blog_id=blog_id,
            content=content,
            version=1 if latest is None else latest.version + 1,
            provenance_map=provenance_map,
        )
        self.session.add(draft)
        self.session.commit()
        self.session.refresh(draft)
        return draft

    def get_draft(self, draft_id: str) -> Draft | None:
        return self.session.get(Draft, draft_id)

    def get_owned_draft(self, draft_id: str, user_id: str) -> Draft | None:
        statement = (
            select(Draft)
            .join(Blog, Blog.id == Draft.blog_id)
            .where(Draft.id == draft_id, Blog.user_id == user_id)
        )
        return self.session.exec(statement).first()

    def get_latest_draft(self, blog_id: str) -> Draft | None:
        statement = select(Draft).where(Draft.blog_id == blog_id).order_by(desc(Draft.version))
        return self.session.exec(statement).first()

    def save_qa_result(self, draft_id: str, payload: dict[str, Any]) -> QaResult:
        item = QaResult(draft_id=draft_id, **payload)
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item
