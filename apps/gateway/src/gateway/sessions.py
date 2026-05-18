from __future__ import annotations

from dataclasses import replace
from typing import Any, Optional

from shared.types import SessionInfo, SessionStatus

# Re-export broker from event_broker (single source of truth)
from gateway.event_broker import broker  # noqa: F401

__all__ = ["SessionStore", "broker"]


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
