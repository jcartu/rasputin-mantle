from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Query

logger = logging.getLogger(__name__)

router = APIRouter()

# Will be set by app.py at startup
_writer: Any = None


def set_writer(writer: Any) -> None:
    """Set the SessionEventWriter instance (called from app.py)."""
    global _writer
    _writer = writer


@router.get("/{session_id}/events")
async def get_session_events(
    session_id: str,
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    """Get paginated session events from session_events table.

    Args:
        session_id: UUID of the session
        limit: Number of events to return (1-1000, default 50)
        offset: Number of events to skip (default 0)

    Returns:
        {
            "events": [
                {
                    "id": 123,
                    "session_id": "...",
                    "seq": 1,
                    "ts": "2026-05-19T...",
                    "event_type": "tool_call",
                    "payload": {...}
                },
                ...
            ],
            "total": 42,
            "limit": 50,
            "offset": 0
        }
    """
    if _writer is None or _writer._pool is None:
        raise HTTPException(
            status_code=503,
            detail={"error": "persistence_unavailable", "message": "Event persistence not available"},
        )

    try:
        async with _writer._pool.acquire() as conn:
            # Get total count
            total_row = await conn.fetchrow(
                "SELECT COUNT(*) as count FROM session_events WHERE session_id = $1",
                session_id,
            )
            total = total_row["count"] if total_row else 0

            # Get paginated events
            rows = await conn.fetch(
                """
                SELECT id, session_id, seq, ts, event_type, payload
                FROM session_events
                WHERE session_id = $1
                ORDER BY seq ASC
                LIMIT $2 OFFSET $3
                """,
                session_id,
                limit,
                offset,
            )

            events = [
                {
                    "id": row["id"],
                    "session_id": row["session_id"],
                    "seq": row["seq"],
                    "ts": row["ts"].isoformat() if row["ts"] else None,
                    "event_type": row["event_type"],
                    "payload": row["payload"],
                }
                for row in rows
            ]

            return {
                "events": events,
                "total": total,
                "limit": limit,
                "offset": offset,
            }
    except Exception as e:
        logger.error(f"Failed to fetch events for {session_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "fetch_failed", "message": str(e)},
        ) from e
