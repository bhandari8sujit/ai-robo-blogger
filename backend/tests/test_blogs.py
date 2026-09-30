from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.core.database import get_session
from app.main import app
from app.repositories.blog_repository import BlogRepository


def _test_engine():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    return engine


def test_blog_creation_seeds_state_and_public_reads() -> None:
    engine = _test_engine()

    def get_test_session() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_test_session
    try:
        with TestClient(app) as client:
            client.post("/auth/register", json={"email": "owner@example.com", "password": "secure-password"})
            login = client.post("/auth/token", data={"username": "owner@example.com", "password": "secure-password"})
            headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

            unauthenticated = client.post("/blogs", json={"title": "Private mutation"})
            assert unauthenticated.status_code == 401

            created = client.post("/blogs", json={"title": "Thinking aloud"}, headers=headers)
            assert created.status_code == 201
            assert created.json()["title"] == "Thinking aloud"
            assert "createdAt" in created.json()
            blog_id = created.json()["id"]

            public_blog = client.get(f"/blogs/{blog_id}")
            public_state = client.get(f"/blogs/{blog_id}/state")
            assert public_blog.status_code == 200
            assert public_state.status_code == 200
            assert public_state.json()["blogId"] == blog_id

        with Session(engine) as session:
            repo = BlogRepository(session)
            first = repo.get_latest_blog_brain(blog_id)
            assert first is not None and first.version == 1
            updated = repo.save_blog_brain(blog_id, {**first.payload, "thesis": "A clearer thesis"})
            assert updated.version == 2
            assert repo.get_guardrail(blog_id) is not None
    finally:
        app.dependency_overrides.clear()
