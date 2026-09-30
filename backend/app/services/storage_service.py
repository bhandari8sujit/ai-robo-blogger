from pathlib import Path
from uuid import uuid4

from app.core.config import settings


class StorageService:
    def __init__(self) -> None:
    # Path normalizes filesystem joining across operating systems.
        self.base_dir = Path(settings.audio_storage_dir)
        # `parents=True` creates missing ancestors; `exist_ok=True` makes repeated setup harmless.
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_audio(self, blog_id: str, content: bytes, suffix: str = ".webm") -> tuple[str, float]:
        # `/` is overloaded by pathlib for path joining, not numeric division.
        blog_dir = self.base_dir / blog_id
        blog_dir.mkdir(parents=True, exist_ok=True)

        file_name = f"{uuid4()}{suffix}"
        target = blog_dir / file_name
        target.write_bytes(content)

        duration_seconds = round(len(content) / 16000, 2)
        return str(target), duration_seconds
