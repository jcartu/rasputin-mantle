from __future__ import annotations

import base64
import os
from typing import Any

import httpx

DEFAULT_KOKORO_URL = "http://127.0.0.1:8804"
DEFAULT_TIMEOUT = httpx.Timeout(timeout=60.0, connect=3.0, read=60.0, write=10.0, pool=3.0)

_TRANSPORT: httpx.AsyncBaseTransport | None = None


class TTSUnavailable(RuntimeError):
    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


async def synthesize(text: str, voice: str = "default") -> bytes:
    if not text.strip():
        raise ValueError("text must not be empty")

    base_url = os.environ.get("KOKORO_URL", DEFAULT_KOKORO_URL).rstrip("/")
    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT, transport=_TRANSPORT) as client:
            response = await client.post(f"{base_url}/synthesize", json={"text": text, "voice": voice})
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise TTSUnavailable(
            f"Kokoro request failed with HTTP {exc.response.status_code}: {exc.response.text[:300]}",
            status_code=exc.response.status_code,
        ) from exc
    except httpx.RequestError as exc:
        raise TTSUnavailable(f"Kokoro service unavailable at {base_url}: {exc}") from exc

    return _extract_audio(response)


def _extract_audio(response: httpx.Response) -> bytes:
    content_type = response.headers.get("content-type", "").lower()
    if "application/json" not in content_type:
        if response.content:
            return response.content
        raise TTSUnavailable("Kokoro response was empty")

    data: Any = response.json()
    if isinstance(data, dict):
        for key in ("audio", "wav", "audio_base64"):
            value = data.get(key)
            if isinstance(value, str) and value:
                try:
                    return base64.b64decode(value)
                except ValueError as exc:
                    raise TTSUnavailable("Kokoro response included invalid base64 audio") from exc
    raise TTSUnavailable("Kokoro response did not contain audio bytes")
