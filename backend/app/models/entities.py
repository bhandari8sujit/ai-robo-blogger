from datetime import datetime, UTC
from uuid import uuid4

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
