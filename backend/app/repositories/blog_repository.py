from datetime import UTC, datetime
from typing import Any

from sqlmodel import Session, desc, select

from app.models import Blog, BlogBrainSnapshot, Claim, Fragment, FragmentAnalysis, Guardrail


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
