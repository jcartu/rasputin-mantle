from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient
from gateway.config import settings
from gateway.routes import project_kb, projects


class _Transaction:
    async def __aenter__(self) -> None:
        return None

    async def __aexit__(self, *_exc: object) -> None:
        return None


class _Acquire:
    def __init__(self, conn: "_ProjectConn") -> None:
        self._conn = conn

    async def __aenter__(self) -> "_ProjectConn":
        return self._conn

    async def __aexit__(self, *_exc: object) -> None:
        return None


class _ProjectPool:
    def __init__(self, conn: "_ProjectConn") -> None:
        self._conn = conn

    def acquire(self) -> _Acquire:
        return _Acquire(self._conn)


class _ProjectWriter:
    def __init__(self, conn: "_ProjectConn") -> None:
        self._pool = _ProjectPool(conn)


class _ProjectConn:
    def __init__(self) -> None:
        self.projects: dict[str, dict[str, Any]] = {}
        self.kb_files: list[dict[str, Any]] = []

    def transaction(self) -> _Transaction:
        return _Transaction()

    async def fetchrow(self, query: str, *args: Any) -> dict[str, Any] | None:
        now = datetime.now(timezone.utc)
        if "INSERT INTO projects" in query:
            project_id = str(uuid.uuid4())
            row = {
                "id": project_id,
                "name": args[0],
                "slug": args[1],
                "owner_id": args[2],
                "visibility": args[3],
                "default_planner": args[4],
                "system_prompt_addendum": args[5],
                "allowed_tools": args[6],
                "created_at": now,
                "updated_at": now,
            }
            self.projects[project_id] = row
            return row
        if "FROM projects p" in query and "m.role IN ('owner', 'editor')" in query:
            row = self.projects.get(str(args[0]))
            if row is None or row["owner_id"] != args[1]:
                return None
            return {"id": row["id"]}
        if "COUNT(*)::int AS file_count" in query:
            project_id = str(args[0])
            files = [item for item in self.kb_files if item["project_id"] == project_id]
            return {
                "file_count": len(files),
                "total_bytes": sum(int(item["size_bytes"]) for item in files),
            }
        if "INSERT INTO project_kb_files" in query:
            row = {
                "id": len(self.kb_files) + 1,
                "project_id": str(args[0]),
                "filename": args[1],
                "mime_type": args[2],
                "size_bytes": args[3],
                "sha256": args[4],
                "storage_path": args[5],
                "uploaded_at": now,
            }
            self.kb_files.append(row)
            return row
        raise AssertionError(f"Unexpected fetchrow query: {query}")

    async def execute(self, query: str, *args: Any) -> str:
        if "INSERT INTO project_members" in query:
            return "INSERT 0 1"
        raise AssertionError(f"Unexpected execute query: {query}")


def test_project_kb_upload_rejects_traversal_and_stores_read_only(tmp_path: Path, monkeypatch: Any) -> None:
    kb_root = tmp_path / "kb-root"
    monkeypatch.setattr(settings, "kb_root", str(kb_root))

    conn = _ProjectConn()
    writer = _ProjectWriter(conn)
    projects.set_writer(writer)
    project_kb.set_writer(writer)
    test_app = FastAPI()
    test_app.include_router(projects.router, prefix="/api/projects")
    test_app.include_router(project_kb.router, prefix="/api/projects")
    client = TestClient(test_app)

    created = client.post(
        "/api/projects",
        json={"name": "Security KB", "slug": f"security-kb-{uuid.uuid4().hex[:8]}"},
        headers={"x-user-id": "security-user"},
    )
    assert created.status_code == 201
    project_id = created.json()["id"]

    uploaded = client.post(
        f"/api/projects/{project_id}/kb",
        files={"file": ("notes.txt", b"safe project knowledge", "text/plain")},
        headers={"x-user-id": "security-user"},
    )
    assert uploaded.status_code == 201
    kb_file = uploaded.json()
    stored_path = (kb_root / project_id / "kb" / kb_file["storage_path"]).resolve()

    assert stored_path.read_bytes() == b"safe project knowledge"
    assert stored_path.is_relative_to(kb_root.resolve())
    assert stored_path.stat().st_mode & 0o777 == 0o444

    for filename in ("../../../etc/passwd", "....//....//etc/passwd"):
        rejected = client.post(
            f"/api/projects/{project_id}/kb",
            files={"file": (filename, b"malicious", "text/plain")},
            headers={"x-user-id": "security-user"},
        )
        assert rejected.status_code == 400

    assert not (tmp_path / "etc" / "passwd").exists()
    assert not Path("/etc/passwd").is_relative_to(kb_root.resolve())
    assert os.access(stored_path, os.R_OK)
