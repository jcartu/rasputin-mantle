from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class SessionStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class SessionInfo:
    session_id: str
    status: SessionStatus
    created_at: float
    cost_tokens: int = 0
    cost_dollars: float = 0.0
    sandbox_id: str | None = None


@dataclass(frozen=True)
class ExecRequest:
    session_id: str
    code: str
    timeout_seconds: int = 120


@dataclass(frozen=True)
class ExecResult:
    stdout: str
    stderr: str
    exit_code: int
    duration_ms: int
    files_changed: list[str]
    results: list[Any]


@dataclass(frozen=True)
class StreamEvent:
    event_type: str
    data: dict[str, Any]
    timestamp: float
