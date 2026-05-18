from __future__ import annotations

import os
from dataclasses import dataclass

from fastapi import APIRouter, HTTPException

from gateway.routes.sessions import store

router = APIRouter()


@dataclass(frozen=True)
class NekoSession:
    url: str
    status: str


_neko_sessions: dict[str, NekoSession] = {}


@router.post("/api/sessions/{id}/neko")
async def get_neko_session(id: str) -> dict[str, str]:
    session = store.get(id)
    if session is None:
        raise HTTPException(status_code=404, detail={"error": "session_not_found", "message": "Session not found"})

    existing = _neko_sessions.get(id)
    if existing is not None:
        return {"url": existing.url, "status": existing.status}

    neko = NekoSession(url=_neko_url(id), status="running" if _neko_is_configured() else "starting")
    _neko_sessions[id] = neko
    return {"url": neko.url, "status": neko.status}


def _neko_url(session_id: str) -> str:
    template = os.environ.get("MANTLE_NEKO_URL_TEMPLATE")
    if template:
        return template.format(session_id=session_id)
    base_url = os.environ.get("MANTLE_NEKO_BASE_URL", "http://127.0.0.1:8080").rstrip("/")
    return f"{base_url}/?session={session_id}"


def _neko_is_configured() -> bool:
    return bool(os.environ.get("MANTLE_NEKO_BASE_URL") or os.environ.get("MANTLE_NEKO_URL_TEMPLATE"))
