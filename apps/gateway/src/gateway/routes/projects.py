from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Header, HTTPException, Response, status
from shared.project import (
    ProjectCreateRequest,
    ProjectMemberCreateRequest,
    ProjectMemberSchema,
    ProjectSchema,
    ProjectUpdateRequest,
)

router = APIRouter()
_writer: Any = None


def set_writer(writer: Any) -> None:
    global _writer
    _writer = writer


async def _pool() -> Any:
    if _writer is None or _writer._pool is None:
        raise HTTPException(
            status_code=503,
            detail={"error": "persistence_unavailable", "message": "Project persistence not available"},
        )
    return _writer._pool


def _current_user(x_user_id: str | None) -> str:
    return x_user_id or "local"


def _project(row: Any) -> ProjectSchema:
    allowed_tools = row["allowed_tools"]
    if isinstance(allowed_tools, str):
        allowed_tools = json.loads(allowed_tools)
    return ProjectSchema(
        id=str(row["id"]),
        name=row["name"],
        slug=row["slug"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        owner_id=row["owner_id"],
        visibility=row["visibility"],
        default_planner=row["default_planner"],
        system_prompt_addendum=row["system_prompt_addendum"],
        allowed_tools=list(allowed_tools or []),
    )


def _member(row: Any) -> ProjectMemberSchema:
    return ProjectMemberSchema(
        project_id=str(row["project_id"]),
        user_id=row["user_id"],
        role=row["role"],
        added_at=row["added_at"],
    )


async def _require_project(conn: Any, project_id: str, user_id: str) -> Any:
    row = await conn.fetchrow(
        """
        SELECT p.*
        FROM projects p
        LEFT JOIN project_members m ON m.project_id = p.id AND m.user_id = $2
        WHERE p.id = $1::uuid AND (p.owner_id = $2 OR m.user_id IS NOT NULL)
        """,
        project_id,
        user_id,
    )
    if row is None:
        raise HTTPException(status_code=404, detail={"error": "project_not_found", "message": "Project not found"})
    return row


async def _require_editor(conn: Any, project_id: str, user_id: str) -> Any:
    row = await conn.fetchrow(
        """
        SELECT p.*
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
    return row


@router.get("", response_model=list[ProjectSchema])
async def list_projects(x_user_id: str | None = Header(default=None)) -> list[ProjectSchema]:
    user_id = _current_user(x_user_id)
    pool = await _pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT DISTINCT p.*
            FROM projects p
            LEFT JOIN project_members m ON m.project_id = p.id
            WHERE p.owner_id = $1 OR m.user_id = $1 OR p.visibility = 'public'
            ORDER BY p.updated_at DESC, p.created_at DESC
            """,
            user_id,
        )
    return [_project(row) for row in rows]


@router.post("", response_model=ProjectSchema, status_code=status.HTTP_201_CREATED)
async def create_project(
    request: ProjectCreateRequest,
    x_user_id: str | None = Header(default=None),
) -> ProjectSchema:
    user_id = _current_user(x_user_id)
    pool = await _pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            try:
                row = await conn.fetchrow(
                    """
                    INSERT INTO projects (
                        name, slug, owner_id, visibility, default_planner, system_prompt_addendum, allowed_tools
                    )
                    VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb)
                    RETURNING *
                    """,
                    request.name,
                    request.slug,
                    user_id,
                    request.visibility,
                    request.default_planner,
                    request.system_prompt_addendum,
                    json.dumps(request.allowed_tools),
                )
            except Exception as exc:
                raise HTTPException(
                    status_code=409,
                    detail={"error": "project_slug_conflict", "message": "Project slug is already in use"},
                ) from exc
            await conn.execute(
                """
                INSERT INTO project_members (project_id, user_id, role)
                VALUES ($1, $2, 'owner')
                ON CONFLICT (project_id, user_id) DO UPDATE SET role = 'owner'
                """,
                row["id"],
                user_id,
            )
    return _project(row)


@router.get("/{project_id}", response_model=ProjectSchema)
async def get_project(project_id: str, x_user_id: str | None = Header(default=None)) -> ProjectSchema:
    user_id = _current_user(x_user_id)
    pool = await _pool()
    async with pool.acquire() as conn:
        row = await _require_project(conn, project_id, user_id)
    return _project(row)


@router.patch("/{project_id}", response_model=ProjectSchema)
async def update_project(
    project_id: str,
    request: ProjectUpdateRequest,
    x_user_id: str | None = Header(default=None),
) -> ProjectSchema:
    user_id = _current_user(x_user_id)
    pool = await _pool()
    async with pool.acquire() as conn:
        await _require_editor(conn, project_id, user_id)
        try:
            row = await conn.fetchrow(
                """
                UPDATE projects
                SET name = COALESCE($2, name),
                    slug = COALESCE($3, slug),
                    visibility = COALESCE($4, visibility),
                    default_planner = COALESCE($5, default_planner),
                    system_prompt_addendum = COALESCE($6, system_prompt_addendum),
                    allowed_tools = COALESCE($7::jsonb, allowed_tools),
                    updated_at = now()
                WHERE id = $1::uuid
                RETURNING *
                """,
                project_id,
                request.name,
                request.slug,
                request.visibility,
                request.default_planner,
                request.system_prompt_addendum,
                json.dumps(request.allowed_tools) if request.allowed_tools is not None else None,
            )
        except Exception as exc:
            raise HTTPException(
                status_code=409,
                detail={"error": "project_slug_conflict", "message": "Project slug is already in use"},
            ) from exc
    return _project(row)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: str, x_user_id: str | None = Header(default=None)) -> Response:
    user_id = _current_user(x_user_id)
    pool = await _pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT owner_id FROM projects WHERE id = $1::uuid", project_id)
        if row is None:
            raise HTTPException(status_code=404, detail={"error": "project_not_found", "message": "Project not found"})
        if row["owner_id"] != user_id:
            raise HTTPException(
                status_code=403, detail={"error": "project_forbidden", "message": "Project owner required"}
            )
        await conn.execute("DELETE FROM projects WHERE id = $1::uuid", project_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{project_id}/members", response_model=list[ProjectMemberSchema])
async def list_members(project_id: str, x_user_id: str | None = Header(default=None)) -> list[ProjectMemberSchema]:
    user_id = _current_user(x_user_id)
    pool = await _pool()
    async with pool.acquire() as conn:
        await _require_project(conn, project_id, user_id)
        rows = await conn.fetch(
            """
            SELECT project_id, user_id, role, added_at
            FROM project_members
            WHERE project_id = $1::uuid
            ORDER BY added_at ASC
            """,
            project_id,
        )
    return [_member(row) for row in rows]


@router.post("/{project_id}/members", response_model=ProjectMemberSchema, status_code=status.HTTP_201_CREATED)
async def add_member(
    project_id: str,
    request: ProjectMemberCreateRequest,
    x_user_id: str | None = Header(default=None),
) -> ProjectMemberSchema:
    user_id = _current_user(x_user_id)
    pool = await _pool()
    async with pool.acquire() as conn:
        await _require_editor(conn, project_id, user_id)
        row = await conn.fetchrow(
            """
            INSERT INTO project_members (project_id, user_id, role)
            VALUES ($1::uuid, $2, $3)
            ON CONFLICT (project_id, user_id) DO UPDATE SET role = EXCLUDED.role
            RETURNING project_id, user_id, role, added_at
            """,
            project_id,
            request.user_id,
            request.role,
        )
    return _member(row)


@router.delete("/{project_id}/members/{member_user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    project_id: str,
    member_user_id: str,
    x_user_id: str | None = Header(default=None),
) -> Response:
    user_id = _current_user(x_user_id)
    pool = await _pool()
    async with pool.acquire() as conn:
        await _require_editor(conn, project_id, user_id)
        owner = await conn.fetchval("SELECT owner_id FROM projects WHERE id = $1::uuid", project_id)
        if owner == member_user_id:
            raise HTTPException(
                status_code=400,
                detail={"error": "owner_remove_forbidden", "message": "Project owner cannot be removed"},
            )
        await conn.execute(
            "DELETE FROM project_members WHERE project_id = $1::uuid AND user_id = $2", project_id, member_user_id
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
