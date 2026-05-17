from __future__ import annotations

import os

import httpx
from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.responses import Response
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
async def transcribe(
    file: UploadFile,
    model: str = 'faster-whisper-large-v3',
    language: str = 'en',
) -> dict:
    whisper_url = os.environ.get('WHISPER_URL', 'http://127.0.0.1:8803')
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            resp = await client.post(
                f'{whisper_url}/transcribe',
                files={
                    'file': (
                        file.filename or 'audio.wav',
                        await file.read(),
                        file.content_type,
                    )
                },
                data={'model': model, 'language': language},
            )
            if resp.status_code != 200:
                raise HTTPException(
                    status_code=502,
                    detail={'error': 'stt_failed', 'message': resp.text},
                )
            return resp.json()
        except httpx.ConnectError as exc:
            raise HTTPException(
                status_code=503,
                detail={
                    'error': 'stt_unavailable',
                    'message': 'STT service is not running',
                },
            ) from exc


@router.post('/synthesize')
async def synthesize(request: SynthesizeRequest) -> Response:
    kokoro_url = os.environ.get('KOKORO_URL', 'http://127.0.0.1:8804')
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            resp = await client.post(
                f'{kokoro_url}/synthesize',
                json={
                    'text': request.text,
                    'model': request.model,
                    'voice': request.voice,
                },
            )
            if resp.status_code != 200:
                raise HTTPException(
                    status_code=502,
                    detail={'error': 'tts_failed', 'message': resp.text},
                )
            return Response(
                content=resp.content,
                media_type='audio/wav',
                headers={
                    'X-Latency-Ms': resp.headers.get('X-Latency-Ms', ''),
                },
            )
        except httpx.ConnectError as exc:
            raise HTTPException(
                status_code=503,
                detail={
                    'error': 'tts_unavailable',
                    'message': 'TTS service is not running',
                },
            ) from exc


@router.get('/status')
async def voice_status() -> dict:
    stt_ok = False
    tts_ok = False
    whisper_url = os.environ.get('WHISPER_URL', 'http://127.0.0.1:8803')
    kokoro_url = os.environ.get('KOKORO_URL', 'http://127.0.0.1:8804')
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            resp = await client.get(f'{whisper_url}/health')
            stt_ok = resp.status_code == 200
        except httpx.RequestError:
            pass
        try:
            resp = await client.get(f'{kokoro_url}/health')
            tts_ok = resp.status_code == 200
        except httpx.RequestError:
            pass
    return {
        'stt': {
            'available': stt_ok,
            'service': 'faster-whisper',
            'port': 8803,
        },
        'tts': {
            'available': tts_ok,
            'service': 'kokoro-82M',
            'port': 8804,
        },
    }
