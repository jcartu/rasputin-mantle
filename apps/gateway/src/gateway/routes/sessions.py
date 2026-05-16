from __future__ import annotations

import asyncio
import json
import time
import uuid

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from sandbox.backend import create_backend
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
    backend = create_backend()
    sandbox_id = backend.create()
    info = SessionInfo(
        session_id=session_id,
        status=SessionStatus.ACTIVE,
        created_at=time.time(),
        sandbox_id=sandbox_id,
    )
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
    session = store.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail={'error': 'session_not_found', 'message': 'Session not found'})
    if request.session_id != session_id:
        raise HTTPException(
            status_code=400,
            detail={'error': 'session_id_mismatch', 'message': 'Request session_id must match the route session_id'},
        )
    if session.sandbox_id is None:
        raise HTTPException(status_code=500, detail={'error': 'no_sandbox', 'message': 'Session has no sandbox'})
    try:
        backend = create_backend()
        result = backend.exec_code(session.sandbox_id, request.code)
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
        duration_ms=0,
        files_changed=[],
        results=[],
    )

@router.delete('/{session_id}')
async def delete_session(session_id: str) -> dict[str, str]:
    session = store.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail={'error': 'session_not_found', 'message': 'Session not found'})
    if session.sandbox_id is not None:
        backend = create_backend()
        backend.destroy(session.sandbox_id)
    store._sessions.pop(session_id, None)
    return {'status': 'deleted'}

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
