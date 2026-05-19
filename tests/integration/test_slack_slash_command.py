from __future__ import annotations

import hashlib
import hmac
import time
from typing import Any
from urllib.parse import urlencode

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from gateway.config import settings
from gateway.routes import slack
from gateway.routes.sessions import store

app = FastAPI()
app.include_router(slack.router, prefix="/api/slack")


class _FakeBackend:
    def create(self) -> str:
        return "slack-sandbox"

    def destroy(self, session_id: str) -> None:
        return None

    def exec_code(self, session_id: str, code: str) -> object:
        raise AssertionError("Slack command test must not execute code")

    def read(self, session_id: str, path: str) -> str:
        return ""

    def write(self, session_id: str, path: str, data: str) -> None:
        return None

    def write_bytes(self, session_id: str, path: str, data: bytes, *, read_only: bool = False) -> None:
        return None

    def list_files(self, session_id: str, path: str) -> list[str]:
        return []


@pytest.fixture(autouse=True)
def _clean_store() -> None:
    store.clear()


def _slack_signature(secret: str, timestamp: str, body: bytes) -> str:
    base = b"v0:" + timestamp.encode("utf-8") + b":" + body
    digest = hmac.new(secret.encode("utf-8"), base, hashlib.sha256).hexdigest()
    return f"v0={digest}"


def test_slack_slash_command_verifies_signature_and_creates_session(monkeypatch: pytest.MonkeyPatch) -> None:
    secret = "test-slack-secret"
    settings.slack_signing_secret = secret
    monkeypatch.setattr("gateway.routes.sessions.create_backend", lambda: _FakeBackend())

    posted_messages: list[dict[str, Any]] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        posted_messages.append({"url": str(request.url), "json": request.read().decode("utf-8")})
        return httpx.Response(200, json={"ok": True})

    transport = httpx.MockTransport(handler)
    async_client = httpx.AsyncClient
    monkeypatch.setattr(slack.httpx, "AsyncClient", lambda **kwargs: async_client(transport=transport))

    body = urlencode(
        {
            "team_id": "T123",
            "channel_id": "C123",
            "user_id": "U123",
            "command": "/mantle",
            "text": "summarize the launch checklist",
            "response_url": "https://slack.example.test/response",
        }
    ).encode("utf-8")
    timestamp = str(int(time.time()))
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "X-Slack-Request-Timestamp": timestamp,
        "X-Slack-Signature": _slack_signature(secret, timestamp, body),
    }

    response = TestClient(app).post("/api/slack/command", content=body, headers=headers)

    assert response.status_code == 200
    session_id = response.json()["session_id"]
    assert store.get(session_id) is not None
    assert response.json()["text"] == "Working on it…"
    assert posted_messages
    assert "summarize the launch checklist" in posted_messages[0]["json"]

    invalid_response = TestClient(app).post(
        "/api/slack/command",
        content=body,
        headers={**headers, "X-Slack-Signature": "v0=invalid"},
    )
    assert invalid_response.status_code == 401
