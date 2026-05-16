from __future__ import annotations

import asyncio
import json
import time
import uuid

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from shared.schemas import ExecRequestSchema, ExecResultSchema, SessionInfoSchema, StreamEventSchema
from shared.types import ExecResult, SessionInfo, SessionStatus

from gateway.sessions import SessionStore

router = APIRouter()
store = SessionStore()


@router.get('', response_model=list[SessionInfoSchema])
async def list_sessions() -> list[SessionInfo]:
    return store.list_all()


@router.post('', response_model=SessionInfoSchema)
async def create_session() -> SessionInfo:
    session_id = str(uuid.uuid4())
    info = SessionInfo(session_id=session_id, status=SessionStatus.ACTIVE, created_at=time.time())
    store.create(info)
    return info


@router.get('/{session_id}', response_model=SessionInfoSchema)
async def get_session(session_id: str) -> SessionInfo:
    info = store.get(session_id)
    if info is None:
        raise HTTPException(status_code=404, detail={'error': 'session_not_found', 'message': 'Session not found'})
    return info


@router.post('/{session_id}/exec', response_model=ExecResultSchema)
async def exec_code_route(session_id: str, request: ExecRequestSchema) -> ExecResult:
    if store.get(session_id) is None:
        raise HTTPException(status_code=404, detail={'error': 'session_not_found', 'message': 'Session not found'})
    if request.session_id != session_id:
        raise HTTPException(
            status_code=400,
            detail={'error': 'session_id_mismatch', 'message': 'Request session_id must match the route session_id'},
        )
    try:
        from codeact.executor import execute_code
        result = await asyncio.wait_for(execute_code(request.code), timeout=request.timeout_seconds)
    except TimeoutError as exc:
        store.update_status(session_id, SessionStatus.ERROR)
        raise HTTPException(
            status_code=408,
            detail={'error': 'exec_timeout', 'message': 'Execution timed out'},
        ) from exc
    except Exception as exc:
        store.update_status(session_id, SessionStatus.ERROR)
        raise HTTPException(status_code=500, detail={'error': 'exec_failed', 'message': str(exc)}) from exc
    return ExecResult(
        stdout=result.stdout,
        stderr=result.stderr,
        exit_code=result.exit_code,
        duration_ms=result.duration_ms,
        files_changed=result.files_changed,
        results=result.results,
    )


@router.get('/{session_id}/stream')
async def stream_session(session_id: str) -> StreamingResponse:
    if store.get(session_id) is None:
        raise HTTPException(status_code=404, detail={'error': 'session_not_found', 'message': 'Session not found'})

    async def event_generator():  # type: ignore[no-untyped-def]
        while True:
            event = StreamEventSchema(event_type='heartbeat', data={'type': 'heartbeat'}, timestamp=time.time())
            yield f"event: {event.event_type}\\ndata: {json.dumps(event.model_dump(), separators=(',', ':'))}\\n\\n"
            await asyncio.sleep(30)

    return StreamingResponse(
        event_generator(),
        media_type='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'},
    )
