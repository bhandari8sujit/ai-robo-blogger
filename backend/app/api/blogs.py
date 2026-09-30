from datetime import UTC, datetime
from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Path

from app.core.deps import CurrentUserId, DbSession
from app.repositories.blog_repository import BlogRepository
from app.schemas.api import BlogCreateRequest, BlogResponse, BlogStateResponse

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

    return BlogStateResponse(
        blogId=blog.id,
        title=blog.title,
        thesis=card(brain.payload.get("thesis", "")),
        arguments=card(brain.payload.get("arguments", [])),
        sentiment=card(brain.payload.get("sentiment", {})),
        intent=card(brain.payload.get("intent", "exploration")),
        openQuestions=card(brain.payload.get("open_questions", [])),
    )
