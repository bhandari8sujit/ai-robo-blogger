from typing import Annotated

from fastapi import APIRouter, HTTPException, Path

from app.core.deps import DbSession
from app.repositories.blog_repository import BlogRepository
from app.schemas.api import DraftResponse, DraftRevisionRequest, QaResultResponse, SentenceWhyResponse, SourceResponse
from app.services.orchestration_service import OrchestrationService

router = APIRouter(prefix="/drafts", tags=["drafts"])


# FastAPI validates and serializes the returned value against `response_model`.
@router.post("/{draft_id}/validate", response_model=QaResultResponse)
def validate_draft(draft_id: Annotated[str, Path(min_length=1)], session: DbSession) -> QaResultResponse:
    service = OrchestrationService(session)
    payload = service.validate_draft(draft_id)
    if payload is None:
        # Raising HTTPException is FastAPI's structured early-return mechanism.
        raise HTTPException(status_code=404, detail="Draft not found")
    return QaResultResponse(
        passed=payload["passed"],
        issues=payload["issues"],
        voiceScore=payload["voice_score"],
        factualityScore=payload["factuality_score"],
        publishBlocked=payload["publish_blocked"],
    )


@router.post("/{draft_id}/revise", response_model=DraftResponse)
def revise_draft(
    draft_id: Annotated[str, Path(min_length=1)],
    payload: DraftRevisionRequest,
    session: DbSession,
) -> DraftResponse:
    service = OrchestrationService(session)
    revised = service.revise_draft(draft_id, payload.revision_prompt)
    if revised is None:
        raise HTTPException(status_code=404, detail="Draft not found")

    return DraftResponse(
        id=revised["id"],
        blogId=revised["blog_id"],
        version=revised["version"],
        content=revised["content"],
        wordCount=revised["word_count"],
        updatedAt=revised["updated_at"],
    )


@router.get("/{draft_id}/sources", response_model=list[SourceResponse])
def get_sources(draft_id: Annotated[str, Path(min_length=1)], session: DbSession) -> list[SourceResponse]:
    repo = BlogRepository(session)
    draft = repo.get_draft(draft_id)
    if draft is None:
        raise HTTPException(status_code=404, detail="Draft not found")

    sources = repo.list_sources(draft.blog_id)
    return [
        SourceResponse(
            id=source.id,
            title=source.title,
            url=source.url,
            publisher=source.publisher,
            publishedAt=source.published_at,
            credibility=source.credibility,
        )
        for source in sources
    ]


@router.get("/{draft_id}/sentences/{sentence_id}/why", response_model=SentenceWhyResponse)
def sentence_why(
    draft_id: Annotated[str, Path(min_length=1)],
    sentence_id: Annotated[str, Path(min_length=1)],
    session: DbSession,
) -> SentenceWhyResponse:
    service = OrchestrationService(session)
    why = service.sentence_why(draft_id, sentence_id)
    if why is None:
        raise HTTPException(status_code=404, detail="Draft not found")

    return SentenceWhyResponse(**why)
