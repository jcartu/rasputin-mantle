from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from gateway.config import settings
from gateway.routes import mail
from gateway.routes.sessions import store

app = FastAPI()
app.include_router(mail.router, prefix="/api/mail")


class _FakeBackend:
    def create(self) -> str:
        return "mail-sandbox"

    def destroy(self, session_id: str) -> None:
        return None

    def exec_code(self, session_id: str, code: str) -> object:
        raise AssertionError("Inbound mail test must not execute code")

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


def test_inbound_mailhog_message_creates_session_and_enforces_allowlist(monkeypatch: pytest.MonkeyPatch) -> None:
    settings.mail_allowed_senders = "alice@example.com,@trusted.test"
    monkeypatch.setattr("gateway.routes.sessions.create_backend", lambda: _FakeBackend())

    client = TestClient(app)
    response = client.post(
        "/api/mail/inbound",
        json={
            "sender": "Alice <alice@example.com>",
            "subject": "Draft launch notes",
            "body": "Turn these notes into a release-ready checklist.",
            "message_id": "<mailhog-1@example.com>",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert store.get(payload["session_id"]) is not None
    assert payload["title"] == "Draft launch notes"
    assert payload["prompt"] == "Turn these notes into a release-ready checklist."

    denied = client.post(
        "/api/mail/inbound",
        json={"sender": "mallory@example.net", "subject": "bad", "body": "ignore"},
    )
    assert denied.status_code == 403

    spam = client.post(
        "/api/mail/inbound",
        json={"sender": "Alice <alice@example.com>", "subject": "spam", "body": "ignore", "spam": True},
    )
    assert spam.status_code == 200
    assert spam.json() == {"status": "skipped_spam"}
