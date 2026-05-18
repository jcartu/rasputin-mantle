from __future__ import annotations

import asyncio
import hashlib
import re
from pathlib import Path, PurePosixPath
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, File, Header, HTTPException, Response, UploadFile, status
from shared.project import KBFileSchema

from gateway.config import settings

router = APIRouter()
_writer: Any = None

MAX_KB_FILES = 50
MAX_KB_BYTES = 100 * 1024 * 1024


def set_writer(writer: Any) -> None:
    global _writer
    _writer = writer


async def _pool() -> Any:
    if _writer is None or _writer._pool is None:
        raise HTTPException(
            status_code=503,
            detail={"error": "persistence_unavailable", "message": "Project KB persistence not available"},
        )
    return _writer._pool


def _current_user(x_user_id: str | None) -> str:
    return x_user_id or "local"


def _kb_file(row: Any) -> KBFileSchema:
    return KBFileSchema(
        id=row["id"],
        project_id=str(row["project_id"]),
        filename=row["filename"],
        mime_type=row["mime_type"],
        size_bytes=row["size_bytes"],
        sha256=row["sha256"],
        uploaded_at=row["uploaded_at"],
        storage_path=row["storage_path"],
    )


def _safe_filename(filename: str) -> str:
    name = PurePosixPath(filename).name.strip()
    if not name or name in {".", ".."}:
        raise HTTPException(status_code=400, detail={"error": "invalid_filename", "message": "File name is invalid"})
    return re.sub(r"[^A-Za-z0-9._ -]", "_", name)[:180]


def _safe_project_kb_dir(project_id: str) -> Path:
    root = Path(settings.kb_root).resolve()
    target = (root / project_id / "kb").resolve()
    if root != target and root not in target.parents:
        raise HTTPException(
            status_code=400, detail={"error": "invalid_project_path", "message": "Project path is invalid"}
        )
    return target


async def _require_project(conn: Any, project_id: str, user_id: str) -> None:
    row = await conn.fetchrow(
        """
        SELECT p.id
        FROM projects p
        LEFT JOIN project_members m ON m.project_id = p.id AND m.user_id = $2
        WHERE p.id = $1::uuid AND (p.owner_id = $2 OR m.user_id IS NOT NULL)
        """,
        project_id,
        user_id,
    )
    if row is None:
        raise HTTPException(status_code=404, detail={"error": "project_not_found", "message": "Project not found"})


async def _require_editor(conn: Any, project_id: str, user_id: str) -> None:
    row = await conn.fetchrow(
        """
        SELECT p.id
        FROM projects p
        LEFT JOIN project_members m ON m.project_id = p.id AND m.user_id = $2
        WHERE p.id = $1::uuid AND (p.owner_id = $2 OR m.role IN ('owner', 'editor'))
        """,
        project_id,
        user_id,
    )
    if row is None:
        raise HTTPException(
            status_code=403, detail={"error": "project_forbidden", "message": "Project editor access required"}
        )


@router.post("/{project_id}/kb", response_model=KBFileSchema, status_code=status.HTTP_201_CREATED)
async def upload_kb_file(
    project_id: str,
    file: UploadFile = File(...),
    x_user_id: str | None = Header(default=None),
) -> KBFileSchema:
    user_id = _current_user(x_user_id)
    data = await file.read()
    size = len(data)
    pool = await _pool()

    async with pool.acquire() as conn:
        await _require_editor(conn, project_id, user_id)
        stats = await conn.fetchrow(
            """
            SELECT COUNT(*)::int AS file_count, COALESCE(SUM(size_bytes), 0)::bigint AS total_bytes
            FROM project_kb_files
            WHERE project_id = $1::uuid
            """,
            project_id,
        )
        file_count = int(stats["file_count"])
        total_bytes = int(stats["total_bytes"])
        if file_count >= MAX_KB_FILES:
            raise HTTPException(
                status_code=413, detail={"error": "kb_file_limit", "message": "Project KB file limit exceeded"}
            )
        if total_bytes + size > MAX_KB_BYTES:
            raise HTTPException(
                status_code=413, detail={"error": "kb_size_limit", "message": "Project KB size cap exceeded"}
            )

        original = _safe_filename(file.filename or "upload.bin")
        storage_name = f"{uuid4().hex}-{original}"
        storage_path = storage_name
        target_dir = _safe_project_kb_dir(project_id)
        target = target_dir / storage_name
        digest = hashlib.sha256(data).hexdigest()

        await asyncio.to_thread(target_dir.mkdir, parents=True, exist_ok=True)
        await asyncio.to_thread(target.write_bytes, data)
        await asyncio.to_thread(target.chmod, 0o444)

        row = await conn.fetchrow(
            """
            INSERT INTO project_kb_files (project_id, filename, mime_type, size_bytes, sha256, storage_path)
            VALUES ($1::uuid, $2, $3, $4, $5, $6)
            RETURNING id, project_id, filename, mime_type, size_bytes, sha256, uploaded_at, storage_path
            """,
            project_id,
            original,
            file.content_type,
            size,
            digest,
            storage_path,
        )
    return _kb_file(row)


@router.get("/{project_id}/kb", response_model=list[KBFileSchema])
async def list_kb_files(project_id: str, x_user_id: str | None = Header(default=None)) -> list[KBFileSchema]:
    user_id = _current_user(x_user_id)
    pool = await _pool()
    async with pool.acquire() as conn:
        await _require_project(conn, project_id, user_id)
        rows = await conn.fetch(
            """
            SELECT id, project_id, filename, mime_type, size_bytes, sha256, uploaded_at, storage_path
            FROM project_kb_files
            WHERE project_id = $1::uuid
            ORDER BY uploaded_at DESC
            """,
            project_id,
        )
    return [_kb_file(row) for row in rows]


@router.delete("/{project_id}/kb/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_kb_file(
    project_id: str,
    file_id: int,
    x_user_id: str | None = Header(default=None),
) -> Response:
    user_id = _current_user(x_user_id)
    pool = await _pool()
    async with pool.acquire() as conn:
        await _require_editor(conn, project_id, user_id)
        row = await conn.fetchrow(
            """
            DELETE FROM project_kb_files
            WHERE project_id = $1::uuid AND id = $2
            RETURNING storage_path
            """,
            project_id,
            file_id,
        )
    if row is None:
        raise HTTPException(status_code=404, detail={"error": "kb_file_not_found", "message": "KB file not found"})
    target = _safe_project_kb_dir(project_id) / row["storage_path"]
    if target.exists():
        await asyncio.to_thread(target.unlink)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
