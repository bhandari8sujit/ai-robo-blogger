from typing import Annotated

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


# The decorator registers request parsing and response validation from the annotated types.
@router.post("", response_model=BlogResponse)
def create_blog(payload: BlogCreateRequest, session: DbSession, user_id: CurrentUserId) -> BlogResponse:
    repo = BlogRepository(session)
    blog = repo.create_blog(user_id=user_id, title=payload.title)
    return BlogResponse(
        id=blog.id,
        title=blog.title,
        status=blog.status,
        thesis=blog.thesis,
        createdAt=blog.created_at,
        updatedAt=blog.updated_at,
    )


@router.get("/{blog_id}", response_model=BlogResponse)
def get_blog(blog_id: Annotated[str, Path(min_length=1)], session: DbSession) -> BlogResponse:
    # `Annotated[..., Path(...)]` supplies runtime validation for a URL path segment.
    repo = BlogRepository(session)
    blog = repo.get_blog(blog_id)
    if blog is None:
        raise HTTPException(status_code=404, detail="Blog not found")

    return BlogResponse(
        id=blog.id,
        title=blog.title,
        status=blog.status,
        thesis=blog.thesis,
        createdAt=blog.created_at,
        updatedAt=blog.updated_at,
    )


@router.post("/{blog_id}/fragments", response_model=FragmentResponse)
async def upload_fragment(
    blog_id: Annotated[str, Path(min_length=1)],
    session: DbSession,
    _: CurrentUserId,
    audio: Annotated[UploadFile, File()],
) -> FragmentResponse:
    repo = BlogRepository(session)
    blog = repo.get_blog(blog_id)
    if blog is None:
        raise HTTPException(status_code=404, detail="Blog not found")

    # UploadFile I/O is awaitable so the event loop can serve other requests while reading.
    blob = await audio.read()
    if not blob:
        raise HTTPException(status_code=400, detail="Empty audio payload")

    storage = StorageService()
    suffix = ".webm"
    if audio.filename and "." in audio.filename:
        suffix = "." + audio.filename.rsplit(".", 1)[1]

    audio_url, duration = storage.save_audio(blog_id=blog_id, content=blob, suffix=suffix)
    fragment = repo.create_fragment(blog_id=blog_id, audio_url=audio_url, duration_seconds=duration)
    repo.add_event(blog_id, "fragment.uploaded", {"fragment_id": fragment.id})

    orchestrator = OrchestrationService(session)
    await orchestrator.process_fragment(fragment.id)

    return FragmentResponse(
        id=fragment.id,
        blogId=fragment.blog_id,
        createdAt=fragment.created_at,
        durationSeconds=fragment.duration_seconds,
        transcript=fragment.transcript,
        status=fragment.status,
    )


@router.get("/{blog_id}/fragments", response_model=list[FragmentResponse])
def list_fragments(blog_id: Annotated[str, Path(min_length=1)], session: DbSession) -> list[FragmentResponse]:
    repo = BlogRepository(session)
    fragments = repo.list_fragments(blog_id)
    # A list comprehension maps persisted SQLModel rows into the public Pydantic response model.
    return [
        FragmentResponse(
            id=fragment.id,
            blogId=fragment.blog_id,
            createdAt=fragment.created_at,
            durationSeconds=fragment.duration_seconds,
            transcript=fragment.transcript,
            status=fragment.status,
        )
        for fragment in fragments
    ]


@router.get("/{blog_id}/state", response_model=BlogStateResponse)
def get_blog_state(blog_id: Annotated[str, Path(min_length=1)], session: DbSession) -> BlogStateResponse:
    service = OrchestrationService(session)
    state = service.blog_state(blog_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Blog not found")

    return BlogStateResponse(**state)


@router.get("/{blog_id}/timeline", response_model=list[TimelineItem])
def get_timeline(blog_id: Annotated[str, Path(min_length=1)], session: DbSession) -> list[TimelineItem]:
    repo = BlogRepository(session)
    events = repo.timeline(blog_id)
    return [
        TimelineItem(
            id=event.id,
            eventType=event.event_type,
            payload=event.payload,
            status=event.status,
            attempt=event.attempt,
            createdAt=event.created_at,
        )
        for event in events
    ]


@router.get("/{blog_id}/research", response_model=list[ResearchQuestionResponse])
def get_research_questions(
    blog_id: Annotated[str, Path(min_length=1)],
    session: DbSession,
) -> list[ResearchQuestionResponse]:
    repo = BlogRepository(session)
    questions = repo.list_research_questions(blog_id)
    source_count = len(repo.list_sources(blog_id))
    return [
        ResearchQuestionResponse(
            id=question.id,
            question=question.question,
            status=question.status,
            priority=question.priority,
            sourceCount=source_count,
        )
        for question in questions
    ]


@router.post("/{blog_id}/research/run")
async def run_research(
    blog_id: Annotated[str, Path(min_length=1)], session: DbSession, _: CurrentUserId
) -> dict[str, int]:
    service = OrchestrationService(session)
    completed = await service.run_research(blog_id)
    return {"completed": completed}
