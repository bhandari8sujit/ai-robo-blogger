from datetime import datetime, UTC
from typing import Any
from uuid import uuid4

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


# SQLModel combines Pydantic validation with SQLAlchemy table mapping when `table=True`.
class User(SQLModel, table=True):
    __tablename__ = "users"

    # `default_factory` creates a fresh UUID for every row rather than reusing one import-time value.
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Blog(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(index=True)
    title: str = Field(default="Untitled Blog")
    thesis: str | None = Field(default=None)
    status: str = Field(default="draft", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class BlogBrainSnapshot(SQLModel, table=True):
    # Snapshots are append-only, so earlier interpretations remain available for auditing.
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    blog_id: str = Field(index=True)
    version: int = Field(default=1)
    payload: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Guardrail(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    blog_id: str = Field(index=True)
    tone: str = Field(default="conversational")
    length: str = Field(default="1200-1800")
    preserve_voice: bool = Field(default=True)
    citation_required: bool = Field(default=True)
    # `default_factory` gives every row its own list instead of sharing a mutable default.
    banned_topics: list[str] = Field(default_factory=list, sa_column=Column(JSON))
