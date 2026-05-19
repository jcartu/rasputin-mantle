from __future__ import annotations

import sys
import uuid
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
for package_path in (ROOT / "packages" / "shared", ROOT / "packages" / "scheduler"):
    sys.path.insert(0, str(package_path))


class _Acquire:
    def __init__(self, conn: "_ProjectConn") -> None:
        self._conn = conn

    async def __aenter__(self) -> "_ProjectConn":
        return self._conn

    async def __aexit__(self, *_exc: object) -> None:
        return None


class _Pool:
    def __init__(self, conn: "_ProjectConn") -> None:
        self._conn = conn

    def acquire(self) -> _Acquire:
        return _Acquire(self._conn)


class _Writer:
    def __init__(self, conn: "_ProjectConn") -> None:
        self._pool = _Pool(conn)


class _ProjectConn:
    def __init__(self, project_id: str) -> None:
        self.project_id = project_id
        self.kb_fetches = 0

    async def fetchrow(self, query: str, *args: Any) -> dict[str, Any] | None:
        if "SELECT * FROM projects" in query:
            assert str(args[0]) == self.project_id
            return {
                "id": self.project_id,
                "default_planner": "gpt-5.5",
                "system_prompt_addendum": "project-only addendum",
                "allowed_tools": [],
            }
        raise AssertionError(f"Unexpected fetchrow query: {query}")

    async def fetch(self, query: str, *args: Any) -> list[dict[str, str]]:
        self.kb_fetches += 1
        raise AssertionError("Project KB rows should not be fetched in eval mode")


class _Backend:
    def __init__(self) -> None:
        self.writes: list[tuple[str, str, bytes, bool]] = []

    def create(self) -> str:
        return "sandbox-eval"

    def destroy(self, sandbox_id: str) -> None:
        return None

    def write_bytes(self, sandbox_id: str, target: str, data: bytes, read_only: bool = False) -> None:
        self.writes.append((sandbox_id, target, data, read_only))


def _write_skill(path: Path, name: str, description: str) -> None:
    skill_dir = path / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        f"""---
name: {name}
description: {description}
when_to_use: Use this skill in eval-mode tests.
capability: test
version: 1.0.0
license: MIT
---

# {name}
""",
        encoding="utf-8",
    )


def test_is_eval_mode_accepts_enabled_values(monkeypatch: pytest.MonkeyPatch) -> None:
    from gateway.eval_mode import is_eval_mode

    monkeypatch.setenv("MANTLE_EVAL_MODE", "1")
    assert is_eval_mode() is True


def test_scheduler_is_not_started_in_eval_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    from scheduler.jobs import init_scheduler

    monkeypatch.setenv("MANTLE_EVAL_MODE", "1")

    scheduler = init_scheduler("redis://127.0.0.1:6379/0?jobs_key=eval.jobs&run_times_key=eval.run_times")

    assert scheduler.running is False


def test_skill_rediscovery_is_skipped_in_eval_mode(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from codeact import skills_loader

    skills_loader.invalidate_session_cache()
    _write_skill(tmp_path, "cached-skill", "Original description")

    first = skills_loader.discover_skills(search_paths=[tmp_path])
    assert [skill.description for skill in first] == ["Original description"]

    (tmp_path / "cached-skill" / "SKILL.md").write_text("changed", encoding="utf-8")


    def fail_signature(paths: list[Path], session_id: str | None) -> str:
        raise AssertionError("signature scan should be skipped in eval mode when cache is warm")

    monkeypatch.setenv("MANTLE_EVAL_MODE", "1")
    monkeypatch.setattr(skills_loader, "_signature", fail_signature)

    second = skills_loader.discover_skills(search_paths=[tmp_path])
    assert [skill.description for skill in second] == ["Original description"]


@pytest.mark.asyncio
async def test_project_kb_lazy_mount_is_skipped_in_eval_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    from gateway.routes import sessions
    from gateway.sessions import SessionStore

    project_id = str(uuid.uuid4())
    conn = _ProjectConn(project_id)
    backend = _Backend()

    monkeypatch.setenv("MANTLE_EVAL_MODE", "1")
    monkeypatch.setattr(sessions, "_writer", _Writer(conn))
    monkeypatch.setattr(sessions, "store", SessionStore())
    monkeypatch.setattr(sessions, "create_backend", lambda: backend)

    info = await sessions.create_session(sessions.SessionCreateRequest(project_id=project_id))

    assert info.project_id == project_id
    assert info.kb_index == []
    assert info.system_prompt_addendum == "project-only addendum"
    assert conn.kb_fetches == 0
    assert backend.writes == []
