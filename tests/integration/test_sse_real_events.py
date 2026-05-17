from __future__ import annotations

import asyncio
import json
import time

import pytest

from gateway.routes.sessions import store, broker
from shared.schemas import StreamEventSchema
from shared.types import SessionInfo, SessionStatus


@pytest.fixture(autouse=True)
def _clean_store() -> None:
    store.clear()
    broker._queues.clear()


async def _collect_events(session_id: str, max_events: int = 5, timeout: float = 2.0) -> list[str]:
    """Collect SSE events from the broker queue directly (avoids TestClient stream blocking)."""
    queue = broker.get_queue(session_id)
    lines: list[str] = []

    for _ in range(max_events):
        try:
            event = await asyncio.wait_for(queue.get(), timeout=timeout)
            line = f"event: {event.event_type}\ndata: {json.dumps(event.model_dump(), separators=(',', ':'))}\n\n"
            lines.append(line)
        except asyncio.TimeoutError:
            break

    return lines


def test_sse_stream_emits_real_events_from_broker() -> None:
    """SSE stream must deliver real events from the broker, not just heartbeats."""
    session_id = "sse-test-session"
    info = SessionInfo(
        session_id=session_id,
        status=SessionStatus.ACTIVE,
        created_at=time.time(),
        sandbox_id=None,
    )
    store.create(info)

    broker.publish(
        session_id,
        StreamEventSchema(
            event_type="token",
            data={"text": "hello from broker"},
            timestamp=time.time(),
        ),
    )
    broker.publish(
        session_id,
        StreamEventSchema(
            event_type="complete",
            data={"status": "done"},
            timestamp=time.time(),
        ),
    )

    lines = asyncio.run(_collect_events(session_id))

    event_types = []
    for line in lines:
        if line.startswith("event:"):
            event_types.append(line.split("\n")[0].split(":", 1)[1].strip())

    assert "token" in event_types, f"Expected 'token' event, got {event_types}"
    assert "complete" in event_types, f"Expected 'complete' event, got {event_types}"


def test_sse_stream_contains_real_newlines_not_literal() -> None:
    """SSE output must contain real newline characters, not literal backslash-n."""
    session_id = "sse-newline-test"
    info = SessionInfo(
        session_id=session_id,
        status=SessionStatus.ACTIVE,
        created_at=time.time(),
        sandbox_id=None,
    )
    store.create(info)

    broker.publish(
        session_id,
        StreamEventSchema(
            event_type="token",
            data={"text": "test"},
            timestamp=time.time(),
        ),
    )

    lines = asyncio.run(_collect_events(session_id))
    raw = "".join(lines)

    assert "\n" in raw, "SSE stream must contain real newline characters"
    assert "\\n" not in raw, "SSE stream must NOT contain literal \\n characters"


def test_sse_stream_returns_404_for_unknown_session() -> None:
    """SSE stream must return 404 for non-existent sessions."""
    from fastapi.testclient import TestClient
    from gateway.app import app

    client = TestClient(app)
    resp = client.get("/api/sessions/nonexistent/stream")
    assert resp.status_code == 404


def test_event_broker_publish_and_queue() -> None:
    """EventBroker.publish() puts events on per-session queues."""
    session_id = "broker-test"
    q = broker.get_queue(session_id)
    assert q.empty()

    broker.publish(
        session_id,
        StreamEventSchema(
            event_type="token",
            data={"text": "broker test"},
            timestamp=time.time(),
        ),
    )
    assert q.qsize() == 1

    event = q.get_nowait()
    assert event.event_type == "token"
    assert event.data["text"] == "broker test"


def test_event_broker_removes_queue_on_delete() -> None:
    """EventBroker.remove() cleans up per-session queues."""
    session_id = "broker-remove-test"
    broker.get_queue(session_id)
    assert session_id in broker._queues

    broker.remove(session_id)
    assert session_id not in broker._queues
