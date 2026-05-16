from __future__ import annotations

import httpx

from fastapi import APIRouter, HTTPException, UploadFile
from pydantic import BaseModel

router = APIRouter()


class TranscribeRequest(BaseModel):
    model: str = 'faster-whisper-large-v3'
    language: str = 'en'


class SynthesizeRequest(BaseModel):
    text: str
    model: str = 'kokoro-82M'
    voice: str = 'af_heart'


@router.post('/transcribe')
async def transcribe(file: UploadFile, model: str = 'faster-whisper-large-v3', language: str = 'en') -> dict:
    # Proxy to local STT service
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            resp = await client.post(
                'http://127.0.0.1:8803/transcribe',
                files={'file': (file.filename or 'audio.wav', await file.read(), file.content_type)},
                data={'model': model, 'language': language},
            )
            if resp.status_code != 200:
                raise HTTPException(status_code=502, detail={'error': 'stt_failed', 'message': resp.text})
            return resp.json()
        except httpx.ConnectError as exc:
            raise HTTPException(status_code=503, detail={'error': 'stt_unavailable', 'message': 'STT service is not running'}) from exc


@router.post('/synthesize')
async def synthesize(request: SynthesizeRequest) -> dict:
    # Proxy to local TTS service
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            resp = await client.post(
                'http://127.0.0.1:8804/synthesize',
                json={'text': request.text, 'model': request.model, 'voice': request.voice},
            )
            if resp.status_code != 200:
                raise HTTPException(status_code=502, detail={'error': 'tts_failed', 'message': resp.text})
            return resp.json()
        except httpx.ConnectError as exc:
            raise HTTPException(status_code=503, detail={'error': 'tts_unavailable', 'message': 'TTS service is not running'}) from exc


@router.get('/status')
async def voice_status() -> dict:
    stt_ok = False
    tts_ok = False
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            resp = await client.get('http://127.0.0.1:8803/health')
            stt_ok = resp.status_code == 200
        except httpx.RequestError:
            pass
        try:
            resp = await client.get('http://127.0.0.1:8804/health')
            tts_ok = resp.status_code == 200
        except httpx.RequestError:
            pass
    return {
        'stt': {'available': stt_ok, 'service': 'faster-whisper', 'port': 8803},
        'tts': {'available': tts_ok, 'service': 'kokoro-82M', 'port': 8804},
    }
