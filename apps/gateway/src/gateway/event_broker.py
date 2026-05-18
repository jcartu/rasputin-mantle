from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any, Literal

EventType = Literal[
    "tool_call",
    "reasoning",
    "file_touch",
    "screenshot",
    "error",
    "completion",
    # StreamEventSchema compat types
    "token",
    "plan",
    "complete",
    "heartbeat",
]

ALL_EVENT_TYPES = set(EventType.__args__)  # type: ignore[attr-defined]


@dataclass(frozen=True)
class BrokerEvent:
    event_type: EventType
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def model_dump(self) -> dict[str, Any]:
        return {"event_type": self.event_type, "data": self.data, "timestamp": self.timestamp}


class EventBroker:
    """Single SSE broker — replaces the old EventBroker in sessions.py.

    Supports both legacy sync API (get_queue, publish, remove) for SSE routes
    and modern async subscribe() for new consumers.
    """

    def __init__(self, *, max_queue_size: int = 256) -> None:
        self._max_queue_size = max_queue_size
        self._queues: dict[str, set[asyncio.Queue[BrokerEvent]]] = {}
        self._lock = asyncio.Lock()

    # ── Legacy sync API (backward compat with SSE routes & tests) ──

    def get_queue(self, session_id: str) -> asyncio.Queue[BrokerEvent]:
        """Return (or create) the primary queue for a session."""
        if session_id not in self._queues:
            self._queues[session_id] = set()
        if not self._queues[session_id]:
            q = asyncio.Queue(maxsize=self._max_queue_size)
            self._queues[session_id].add(q)
        return next(iter(self._queues[session_id]))

    def publish(self, session_id: str, event: BrokerEvent | dict[str, Any]) -> None:
        """Push an event to all subscriber queues for *session_id*."""
        broker_event = _coerce_event(event)
        # Auto-create queue if none exists (backward compat with SSE routes)
        self.get_queue(session_id)
        for queue in self._queues.get(session_id, ()):
            if not queue.full():
                queue.put_nowait(broker_event)

    def remove(self, session_id: str) -> None:
        """Clean up queues for a terminated session."""
        self._queues.pop(session_id, None)

    # ── Modern async API ──

    async def subscribe(self, session_id: str) -> AsyncIterator[BrokerEvent]:
        """Async generator — yields events until the consumer disconnects."""
        queue: asyncio.Queue[BrokerEvent] = asyncio.Queue(maxsize=self._max_queue_size)
        async with self._lock:
            self._queues.setdefault(session_id, set()).add(queue)
        try:
            while True:
                yield await queue.get()
        finally:
            async with self._lock:
                queues = self._queues.get(session_id)
                if queues is not None:
                    queues.discard(queue)
                    if not queues:
                        self._queues.pop(session_id, None)


def _coerce_event(event: BrokerEvent | dict[str, Any]) -> BrokerEvent:
    if isinstance(event, BrokerEvent):
        return event
    # Handle Pydantic models (StreamEventSchema has model_dump)
    if hasattr(event, "model_dump"):
        event = event.model_dump()  # type: ignore[attr-defined]
    event_type = event.get("event_type")
    if event_type not in ALL_EVENT_TYPES:
        raise ValueError(f"Unsupported event_type: {event_type}")
    data = event.get("data")
    if not isinstance(data, dict):
        data = {}
    timestamp = float(event.get("timestamp") or time.time())
    return BrokerEvent(event_type=event_type, data=data, timestamp=timestamp)


broker = EventBroker()
