from __future__ import annotations

import os
from typing import Any

import httpx

DEFAULT_WHISPER_URL = "http://127.0.0.1:8803"
DEFAULT_TIMEOUT = httpx.Timeout(timeout=60.0, connect=3.0, read=60.0, write=10.0, pool=3.0)

_TRANSPORT: httpx.AsyncBaseTransport | None = None


class STTUnavailable(RuntimeError):
    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


async def transcribe(audio_bytes: bytes) -> str:
    if not audio_bytes:
        raise ValueError("audio_bytes must not be empty")

    base_url = os.environ.get("WHISPER_URL", DEFAULT_WHISPER_URL).rstrip("/")
    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT, transport=_TRANSPORT) as client:
            response = await client.post(
                f"{base_url}/transcribe",
                files={"file": ("audio.wav", audio_bytes, "audio/wav")},
            )
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise STTUnavailable(
            f"Faster-Whisper request failed with HTTP {exc.response.status_code}: {exc.response.text[:300]}",
            status_code=exc.response.status_code,
        ) from exc
    except httpx.RequestError as exc:
        raise STTUnavailable(f"Faster-Whisper service unavailable at {base_url}: {exc}") from exc

    return _extract_text(response)


def _extract_text(response: httpx.Response) -> str:
    content_type = response.headers.get("content-type", "")
    if "application/json" not in content_type.lower():
        text = response.text.strip()
        if text:
            return text
        raise STTUnavailable("Faster-Whisper response was empty")

    data: Any = response.json()
    if isinstance(data, dict):
        for key in ("text", "transcript", "transcription"):
            value = data.get(key)
            if isinstance(value, str) and value.strip():
                return value
        segments = data.get("segments")
        if isinstance(segments, list):
            parts = [str(item.get("text", "")) for item in segments if isinstance(item, dict)]
            joined = "".join(parts).strip()
            if joined:
                return joined
    raise STTUnavailable("Faster-Whisper response did not contain transcript text")
