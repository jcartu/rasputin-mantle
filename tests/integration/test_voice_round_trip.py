from __future__ import annotations

import base64

import httpx
import pytest
import voice.stt as stt_module
import voice.tts as tts_module
from voice import synthesize, transcribe


class HandlerTransport(httpx.AsyncBaseTransport):
    def __init__(self, handler):
        self._handler = handler

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        response = self._handler(request)
        response.request = request
        return response


@pytest.mark.asyncio
async def test_voice_round_trip_with_mock_services(monkeypatch: pytest.MonkeyPatch) -> None:
    wav_bytes = b"RIFFmock-wave"

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/transcribe":
            assert request.method == "POST"
            return httpx.Response(200, json={"text": "hello mantle"})
        if request.url.path == "/synthesize":
            assert request.method == "POST"
            return httpx.Response(200, json={"audio": base64.b64encode(wav_bytes).decode()})
        return httpx.Response(404, json={"error": "not_found"})

    transport = HandlerTransport(handler)
    monkeypatch.setattr(stt_module, "_TRANSPORT", transport)
    monkeypatch.setattr(tts_module, "_TRANSPORT", transport)
    monkeypatch.setenv("WHISPER_URL", "http://mock-whisper")
    monkeypatch.setenv("KOKORO_URL", "http://mock-kokoro")

    transcript = await transcribe(b"RIFFinput-wave")
    audio = await synthesize(transcript, voice="default")

    assert transcript == "hello mantle"
    assert audio == wav_bytes
