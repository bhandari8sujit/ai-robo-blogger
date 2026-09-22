from typing import Annotated

from fastapi import APIRouter, HTTPException, Path

from app.core.deps import CurrentUserId, DbSession
from app.repositories.blog_repository import BlogRepository
from app.services.orchestration_service import OrchestrationService

router = APIRouter(prefix="/fragments", tags=["fragments"])


@router.post("/{fragment_id}/process")
async def process_fragment(
    fragment_id: Annotated[str, Path(min_length=1)], session: DbSession, _: CurrentUserId
) -> dict[str, str]:
    # `async def` allows this endpoint to await the processing service before responding.
    repo = BlogRepository(session)
    fragment = repo.get_fragment(fragment_id)
    if fragment is None:
        raise HTTPException(status_code=404, detail="Fragment not found")

    service = OrchestrationService(session)
    await service.process_fragment(fragment_id)
    return {"status": "queued"}
