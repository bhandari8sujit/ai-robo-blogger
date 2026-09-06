from datetime import datetime, UTC
from typing import Any
from uuid import uuid4

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


# SQLModel combines Pydantic validation with SQLAlchemy table mapping when `table=True`.
class User(SQLModel, table=True):
    # `default_factory` creates a fresh UUID for every row rather than reusing one import-time value.
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    email: str | None = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Blog(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(index=True)
    title: str = Field(default="Untitled Blog")
    thesis: str | None = Field(default=None)
    status: str = Field(default="draft", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Fragment(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    blog_id: str = Field(index=True)
    audio_url: str
    transcript: str | None = Field(default=None)
    duration_seconds: float = Field(default=0)
    status: str = Field(default="uploaded", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class FragmentAnalysis(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    fragment_id: str = Field(index=True)
    summary: str
    # `sa_column=Column(JSON)` persists nested Python lists/dicts in a JSON database column.
    topics: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    claims: list[dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))
    questions: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    personal_experiences: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    sentiment: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    intent: str


class BlogBrainSnapshot(SQLModel, table=True):
    # Each update is saved as a versioned snapshot instead of overwriting the previous state.
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    blog_id: str = Field(index=True)
    version: int = Field(default=1)
    payload: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Claim(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    blog_id: str = Field(index=True)
    text: str
    source_required: bool = Field(default=True)
    research_status: str = Field(default="pending", index=True)
    confidence: float = Field(default=0.5)
    origin_type: str = Field(default="AI_INFERENCE")


class ResearchQuestion(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    blog_id: str = Field(index=True)
    question: str
    status: str = Field(default="pending", index=True)
    priority: str = Field(default="medium")


class Source(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    blog_id: str = Field(index=True)
    title: str
    url: str
    publisher: str | None = Field(default=None)
    published_at: str | None = Field(default=None)
    credibility: float = Field(default=0.6)
    retrieved_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Evidence(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    claim_id: str = Field(index=True)
    source_id: str = Field(index=True)
    supporting_text: str
    confidence: float = Field(default=0.6)


class Draft(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    blog_id: str = Field(index=True)
    content: str
    version: int = Field(default=1)
    provenance_map: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Guardrail(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    blog_id: str = Field(index=True)
    tone: str = Field(default="conversational")
    length: str = Field(default="1200-1800")
    preserve_voice: bool = Field(default=True)
    citation_required: bool = Field(default=True)
    banned_topics: list[str] = Field(default_factory=list, sa_column=Column(JSON))


class QaResult(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    draft_id: str = Field(index=True)
    passed: bool = Field(default=False)
    issues: list[dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))
    voice_score: float = Field(default=0)
    factuality_score: float = Field(default=0)
    publish_blocked: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ProcessingEvent(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    blog_id: str = Field(index=True)
    event_type: str = Field(index=True)
    payload: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    status: str = Field(default="ok")
    attempt: int = Field(default=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
