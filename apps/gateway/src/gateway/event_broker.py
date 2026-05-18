from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any, Literal

EventType = Literal["tool_call", "reasoning", "file_touch", "screenshot", "error", "completion"]


@dataclass(frozen=True)
class BrokerEvent:
    event_type: EventType
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def model_dump(self) -> dict[str, Any]:
        return {"event_type": self.event_type, "data": self.data, "timestamp": self.timestamp}


class EventBroker:
    def __init__(self, *, max_queue_size: int = 256) -> None:
        self._max_queue_size = max_queue_size
        self._queues: dict[str, set[asyncio.Queue[BrokerEvent]]] = {}
        self._lock = asyncio.Lock()

    async def publish(self, session_id: str, event: BrokerEvent | dict[str, Any]) -> None:
        broker_event = _coerce_event(event)
        async with self._lock:
            queues = tuple(self._queues.get(session_id, ()))
        for queue in queues:
            if not queue.full():
                queue.put_nowait(broker_event)

    async def subscribe(self, session_id: str) -> AsyncIterator[BrokerEvent]:
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
    event_type = event.get("event_type")
    if event_type not in {"tool_call", "reasoning", "file_touch", "screenshot", "error", "completion"}:
        raise ValueError(f"Unsupported event_type: {event_type}")
    data = event.get("data")
    if not isinstance(data, dict):
        data = {}
    timestamp = float(event.get("timestamp") or time.time())
    return BrokerEvent(event_type=event_type, data=data, timestamp=timestamp)


broker = EventBroker()
