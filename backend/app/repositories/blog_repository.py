from datetime import UTC, datetime
from typing import Any

from sqlmodel import Session, desc, select

from app.models import Blog, BlogBrainSnapshot, Guardrail


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
