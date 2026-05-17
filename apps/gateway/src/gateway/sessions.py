from __future__ import annotations

from dataclasses import replace
from typing import Any, Optional

import asyncio

from shared.types import SessionInfo, SessionStatus
from shared.schemas import StreamEventSchema


class EventBroker:
    """Per-session asyncio.Queue broker for SSE events."""

    def __init__(self) -> None:
        self._queues: dict[str, asyncio.Queue] = {}

    def get_queue(self, session_id: str) -> asyncio.Queue:
        q = self._queues.get(session_id)
        if q is None:
            q = asyncio.Queue(maxsize=256)
            self._queues[session_id] = q
        return q

    def publish(self, session_id: str, event: StreamEventSchema) -> None:
        q = self.get_queue(session_id)
        if not q.full():
            q.put_nowait(event)

    def remove(self, session_id: str) -> None:
        self._queues.pop(session_id, None)


broker = EventBroker()


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, SessionInfo] = {}

    def create(self, info: SessionInfo) -> None:
        self._sessions[info.session_id] = info

    def get(self, session_id: str) -> Optional[SessionInfo]:
        return self._sessions.get(session_id)

    def list_all(self) -> list[SessionInfo]:
        return list(self._sessions.values())

    def update_status(self, session_id: str, status: SessionStatus) -> None:
        info = self._sessions.get(session_id)
        if info:
            self._sessions[session_id] = replace(info, status=status)

    def update_cost(self, session_id: str, *, cost_tokens: int, cost_dollars: float) -> None:
        info = self._sessions.get(session_id)
        if info:
            self._sessions[session_id] = replace(
                info,
                cost_tokens=info.cost_tokens + cost_tokens,
                cost_dollars=info.cost_dollars + cost_dollars,
            )

    def clear(self) -> None:
        self._sessions = {}
