from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any

from sandbox.backend import SandboxBackend, create_backend


@dataclass
class CodeActResult:
    stdout: str
    stderr: str
    results: list[Any]
    files_changed: list[str]
    duration_ms: int
    exit_code: int


SNAPSHOT_CODE = r'''
from __future__ import annotations

import hashlib
import json
from pathlib import Path

root = Path("/workspace")
snapshot: dict[str, str] = {}
for path in sorted(root.rglob("*")):
    if not path.is_file() or path.name == ".codeact_tmp.py":
        continue
    snapshot[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
print(json.dumps(snapshot, sort_keys=True))
'''


def _snapshot_workspace(backend: SandboxBackend, session_id: str) -> dict[str, str]:
    result = backend.exec_code(session_id, SNAPSHOT_CODE)
    if result.exit_code != 0:
        raise RuntimeError(f"Failed to snapshot sandbox workspace: {result.stderr}")
    loaded = json.loads(result.stdout or "{}")
    if not isinstance(loaded, dict):
        raise RuntimeError("Sandbox workspace snapshot was not an object")
    return {str(path): str(digest) for path, digest in loaded.items()}


def _diff_snapshots(before: dict[str, str], after: dict[str, str]) -> list[str]:
    return sorted(path for path in set(before) | set(after) if before.get(path) != after.get(path))


def _parse_results(stdout: str) -> list[Any]:
    marker = "__MANTLE_RESULT__="
    results: list[Any] = []
    for line in stdout.splitlines():
        if line.startswith(marker):
            results.append(json.loads(line[len(marker) :]))
    return results


async def execute_code(code: str, language: str = "python") -> CodeActResult:
    if language != "python":
        raise ValueError(f"Unsupported CodeAct language: {language}")

    backend = create_backend()
    started_at = time.monotonic()
    session_id: str | None = None

    try:
        session_id = backend.create()
        before = _snapshot_workspace(backend, session_id)
        exec_result = backend.exec_code(session_id, code)
        after = _snapshot_workspace(backend, session_id)
        return CodeActResult(
            stdout=exec_result.stdout,
            stderr=exec_result.stderr,
            results=_parse_results(exec_result.stdout),
            files_changed=_diff_snapshots(before, after),
            duration_ms=int((time.monotonic() - started_at) * 1000),
            exit_code=exec_result.exit_code,
        )
    finally:
        if session_id is not None:
            backend.destroy(session_id)
