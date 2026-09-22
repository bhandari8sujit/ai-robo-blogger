from dataclasses import dataclass
import os
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
        raise RuntimeError(f"{name} must be set and contain at least {min_length} characters")
    return SecretStr(value)


# A frozen dataclass is an immutable, typed configuration object, similar to Object.freeze.
@dataclass(frozen=True)
class Settings:
    app_name: str = "Robo Blog Backend"
    app_version: str = "0.1.0"
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./robo_blog.db")
    audio_storage_dir: str = os.getenv("AUDIO_STORAGE_DIR", "./audio_store")
    default_user_id: str = os.getenv("DEFAULT_USER_ID", "demo-user")
    jwt_secret_key: SecretStr = _required_secret("JWT_SECRET_KEY", 32)
    openai_api_key: str | None = _optional_env("OPENAI_API_KEY")
    openai_base_url: str | None = _optional_env("OPENAI_BASE_URL")
    transcription_model: str = os.getenv("TRANSCRIPTION_MODEL", "gpt-4o-mini-transcribe")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    llm_strong_model: str = os.getenv("LLM_STRONG_MODEL", "gpt-4.1")
    tavily_api_key: str | None = _optional_env("TAVILY_API_KEY")
    r2_bucket: str | None = _optional_env("R2_BUCKET")
    r2_endpoint_url: str | None = _optional_env("R2_ENDPOINT_URL")
    r2_access_key_id: str | None = _optional_env("R2_ACCESS_KEY_ID")
    r2_secret_access_key: str | None = _optional_env("R2_SECRET_ACCESS_KEY")
    r2_region: str = os.getenv("R2_REGION", "auto")
    supabase_url: str | None = _optional_env("SUPABASE_URL")
    supabase_anon_key: str | None = _optional_env("SUPABASE_ANON_KEY")
    supabase_jwt_secret: str | None = _optional_env("SUPABASE_JWT_SECRET")
    # A tuple is immutable; the ellipsis means "zero or more strings" in a type annotation.
    cors_origins: tuple[str, ...] = tuple(
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
        if origin.strip()
    )


# A single module-level instance acts as the application's configuration singleton.
settings = Settings()
