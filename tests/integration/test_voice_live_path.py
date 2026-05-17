from __future__ import annotations

import os

import httpx
import pytest

from fastapi.testclient import TestClient

from gateway.app import app


def _whisper_available() -> bool:
    whisper_url = os.environ.get("WHISPER_URL", "http://127.0.0.1:8803")
    try:
        r = httpx.get(f"{whisper_url}/health", timeout=3.0)
        return r.status_code == 200
    except httpx.RequestError:
        return False


def _kokoro_available() -> bool:
    kokoro_url = os.environ.get("KOKORO_URL", "http://127.0.0.1:8804")
    try:
        r = httpx.get(f"{kokoro_url}/health", timeout=3.0)
        return r.status_code == 200
    except httpx.RequestError:
        return False


@pytest.mark.asyncio
@pytest.mark.skipif(not _whisper_available(), reason="Faster-Whisper service not running")
async def test_voice_transcribe_when_available() -> None:
    """Live-path test: POST /api/voice/transcribe against running Faster-Whisper."""
    client = TestClient(app)
    # Minimal WAV header (16-bit mono 16kHz, 1 second of silence)
    import struct
    samples = b"\x00" * (16000 * 2)
    wav = (
        b"RIFF"
        + struct.pack("<I", 36 + len(samples))
        + b"WAVEfmt "
        + struct.pack("<IHHIIHH", 16, 1, 1, 16000, 32000, 2, 16)
        + b"data"
        + struct.pack("<I", len(samples))
        + samples
    )
    resp = client.post(
        "/api/voice/transcribe",
        files={"file": ("test.wav", wav, "audio/wav")},
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert any(k in body for k in ("text", "transcript", "transcription"))


@pytest.mark.asyncio
@pytest.mark.skipif(not _kokoro_available(), reason="Kokoro TTS service not running")
async def test_voice_synthesize_when_available() -> None:
    """Live-path test: POST /api/voice/synthesize against running Kokoro."""
    client = TestClient(app)
    resp = client.post(
        "/api/voice/synthesize",
        json={"text": "Hello Mantle", "model": "kokoro-82M", "voice": "af_heart"},
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.headers.get("content-type", "").startswith("audio/")
    assert len(resp.content) > 0, "Synthesized audio should not be empty"


@pytest.mark.asyncio
@pytest.mark.skipif(not _whisper_available(), reason="Faster-Whisper service not running")
@pytest.mark.skipif(not _kokoro_available(), reason="Kokoro TTS service not running")
async def test_voice_round_trip_live() -> None:
    """Live-path round-trip: transcribe known audio, synthesize result, verify both succeed."""
    client = TestClient(app)

    # Transcribe
    import struct
    samples = b"\x00" * (16000 * 2)
    wav = (
        b"RIFF"
        + struct.pack("<I", 36 + len(samples))
        + b"WAVEfmt "
        + struct.pack("<IHHIIHH", 16, 1, 1, 16000, 32000, 2, 16)
        + b"data"
        + struct.pack("<I", len(samples))
        + samples
    )
    transcribe_resp = client.post(
        "/api/voice/transcribe",
        files={"file": ("test.wav", wav, "audio/wav")},
    )
    assert transcribe_resp.status_code == 200

    # Synthesize something
    synthesize_resp = client.post(
        "/api/voice/synthesize",
        json={"text": "Round trip test", "model": "kokoro-82M", "voice": "af_heart"},
    )
    assert synthesize_resp.status_code == 200
    assert len(synthesize_resp.content) > 0
