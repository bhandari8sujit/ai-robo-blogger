from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ApiBaseModel(BaseModel):
    # Pydantic accepts both Python snake_case names and declared camelCase aliases as input.
    model_config = ConfigDict(populate_by_name=True)


class BlogCreateRequest(ApiBaseModel):
    title: str = Field(default="Untitled Blog", min_length=1, max_length=200)


class UserCreateRequest(ApiBaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserResponse(ApiBaseModel):
    id: str
    email: EmailStr
    is_active: bool = Field(alias="isActive")
    created_at: datetime = Field(alias="createdAt")


class TokenResponse(ApiBaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"


class BlogResponse(ApiBaseModel):
    id: str
    title: str
    status: str
    thesis: str | None
    # Aliases keep Python's snake_case internally while returning camelCase JSON.
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class FragmentResponse(ApiBaseModel):
    id: str
    blog_id: str = Field(alias="blogId")
    created_at: datetime = Field(alias="createdAt")
    duration_seconds: float = Field(alias="durationSeconds")
    transcript: str | None = None
    status: str


class ClaimResponse(ApiBaseModel):
    id: str
    text: str
    requires_research: bool = Field(alias="requiresResearch")
    confidence: float
    origin_type: Literal["USER_SAID", "AI_INFERENCE", "RESEARCH_FACT", "AI_GENERATED"] = Field(alias="originType")
    research_status: Literal["pending", "completed", "insufficient"] = Field(alias="researchStatus")


class BlogBrainCard(ApiBaseModel):
    value: Any
    confidence: float
    origin_type: Literal["USER_SAID", "AI_INFERENCE", "RESEARCH_FACT", "AI_GENERATED"] = Field(alias="originType")
    updated_at: datetime = Field(alias="updatedAt")


class BlogStateResponse(ApiBaseModel):
    blog_id: str = Field(alias="blogId")
    title: str
    thesis: BlogBrainCard
    arguments: BlogBrainCard
    sentiment: BlogBrainCard
    intent: BlogBrainCard
    open_questions: BlogBrainCard = Field(alias="openQuestions")
    claims: list[ClaimResponse] = Field(default_factory=list)
    contradiction_count: int = Field(default=0, alias="contradictionCount")
    processing_status: str = Field(default="ready", alias="processingStatus")
