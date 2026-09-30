import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from pydantic import SecretStr

# Runs at module import time so configuration is available before FastAPI creates the app.
load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def _optional_env(name: str) -> str | None:
    # `str | None` is Python's union type; callers must handle a missing value.
    value = os.getenv(name)
    if not value or value.startswith("replace-with-"):
        return None
    return value


def _required_secret(name: str, min_length: int) -> SecretStr:
    value = os.getenv(name, "")
    if len(value) < min_length:
        raise RuntimeError(
            f"{name} must be set and contain at least {min_length} characters"
        )
    return SecretStr(value)


# A frozen dataclass is an immutable, typed configuration object, similar to Object.freeze.
@dataclass(frozen=True)
class Settings:
    app_name: str = "Robo Blog Backend"
    app_version: str = "0.1.0"
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://robo_blog:robo_blog_password@localhost:5432/robo_blog",
    )
    jwt_secret_key: SecretStr = _required_secret("JWT_SECRET_KEY", 32)
    # A tuple is immutable; the ellipsis means "zero or more strings" in a type annotation.
    cors_origins: tuple[str, ...] = tuple(
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
        ).split(",")
        if origin.strip()
    )


# A single module-level instance acts as the application's configuration singleton.
settings = Settings()
