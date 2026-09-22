from typing import Annotated

from fastapi import APIRouter, HTTPException, Path

from app.core.deps import CurrentUserId, DbSession
from app.schemas.api import DraftResponse
from app.services.orchestration_service import OrchestrationService

router = APIRouter(prefix="/blogs", tags=["generation"])


@router.post("/{blog_id}/draft/generate", response_model=DraftResponse)
def generate_draft(
    blog_id: Annotated[str, Path(min_length=1)], session: DbSession, _: CurrentUserId
) -> DraftResponse:
    # A synchronous endpoint is run by FastAPI in its worker thread pool.
    service = OrchestrationService(session)
    payload = service.generate_draft(blog_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="Blog not found")

    return DraftResponse(
        id=payload["id"],
        blogId=payload["blog_id"],
        version=payload["version"],
        content=payload["content"],
        wordCount=payload["word_count"],
        updatedAt=payload["updated_at"],
    )
