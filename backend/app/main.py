from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from app.api.blogs import router as blogs_router
from app.api.auth import router as auth_router
from app.api.drafts import router as drafts_router
from app.api.events import router as events_router
from app.api.fragments import router as fragments_router
from app.api.generation import router as generation_router
from app.core.config import settings
from app.core.database import create_db_and_tables, engine
from app.models import Blog, BlogBrainSnapshot, Guardrail
from app.repositories.blog_repository import BlogRepository

# `asynccontextmanager` turns this setup/teardown coroutine into FastAPI's application lifespan hook.
@asynccontextmanager
async def lifespan(_: FastAPI):
    # `_` intentionally discards the FastAPI app argument.
    create_db_and_tables()
    # The context manager closes the database session deterministically at the end of setup.
    with Session(engine) as session:
        existing = session.exec(select(Blog).where(Blog.id == "demo-blog")).first()
        if existing is None:
            blog = Blog(id="demo-blog", user_id=settings.default_user_id, title="My New Blog", status="draft")
            session.add(blog)
            session.add(Guardrail(blog_id="demo-blog"))
            session.add(
                BlogBrainSnapshot(
                    blog_id="demo-blog",
                    version=1,
                    payload={
                        "thesis": "",
                        "arguments": [],
                        "sentiment": {"primary": "curious", "secondary": None, "intensity": 0.5},
                        "intent": "exploration",
                        "open_questions": [],
                        "contradictions": 0,
                    },
                )
            )
            session.commit()
            repo = BlogRepository(session)
            repo.add_event("demo-blog", "blog.seeded", {"title": "My New Blog"})
    # FastAPI starts serving after this yield; code after it would run during shutdown.
    yield


# Passing `lifespan` registers startup/shutdown work instead of calling it directly.
app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
def healthcheck() -> dict[str, str]:
    # The decorator registers this ordinary function as an HTTP GET endpoint.
    return {"status": "ok"}


# Router modules own their endpoint declarations; registration attaches them to this application.
app.include_router(blogs_router)
app.include_router(auth_router)
app.include_router(fragments_router)
app.include_router(generation_router)
app.include_router(drafts_router)
app.include_router(events_router)
