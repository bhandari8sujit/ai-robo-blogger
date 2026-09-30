from typing import Annotated

from fastapi import APIRouter, HTTPException, Path

from app.core.deps import CurrentUserId, DbSession
from app.repositories.blog_repository import BlogRepository
from app.schemas.api import DraftResponse, DraftRevisionRequest, QaResultResponse, SentenceWhyResponse, SourceResponse
from app.services.orchestration_service import OrchestrationService

router = APIRouter(prefix="/drafts", tags=["drafts"])


def _require_owned_draft(repo: BlogRepository, draft_id: str, user_id: str) -> None:
    if repo.get_owned_draft(draft_id, user_id) is None:
        # A 404 avoids revealing whether another user's draft ID exists.
        raise HTTPException(status_code=404, detail="Draft not found")


@router.post("/{draft_id}/validate", response_model=QaResultResponse)
def validate_draft(
    draft_id: Annotated[str, Path(min_length=1)], session: DbSession, user_id: CurrentUserId
) -> QaResultResponse:
    _require_owned_draft(BlogRepository(session), draft_id, user_id)
    result = OrchestrationService(session).validate_draft(draft_id)
    return QaResultResponse(**result)


@router.post("/{draft_id}/revise", response_model=DraftResponse)
def revise_draft(
    draft_id: Annotated[str, Path(min_length=1)],
    payload: DraftRevisionRequest,
    session: DbSession,
    user_id: CurrentUserId,
) -> DraftResponse:
    _require_owned_draft(BlogRepository(session), draft_id, user_id)
    result = OrchestrationService(session).revise_draft(draft_id, payload.revision_prompt)
    return DraftResponse(**result)


@router.get("/{draft_id}/sources", response_model=list[SourceResponse])
def get_sources(draft_id: Annotated[str, Path(min_length=1)], session: DbSession) -> list[SourceResponse]:
    repo = BlogRepository(session)
    draft = repo.get_draft(draft_id)
    if draft is None:
        raise HTTPException(status_code=404, detail="Draft not found")
    return [SourceResponse.model_validate(source, from_attributes=True) for source in repo.list_sources(draft.blog_id)]


@router.get("/{draft_id}/sentences/{sentence_id}/why", response_model=SentenceWhyResponse)
def sentence_why(
    draft_id: Annotated[str, Path(min_length=1)],
    sentence_id: Annotated[str, Path(min_length=1)],
    session: DbSession,
) -> SentenceWhyResponse:
    result = OrchestrationService(session).sentence_why(draft_id, sentence_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Draft not found")
    return SentenceWhyResponse(**result)
