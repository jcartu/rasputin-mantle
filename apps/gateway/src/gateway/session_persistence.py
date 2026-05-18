from __future__ import annotations

import json
import logging
from typing import Any

from gateway.event_broker import BrokerEvent

logger = logging.getLogger(__name__)

try:
    import asyncpg
except ImportError:
    asyncpg = None  # type: ignore[assignment]

try:
    import psycopg2
except ImportError:
    psycopg2 = None  # type: ignore[assignment]


class SessionEventWriter:
    """Persists session events to PostgreSQL session_events table.

    - Maintains per-session seq counter (in-memory, starts at 1)
    - Uses asyncpg connection pool (with psycopg2 fallback)
    - UPSERT on UNIQUE(session_id, seq) constraint
    - Gracefully degrades if DB unavailable
    """

    def __init__(self, dsn: str) -> None:
        """Initialize writer with database DSN.

        Args:
            dsn: PostgreSQL connection string
        """
        self.dsn = dsn
        self._pool: asyncpg.Pool | None = None
        self._seq_counters: dict[str, int] = {}
        self._use_asyncpg = asyncpg is not None

    async def initialize(self) -> None:
        """Create connection pool. Called at gateway startup."""
        if not self._use_asyncpg:
            logger.warning("asyncpg not available, session persistence disabled")
            return

        try:
            self._pool = await asyncpg.create_pool(
                self.dsn,
                min_size=2,
                max_size=10,
                command_timeout=10,
            )
            logger.info("SessionEventWriter pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize SessionEventWriter pool: {e}")
            self._pool = None

    async def close(self) -> None:
        """Close connection pool. Called at gateway shutdown."""
        if self._pool is not None:
            await self._pool.close()
            self._pool = None

    async def write(self, session_id: str, event: BrokerEvent | dict[str, Any]) -> None:
        """Write event to session_events table.

        Args:
            session_id: UUID of the session
            event: BrokerEvent or dict with event_type, data, timestamp
        """
        if self._pool is None:
            logger.debug(f"Skipping persistence for {session_id} (pool unavailable)")
            return

        # Coerce to dict if BrokerEvent
        if isinstance(event, BrokerEvent):
            event_dict = event.model_dump()
        else:
            event_dict = event

        event_type = event_dict.get("event_type")
        if not event_type:
            logger.warning(f"Event missing event_type: {event_dict}")
            return

        # Increment seq counter for this session
        self._seq_counters[session_id] = self._seq_counters.get(session_id, 0) + 1
        seq = self._seq_counters[session_id]

        # Payload is the full event dict
        payload = json.dumps(event_dict)

        try:
            async with self._pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO session_events (session_id, seq, event_type, payload)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (session_id, seq) DO UPDATE SET
                        event_type = EXCLUDED.event_type,
                        payload = EXCLUDED.payload,
                        ts = now()
                    """,
                    session_id,
                    seq,
                    event_type,
                    payload,
                )
        except Exception as e:
            logger.error(f"Failed to write event for {session_id}: {e}")
