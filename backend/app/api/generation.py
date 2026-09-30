from typing import Annotated

from fastapi import APIRouter, HTTPException, Path

from app.core.deps import CurrentUserId, DbSession
from app.repositories.blog_repository import BlogRepository
from app.schemas.api import DraftResponse
from app.services.orchestration_service import OrchestrationService

router = APIRouter(prefix="/blogs", tags=["generation"])


@router.post("/{blog_id}/draft/generate", response_model=DraftResponse)
def generate_draft(
    blog_id: Annotated[str, Path(min_length=1)], session: DbSession, user_id: CurrentUserId
) -> DraftResponse:
    if BlogRepository(session).get_owned_blog(blog_id, user_id) is None:
        raise HTTPException(status_code=404, detail="Blog not found")
    result = OrchestrationService(session).generate_draft(blog_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Blog state not found")
    return DraftResponse(**result)
