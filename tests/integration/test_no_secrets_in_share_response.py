from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient
from gateway.routes import share


class _Acquire:
    def __init__(self, conn: "_ShareConn") -> None:
        self._conn = conn

    async def __aenter__(self) -> "_ShareConn":
        return self._conn

    async def __aexit__(self, *_exc: object) -> None:
        return None


class _SharePool:
    def __init__(self, conn: "_ShareConn") -> None:
        self._conn = conn

    def acquire(self) -> _Acquire:
        return _Acquire(self._conn)


class _ShareWriter:
    def __init__(self, conn: "_ShareConn") -> None:
        self._pool = _SharePool(conn)


class _ShareConn:
    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        self.share_public = False
        self.expires_at: datetime | None = None
        self.created_at = datetime.now(timezone.utc)
        self.events = [
            {
                "seq": 1,
                "ts": self.created_at,
                "event_type": "tool_result",
                "payload": {
                    "data": {
                        "api_key": "sk-test-api-key",
                        "auth_token": "auth-token-value",
                        "nested": {
                            "access_token": "access-token-value",
                            "safe_text": "visible content",
                        },
                    }
                },
            },
            {
                "seq": 2,
                "ts": self.created_at,
                "event_type": "completion",
                "payload": {
                    "data": {
                        "final_answer": "safe answer",
                        "refresh_token": "refresh-token-value",
                    }
                },
            },
        ]

    async def fetchrow(self, query: str, *args: Any) -> dict[str, Any] | None:
        if "information_schema.columns" in query:
            return None
        if "FROM share_tokens" in query:
            if not self.share_public:
                return None
            return {
                "session_id": self.session_id,
                "public": True,
                "expires_at": self.expires_at,
                "created_at": self.created_at,
            }
        raise AssertionError(f"Unexpected fetchrow query: {query}")

    async def fetch(self, query: str, *args: Any) -> list[dict[str, Any]]:
        if "FROM session_events" in query:
            return self.events
        raise AssertionError(f"Unexpected fetch query: {query}")

    async def execute(self, query: str, *args: Any) -> str:
        if "INSERT INTO share_tokens" in query:
            self.share_public = bool(args[3])
            self.expires_at = args[2]
            return "INSERT 0 1"
        raise AssertionError(f"Unexpected execute query: {query}")


def test_share_response_strips_secret_keys_from_events() -> None:
    session_id = "share-security-session"
    share.set_writer(_ShareWriter(_ShareConn(session_id)))
    test_app = FastAPI()
    test_app.include_router(share.router, prefix="/api/share")
    client = TestClient(test_app)

    patch = client.patch(f"/api/share/{session_id}", json={"share_public": True})
    assert patch.status_code == 200

    response = client.get(f"/api/share/{session_id}")
    assert response.status_code == 200
    body = response.json()

    assert set(body) == {"session", "steps", "final_answer"}
    assert body["session"]["session_id"] == session_id
    assert body["session"]["share_public"] is True
    assert isinstance(body["steps"], list)
    assert body["final_answer"] == "safe answer"

    serialized = json.dumps(body)
    for secret_key in ("api_key", "auth_token", "access_token", "refresh_token"):
        assert secret_key not in serialized
    for secret_value in ("sk-test-api-key", "auth-token-value", "access-token-value", "refresh-token-value"):
        assert secret_value not in serialized
    assert "visible content" in serialized
