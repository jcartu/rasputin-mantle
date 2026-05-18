from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from shared.types import ExecRequest, ExecResult, SessionInfo, SessionStatus, StreamEvent


class SessionInfoSchema(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    session_id: str
    status: SessionStatus
    created_at: float
    cost_tokens: int = 0
    cost_dollars: float = 0.0
    sandbox_id: str | None = None

    @classmethod
    def from_type(cls, info: SessionInfo) -> SessionInfoSchema:
        return cls(
            session_id=info.session_id,
            status=info.status,
            created_at=info.created_at,
            cost_tokens=info.cost_tokens,
            cost_dollars=info.cost_dollars,
            sandbox_id=info.sandbox_id,
        )

    def to_type(self) -> SessionInfo:
        return SessionInfo(
            session_id=self.session_id,
            status=SessionStatus(self.status),
            created_at=self.created_at,
            cost_tokens=self.cost_tokens,
            cost_dollars=self.cost_dollars,
            sandbox_id=self.sandbox_id,
        )


class ExecRequestSchema(BaseModel):
    session_id: str
    code: str = Field(min_length=1)
    timeout_seconds: int = Field(default=120, ge=1, le=3600)

    @classmethod
    def from_type(cls, request: ExecRequest) -> ExecRequestSchema:
        return cls(
            session_id=request.session_id,
            code=request.code,
            timeout_seconds=request.timeout_seconds,
        )

    def to_type(self) -> ExecRequest:
        return ExecRequest(
            session_id=self.session_id,
            code=self.code,
            timeout_seconds=self.timeout_seconds,
        )


class ExecResultSchema(BaseModel):
    stdout: str
    stderr: str
    exit_code: int
    duration_ms: int
    files_changed: list[str]
    results: list[Any]

    @classmethod
    def from_type(cls, result: ExecResult) -> ExecResultSchema:
        return cls(
            stdout=result.stdout,
            stderr=result.stderr,
            exit_code=result.exit_code,
            duration_ms=result.duration_ms,
            files_changed=result.files_changed,
            results=result.results,
        )

    def to_type(self) -> ExecResult:
        return ExecResult(
            stdout=self.stdout,
            stderr=self.stderr,
            exit_code=self.exit_code,
            duration_ms=self.duration_ms,
            files_changed=self.files_changed,
            results=self.results,
        )


class StreamEventSchema(BaseModel):
    event_type: Literal["token", "plan", "tool_call", "error", "complete", "heartbeat"]
    data: dict[str, Any]
    timestamp: float

    @classmethod
    def from_type(cls, event: StreamEvent) -> StreamEventSchema:
        return cls(event_type=event.event_type, data=event.data, timestamp=event.timestamp)

    def to_type(self) -> StreamEvent:
        return StreamEvent(event_type=self.event_type, data=self.data, timestamp=self.timestamp)


class Playbook(BaseModel):
    id: str
    title: str
    description: str
    intent: str
    prompt_template: str
    created_by: str
    created_at: str
