from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from gateway.routes import share
from gateway.routes.sessions import store
from shared.types import SessionInfo, SessionStatus

app = FastAPI()
app.include_router(share.router, prefix="/api/share")


class _Row(dict[str, Any]):
    def __getitem__(self, key: str) -> Any:
        return dict.__getitem__(self, key)


class _Acquire:
    def __init__(self, conn: "_ShareConn") -> None:
        self._conn = conn

    async def __aenter__(self) -> "_ShareConn":
        return self._conn

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None


class _SharePool:
    def __init__(self, conn: "_ShareConn") -> None:
        self._conn = conn

    def acquire(self) -> _Acquire:
        return _Acquire(self._conn)


class _Writer:
    def __init__(self, conn: "_ShareConn") -> None:
        self._pool = _SharePool(conn)


class _ShareConn:
    def __init__(self) -> None:
        self.public_sessions: dict[str, bool] = {}
        self.events: dict[str, list[_Row]] = {}

    async def fetchrow(self, query: str, *args: Any) -> _Row | None:
        if "information_schema.columns" in query:
            return _Row({"?column?": 1})

        session_id = str(args[0])
        if "FROM share_tokens" in query or "FROM sessions" in query:
            if self.public_sessions.get(session_id):
                return _Row(
                    {
                        "session_id": session_id,
                        "public": True,
                        "expires_at": None,
                        "created_at": datetime.now(timezone.utc),
                    }
                )
            return None
        return None

    async def fetch(self, query: str, *args: Any) -> list[_Row]:
        session_id = str(args[0])
        return self.events.get(session_id, [])

    async def execute(self, query: str, *args: Any) -> str:
        session_id = str(args[0])
        if "INSERT INTO share_tokens" in query:
            self.public_sessions[session_id] = bool(args[3])
        if "UPDATE sessions SET share_public" in query:
            self.public_sessions[session_id] = bool(args[1])
        return "OK"


@pytest.fixture(autouse=True)
def _clean_store() -> None:
    store.clear()


def test_public_share_link_works_without_auth_and_private_returns_404() -> None:
    conn = _ShareConn()
    share.set_writer(_Writer(conn))
    client = TestClient(app)
    session_id = "public-share-session"
    store.create(SessionInfo(session_id=session_id, status=SessionStatus.ACTIVE, created_at=time.time()))
    conn.events[session_id] = [
        _Row(
            {
                "seq": 1,
                "ts": datetime(2026, 5, 19, tzinfo=timezone.utc),
                "event_type": "completion",
                "payload": {"data": {"final_answer": "done", "api_key": "secret"}},
            }
        )
    ]

    private_response = client.get(f"/api/share/{session_id}")
    assert private_response.status_code == 404

    patch_response = client.patch(f"/api/share/{session_id}", json={"share_public": True})
    assert patch_response.status_code == 200

    public_response = client.get(f"/api/share/{session_id}")
    assert public_response.status_code == 200
    payload = public_response.json()
    assert payload["session"]["session_id"] == session_id
    assert payload["session"]["share_public"] is True
    assert payload["final_answer"] == "done"
    assert "api_key" not in payload["steps"][0]["payload"]["data"]

    patch_private_response = client.patch(f"/api/share/{session_id}", json={"share_public": False})
    assert patch_private_response.status_code == 200
    assert client.get(f"/api/share/{session_id}").status_code == 404
