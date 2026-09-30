from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.blogs import router as blogs_router
from app.api.fragments import router as fragments_router
from app.core.config import settings
from app.core.database import create_db_and_tables

# `asynccontextmanager` turns this setup/teardown coroutine into FastAPI's application lifespan hook.
@asynccontextmanager
async def lifespan(_: FastAPI):
    # `_` intentionally discards the FastAPI app argument.
    create_db_and_tables()
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
app.include_router(auth_router)
app.include_router(blogs_router)
app.include_router(fragments_router)
