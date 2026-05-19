from __future__ import annotations

import asyncio
import json
import time
import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sandbox.backend import create_backend
from shared.schemas import ExecRequestSchema, ExecResultSchema, SessionInfoSchema, StreamEventSchema
from shared.types import ExecResult, SessionInfo, SessionStatus

from gateway.config import settings
from gateway.eval_mode import is_eval_mode
from gateway.sessions import SessionStore, broker

router = APIRouter()
store = SessionStore()
_writer: Any = None


class SessionCreateRequest(BaseModel):
    project_id: str | None = None


def set_writer(writer: Any) -> None:
    global _writer
    _writer = writer


async def _pool() -> Any:
    if _writer is None or _writer._pool is None:
        raise HTTPException(
            status_code=503,
            detail={"error": "persistence_unavailable", "message": "Project persistence not available"},
        )
    return _writer._pool


def _list_value(value: Any) -> list[str]:
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return []
        return [str(item) for item in parsed] if isinstance(parsed, list) else []
    if isinstance(value, list):
        return [str(item) for item in value]
    return []


@router.get("", response_model=list[SessionInfoSchema])
async def list_sessions(project_id: str | None = Query(default=None)) -> list[SessionInfo]:
    sessions = store.list_all()
    if project_id == "personal":
        return [session for session in sessions if session.project_id is None]
    if project_id is not None:
        return [session for session in sessions if session.project_id == project_id]
    return sessions


@router.post("", response_model=SessionInfoSchema)
async def create_session(request: SessionCreateRequest | None = None) -> SessionInfo:
    request = request or SessionCreateRequest()
    session_id = str(uuid.uuid4())
    backend = create_backend()
    sandbox_id = backend.create()
    project_row: Any | None = None
    kb_rows: list[Any] = []
    kb_index: list[str] = []
    system_prompt_addendum: str | None = None
    default_planner: str | None = None
    allowed_tools: list[str] | None = None

    if request.project_id is not None:
        pool = await _pool()
        async with pool.acquire() as conn:
            project_row = await conn.fetchrow("SELECT * FROM projects WHERE id = $1::uuid", request.project_id)
            if project_row is None:
                backend.destroy(sandbox_id)
                raise HTTPException(
                    status_code=404, detail={"error": "project_not_found", "message": "Project not found"}
                )
            if not is_eval_mode():
                kb_rows = await conn.fetch(
                    """
                    SELECT filename, storage_path
                    FROM project_kb_files
                    WHERE project_id = $1::uuid
                    ORDER BY uploaded_at ASC
                    """,
                    request.project_id,
                )
        default_planner = project_row["default_planner"]
        allowed_tools = _list_value(project_row["allowed_tools"])
        raw_addendum = project_row["system_prompt_addendum"]
        system_prompt_addendum = raw_addendum

        if not is_eval_mode():
            kb_index = [row["filename"] for row in kb_rows]
            kb_index_text = ", ".join(kb_index) if kb_index else "(empty)"
            kb_instruction = (
                f"You have access to project knowledge at /workspace/{session_id}/_kb/. "
                f"Reference these files when relevant. KB index: {kb_index_text}."
            )
            system_prompt_addendum = f"{raw_addendum}\n\n{kb_instruction}" if raw_addendum else kb_instruction

            for row in kb_rows:
                source = Path(settings.kb_root).resolve() / request.project_id / "kb" / row["storage_path"]
                if source.exists():
                    target = f"/workspace/{session_id}/_kb/{row['filename']}"
                    backend.write_bytes(sandbox_id, target, source.read_bytes(), read_only=True)

    info = SessionInfo(
        session_id=session_id,
        status=SessionStatus.ACTIVE,
        created_at=time.time(),
        sandbox_id=sandbox_id,
        project_id=request.project_id,
        default_planner=default_planner,
        system_prompt_addendum=system_prompt_addendum,
        allowed_tools=allowed_tools,
        kb_index=kb_index,
    )
    store.create(info)
    return info


@router.get("/{session_id}", response_model=SessionInfoSchema)
async def get_session(session_id: str) -> SessionInfo:
    info = store.get(session_id)
    if info is None:
        raise HTTPException(status_code=404, detail={"error": "session_not_found", "message": "Session not found"})
    return info


@router.post("/{session_id}/exec", response_model=ExecResultSchema)
async def exec_code_route(session_id: str, request: ExecRequestSchema) -> ExecResult:
    session = store.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail={"error": "session_not_found", "message": "Session not found"})
    if request.session_id != session_id:
        raise HTTPException(
            status_code=400,
            detail={"error": "session_id_mismatch", "message": "Request session_id must match the route session_id"},
        )
    if session.sandbox_id is None:
        raise HTTPException(status_code=500, detail={"error": "no_sandbox", "message": "Session has no sandbox"})
    try:
        backend = create_backend()
        result = backend.exec_code(session.sandbox_id, request.code)
        broker.publish(
            session_id,
            StreamEventSchema(
                event_type="token",
                data={"stdout": result.stdout[:1024], "exit_code": result.exit_code},
                timestamp=time.time(),
            ),
        )
    except TimeoutError as exc:
        store.update_status(session_id, SessionStatus.ERROR)
        raise HTTPException(
            status_code=408,
            detail={"error": "exec_timeout", "message": "Execution timed out"},
        ) from exc
    except Exception as exc:
        store.update_status(session_id, SessionStatus.ERROR)
        raise HTTPException(status_code=500, detail={"error": "exec_failed", "message": str(exc)}) from exc
    return ExecResult(
        stdout=result.stdout,
        stderr=result.stderr,
        exit_code=result.exit_code,
        duration_ms=0,
        files_changed=[],
        results=[],
    )


@router.delete("/{session_id}")
async def delete_session(session_id: str) -> dict[str, str]:
    session = store.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail={"error": "session_not_found", "message": "Session not found"})
    if session.sandbox_id is not None:
        backend = create_backend()
        backend.destroy(session.sandbox_id)
    store._sessions.pop(session_id, None)
    return {"status": "deleted"}


@router.get("/{session_id}/stream")
async def stream_session(session_id: str) -> StreamingResponse:
    if store.get(session_id) is None:
        raise HTTPException(status_code=404, detail={"error": "session_not_found", "message": "Session not found"})

    queue = broker.get_queue(session_id)

    async def event_generator():  # type: ignore[no-untyped-def]
        try:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                    line = (
                        f"event: {event.event_type}\ndata: {json.dumps(event.model_dump(), separators=(',', ':'))}\n\n"
                    )
                    yield line
                except asyncio.TimeoutError:
                    yield "event: heartbeat\ndata: {}\n\n"
        except asyncio.CancelledError:
            pass

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
