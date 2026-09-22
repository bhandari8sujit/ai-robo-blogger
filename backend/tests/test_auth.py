from collections.abc import Generator
import os

os.environ.setdefault("JWT_SECRET_KEY", "test-only-signing-key-that-is-at-least-32-chars")

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.core.database import get_session
from app.main import app


def test_register_login_and_current_user() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def get_test_session() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_test_session
    try:
        with TestClient(app) as client:
            registration = client.post(
                "/auth/register",
                json={"email": "writer@example.com", "password": "correct-horse-battery-staple"},
            )
            assert registration.status_code == 201
            assert registration.json()["email"] == "writer@example.com"
            assert "hashed_password" not in registration.json()

            login = client.post(
                "/auth/token",
                data={"username": "writer@example.com", "password": "correct-horse-battery-staple"},
            )
            assert login.status_code == 200
            token = login.json()["access_token"]

            current_user = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
            assert current_user.status_code == 200
            assert current_user.json()["email"] == "writer@example.com"

            invalid = client.get("/auth/me", headers={"Authorization": "Bearer invalid"})
            assert invalid.status_code == 401
    finally:
        app.dependency_overrides.clear()