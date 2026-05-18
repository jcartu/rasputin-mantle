from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter()
_writer: Any = None

SECRET_KEY_PARTS = (
    "api_key",
    "apikey",
    "authorization",
    "auth_token",
    "access_token",
    "refresh_token",
    "credential",
    "credentials",
    "password",
    "secret",
    "token",
    "cookie",
    "sandbox_credential",
)


class SharePatchRequest(BaseModel):
    share_public: bool = Field(..., description="Whether the replay is publicly visible")
    expires_at: datetime | None = Field(default=None, description="Optional public link expiry")


def set_writer(writer: Any) -> None:
    global _writer
    _writer = writer


def _is_secret_key(key: str) -> bool:
    normalized = key.lower().replace("-", "_")
    return any(part in normalized for part in SECRET_KEY_PARTS)


def sanitize_share_value(value: Any) -> Any:
    if isinstance(value, dict):
        clean: dict[str, Any] = {}
        for key, nested in value.items():
            if _is_secret_key(str(key)):
                continue
            clean[str(key)] = sanitize_share_value(nested)
        return clean
    if isinstance(value, list):
        return [sanitize_share_value(item) for item in value]
    return value


def _extract_data(payload: dict[str, Any]) -> dict[str, Any]:
    data = payload.get("data")
    if isinstance(data, dict):
        return data
    nested = payload.get("payload")
    if isinstance(nested, dict):
        nested_data = nested.get("data")
        if isinstance(nested_data, dict):
            return nested_data
    return {}


def _extract_final_answer(steps: list[dict[str, Any]]) -> str | None:
    for step in reversed(steps):
        if step.get("event_type") != "completion":
            continue
        data = _extract_data(step.get("payload", {}))
        for key in ("final_answer", "answer", "message", "content", "text"):
            value = data.get(key)
            if isinstance(value, str) and value.strip():
                return value
    return None


async def _pool() -> Any:
    if _writer is None or _writer._pool is None:
        raise HTTPException(
            status_code=503,
            detail={"error": "persistence_unavailable", "message": "Event persistence not available"},
        )
    return _writer._pool


async def _table_has_column(conn: Any, table_name: str, column_name: str) -> bool:
    row = await conn.fetchrow(
        """
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = $1 AND column_name = $2
        LIMIT 1
        """,
        table_name,
        column_name,
    )
    return row is not None


async def _public_share_row(conn: Any, session_id: str) -> Any | None:
    row = await conn.fetchrow(
        """
        SELECT session_id, public, expires_at, created_at
        FROM share_tokens
        WHERE session_id = $1
          AND public = true
          AND (expires_at IS NULL OR expires_at > now())
        ORDER BY created_at DESC
        LIMIT 1
        """,
        session_id,
    )
    if row is not None:
        return row

    has_share_public = await _table_has_column(conn, "sessions", "share_public")
    if not has_share_public:
        return None
    try:
        return await conn.fetchrow(
            """
            SELECT id AS session_id, share_public AS public, NULL::timestamptz AS expires_at, created_at
            FROM sessions
            WHERE id = $1 AND share_public = true
            LIMIT 1
            """,
            session_id,
        )
    except Exception:
        logger.debug("sessions table share_public check failed", exc_info=True)
        return None


@router.get("/{session_id}")
async def get_public_share(session_id: str) -> dict[str, Any]:
    pool = await _pool()
    async with pool.acquire() as conn:
        share_row = await _public_share_row(conn, session_id)
        if share_row is None:
            raise HTTPException(
                status_code=404,
                detail={"error": "share_not_found", "message": "Session is not public"},
            )

        rows = await conn.fetch(
            """
            SELECT seq, ts, event_type, payload
            FROM session_events
            WHERE session_id = $1
            ORDER BY seq ASC
            """,
            session_id,
        )

    steps = [
        {
            "index": index,
            "seq": row["seq"],
            "timestamp": row["ts"].isoformat() if row["ts"] else None,
            "event_type": row["event_type"],
            "payload": sanitize_share_value(row["payload"]),
        }
        for index, row in enumerate(rows)
    ]
    final_answer = _extract_final_answer(steps)
    return {
        "session": {
            "session_id": session_id,
            "share_public": True,
            "expires_at": share_row["expires_at"].isoformat() if share_row["expires_at"] else None,
        },
        "steps": steps,
        "final_answer": final_answer,
    }


@router.patch("/{session_id}")
async def update_share(session_id: str, request: SharePatchRequest) -> dict[str, Any]:
    pool = await _pool()
    expires_at = request.expires_at
    if expires_at is not None and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO share_tokens (id, session_id, expires_at, public)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (id) DO UPDATE SET
              expires_at = EXCLUDED.expires_at,
              public = EXCLUDED.public
            """,
            session_id,
            session_id,
            expires_at,
            request.share_public,
        )
        if await _table_has_column(conn, "sessions", "share_public"):
            try:
                await conn.execute(
                    "UPDATE sessions SET share_public = $2 WHERE id = $1",
                    session_id,
                    request.share_public,
                )
            except Exception:
                logger.debug("sessions.share_public update skipped", exc_info=True)

    return {
        "session_id": session_id,
        "share_public": request.share_public,
        "expires_at": expires_at.isoformat() if expires_at else None,
    }
