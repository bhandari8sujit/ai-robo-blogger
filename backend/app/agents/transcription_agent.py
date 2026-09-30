from datetime import datetime, UTC
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any
from urllib.request import urlopen

from app.core.config import settings


class TranscriptionAgent:
    # A class attribute is shared by instances because the model name comes from global settings.
    model_name = settings.transcription_model

    def run(self, fragment_id: str, audio_url: str, transcript_hint: str | None = None) -> dict[str, Any]:
        if transcript_hint and transcript_hint.strip():
            transcript = transcript_hint.strip()
            return self._result(transcript, 0.95, "completed")

        if not settings.openai_api_key:
            return self._result("", 0.0, "pending_configuration", "OPENAI_API_KEY is not configured.")

        try:
            transcript = self._transcribe(audio_url)
        except Exception as error:
            return self._result("", 0.0, "transcription_failed", str(error))

        if not transcript:
            return self._result("", 0.0, "transcription_failed", "The provider returned an empty transcript.")

        return self._result(transcript, 0.0, "completed")

    def _transcribe(self, audio_url: str) -> str:
        # The OpenAI import remains lazy so local fallback mode does not require provider setup.
        from openai import OpenAI

        source = Path(audio_url)
        if source.is_file():
            with source.open("rb") as audio_file:
                response = self._client().audio.transcriptions.create(model=self.model_name, file=audio_file)
                return response.text.strip()

        with urlopen(audio_url, timeout=30) as response:
            audio_content = response.read()
        suffix = Path(audio_url).suffix or ".webm"
        # This context manager deletes the temporary download automatically when the block exits.
        with NamedTemporaryFile(suffix=suffix) as audio_file:
            audio_file.write(audio_content)
            audio_file.flush()
            audio_file.seek(0)
            response = self._client().audio.transcriptions.create(model=self.model_name, file=audio_file)
            return response.text.strip()

    @staticmethod
    def _client() -> Any:
        # The static factory centralizes provider configuration without depending on instance state.
        from openai import OpenAI

        return OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)

    def _result(
        self,
        transcript: str,
        confidence: float,
        status: str,
        reason: str | None = None,
    ) -> dict[str, Any]:
        # Build a stable response shape and append the optional failure field only when applicable.
        result = {
            "transcript": transcript,
            "transcript_confidence": confidence,
            "transcription_model": self.model_name,
            "transcribed_at": datetime.now(UTC).isoformat(),
            "status": status,
        }
        if reason:
            result["failure_reason"] = reason
        return result
