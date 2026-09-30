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


class ResearchQuestionResponse(ApiBaseModel):
    id: str
    question: str
    status: Literal["pending", "completed", "insufficient"]
    priority: Literal["low", "medium", "high"]
    source_count: int = Field(alias="sourceCount")


class SourceResponse(ApiBaseModel):
    id: str
    title: str
    url: str
    publisher: str | None = None
    published_at: str | None = Field(default=None, alias="publishedAt")
    credibility: float


class DraftResponse(ApiBaseModel):
    id: str
    blog_id: str = Field(alias="blogId")
    version: int
    content: str
    word_count: int = Field(alias="wordCount")
    updated_at: datetime = Field(alias="updatedAt")


class DraftRevisionRequest(ApiBaseModel):
    revision_prompt: str = Field(alias="revisionPrompt", min_length=1, max_length=2_000)


class SentenceWhyResponse(ApiBaseModel):
    sentence_id: str = Field(alias="sentenceId")
    sentence_text: str = Field(alias="sentenceText")
    user_basis: list[str] = Field(alias="userBasis")
    ai_interpretation: str = Field(alias="aiInterpretation")
    source_evidence: list[dict[str, str]] = Field(alias="sourceEvidence")
    confidence: float


class QaIssue(ApiBaseModel):
    type: str
    text: str
    severity: Literal["low", "medium", "high"]


class QaResultResponse(ApiBaseModel):
    passed: bool
    issues: list[QaIssue]
    voice_score: float = Field(alias="voiceScore")
    factuality_score: float = Field(alias="factualityScore")
    publish_blocked: bool = Field(alias="publishBlocked")
