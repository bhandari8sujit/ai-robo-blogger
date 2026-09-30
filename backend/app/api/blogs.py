from datetime import UTC, datetime
from typing import Annotated, Any

from fastapi import APIRouter, File, HTTPException, Path, UploadFile

from app.core.deps import CurrentUserId, DbSession
from app.repositories.blog_repository import BlogRepository
from app.schemas.api import (
    BlogCreateRequest,
    BlogResponse,
    BlogStateResponse,
    FragmentResponse,
    ResearchQuestionResponse,
    TimelineItem,
)
from app.services.orchestration_service import OrchestrationService
from app.services.storage_service import StorageService

router = APIRouter(prefix="/blogs", tags=["blogs"])


def _blog_response(blog: Any) -> BlogResponse:
    return BlogResponse(
        id=blog.id,
        title=blog.title,
        status=blog.status,
        thesis=blog.thesis,
        createdAt=blog.created_at,
        updatedAt=blog.updated_at,
    )


@router.post("", response_model=BlogResponse, status_code=201)
def create_blog(payload: BlogCreateRequest, session: DbSession, user_id: CurrentUserId) -> BlogResponse:
    return _blog_response(BlogRepository(session).create_blog(user_id=user_id, title=payload.title))


@router.get("/{blog_id}", response_model=BlogResponse)
def get_blog(blog_id: Annotated[str, Path(min_length=1)], session: DbSession) -> BlogResponse:
    # Annotated adds URL validation metadata while the runtime value remains a string.
    blog = BlogRepository(session).get_blog(blog_id)
    if blog is None:
        raise HTTPException(status_code=404, detail="Blog not found")
    return _blog_response(blog)


@router.post("/{blog_id}/fragments", response_model=FragmentResponse)
async def upload_fragment(
    blog_id: Annotated[str, Path(min_length=1)],
    session: DbSession,
    user_id: CurrentUserId,
    audio: Annotated[UploadFile, File()],
) -> FragmentResponse:
    repo = BlogRepository(session)
    if repo.get_owned_blog(blog_id, user_id) is None:
        raise HTTPException(status_code=404, detail="Blog not found")

    # Awaiting the upload read lets FastAPI serve other requests while bytes arrive.
    content = await audio.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty audio payload")
    suffix = "." + audio.filename.rsplit(".", 1)[1] if audio.filename and "." in audio.filename else ".webm"
    audio_url, duration = StorageService().save_audio(blog_id, content, suffix)
    fragment = repo.create_fragment(blog_id, audio_url, duration)
    await OrchestrationService(session).process_fragment(fragment.id)
    session.refresh(fragment)
    return FragmentResponse.model_validate(fragment, from_attributes=True)


@router.get("/{blog_id}/fragments", response_model=list[FragmentResponse])
def list_fragments(blog_id: Annotated[str, Path(min_length=1)], session: DbSession) -> list[FragmentResponse]:
    if BlogRepository(session).get_blog(blog_id) is None:
        raise HTTPException(status_code=404, detail="Blog not found")
    return [FragmentResponse.model_validate(item, from_attributes=True) for item in BlogRepository(session).list_fragments(blog_id)]


@router.get("/{blog_id}/state", response_model=BlogStateResponse)
def get_blog_state(blog_id: Annotated[str, Path(min_length=1)], session: DbSession) -> BlogStateResponse:
    repo = BlogRepository(session)
    blog = repo.get_blog(blog_id)
    brain = repo.get_latest_blog_brain(blog_id)
    if blog is None or brain is None:
        raise HTTPException(status_code=404, detail="Blog not found")

    now = datetime.now(UTC)

    def card(value: Any) -> dict[str, Any]:
        return {"value": value, "confidence": 0.8, "originType": "AI_INFERENCE", "updatedAt": now}

    claims = repo.list_claims(blog_id)
    fragments = repo.list_fragments(blog_id)
    return BlogStateResponse(
        blogId=blog.id,
        title=blog.title,
        thesis=card(brain.payload.get("thesis", "")),
        arguments=card(brain.payload.get("arguments", [])),
        sentiment=card(brain.payload.get("sentiment", {})),
        intent=card(brain.payload.get("intent", "exploration")),
        openQuestions=card(brain.payload.get("open_questions", [])),
        claims=[
            {
                "id": claim.id,
                "text": claim.text,
                "requiresResearch": claim.source_required,
                "confidence": claim.confidence,
                "originType": claim.origin_type,
                "researchStatus": claim.research_status,
            }
            for claim in claims
        ],
        contradictionCount=brain.payload.get("contradictions", 0),
        processingStatus=fragments[-1].status if fragments else "ready",
    )


@router.get("/{blog_id}/research", response_model=list[ResearchQuestionResponse])
def get_research_questions(
    blog_id: Annotated[str, Path(min_length=1)], session: DbSession
) -> list[ResearchQuestionResponse]:
    repo = BlogRepository(session)
    if repo.get_blog(blog_id) is None:
        raise HTTPException(status_code=404, detail="Blog not found")
    source_count = len(repo.list_sources(blog_id))
    return [
        ResearchQuestionResponse(
            id=item.id,
            question=item.question,
            status=item.status,
            priority=item.priority,
            sourceCount=source_count,
        )
        for item in repo.list_research_questions(blog_id)
    ]


@router.post("/{blog_id}/research/run")
def run_research(
    blog_id: Annotated[str, Path(min_length=1)], session: DbSession, user_id: CurrentUserId
) -> dict[str, int]:
    repo = BlogRepository(session)
    if repo.get_owned_blog(blog_id, user_id) is None:
        raise HTTPException(status_code=404, detail="Blog not found")
    return {"completed": OrchestrationService(session).run_research(blog_id, deep=True)}


@router.get("/{blog_id}/timeline", response_model=list[TimelineItem])
def get_timeline(blog_id: Annotated[str, Path(min_length=1)], session: DbSession) -> list[TimelineItem]:
    repo = BlogRepository(session)
    if repo.get_blog(blog_id) is None:
        raise HTTPException(status_code=404, detail="Blog not found")
    return [TimelineItem.model_validate(event, from_attributes=True) for event in repo.timeline(blog_id)]
