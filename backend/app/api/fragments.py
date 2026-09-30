from typing import Annotated

from fastapi import APIRouter, HTTPException, Path

from app.core.deps import CurrentUserId, DbSession
from app.repositories.blog_repository import BlogRepository
from app.services.orchestration_service import OrchestrationService

router = APIRouter(prefix="/fragments", tags=["fragments"])


@router.post("/{fragment_id}/process")
async def process_fragment(
    fragment_id: Annotated[str, Path(min_length=1)],
    session: DbSession,
    user_id: CurrentUserId,
) -> dict[str, str]:
    repo = BlogRepository(session)
    # Resolve through the parent blog so one user cannot process another user's fragment.
    fragment = repo.get_owned_fragment(fragment_id, user_id)
    if fragment is None:
        raise HTTPException(status_code=404, detail="Fragment not found")

    status = await OrchestrationService(session).process_fragment(fragment.id)
    return {"status": status or "not_found"}
