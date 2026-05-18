from __future__ import annotations

import json
import subprocess
from pathlib import Path, PurePosixPath

import magic
from fastapi import APIRouter, HTTPException

from gateway.routes.sessions import store

router = APIRouter()


@router.get("/api/sandbox/{session_id}/files")
async def list_sandbox_files(session_id: str, path: str = "/") -> dict[str, list[dict[str, object]]]:
    root = _sandbox_root(session_id)
    target = _safe_target(root, path)
    if not target.exists():
        raise HTTPException(status_code=404, detail={"error": "path_not_found", "message": "Path not found"})
    if not target.is_dir():
        raise HTTPException(status_code=400, detail={"error": "not_a_directory", "message": "Path is not a directory"})
    return {
        "files": [
            _entry_to_dict(entry)
            for entry in sorted(target.iterdir(), key=lambda item: (not item.is_dir(), item.name.lower()))
        ]
    }


@router.get("/api/sandbox/{session_id}/files/{path:path}")
async def get_sandbox_file(session_id: str, path: str) -> dict[str, object]:
    root = _sandbox_root(session_id)
    target = _safe_target(root, path)
    if not target.exists():
        raise HTTPException(status_code=404, detail={"error": "path_not_found", "message": "Path not found"})
    if not target.is_file():
        raise HTTPException(status_code=400, detail={"error": "not_a_file", "message": "Path is not a file"})
    data = target.read_bytes()
    return {"content": data.decode("utf-8", errors="replace"), "mime": _detect_mime(data), "size": len(data)}


def _sandbox_root(session_id: str) -> Path:
    session = store.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail={"error": "session_not_found", "message": "Session not found"})
    if session.sandbox_id is None:
        raise HTTPException(status_code=500, detail={"error": "no_sandbox", "message": "Session has no sandbox"})

    volume_name = f"mantle-work-{session.sandbox_id}"
    root = _docker_volume_mountpoint(volume_name)
    if root is None:
        root = Path("/var/lib/docker/volumes") / volume_name / "_data"
    root = root.resolve()
    if not root.exists() or not root.is_dir():
        raise HTTPException(
            status_code=404,
            detail={"error": "sandbox_root_not_found", "message": "Sandbox volume mount not found"},
        )
    return root


def _docker_volume_mountpoint(volume_name: str) -> Path | None:
    try:
        result = subprocess.run(
            ["docker", "volume", "inspect", volume_name, "--format", "{{json .Mountpoint}}"],
            capture_output=True,
            check=False,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0 or not result.stdout.strip():
        return None
    try:
        return Path(str(json.loads(result.stdout.strip())))
    except json.JSONDecodeError:
        return Path(result.stdout.strip())


def _safe_target(root: Path, requested_path: str) -> Path:
    path = PurePosixPath("/" + requested_path.lstrip("/"))
    if ".." in path.parts:
        raise HTTPException(
            status_code=400,
            detail={"error": "invalid_path", "message": "Path traversal is not allowed"},
        )
    target = (root / path.relative_to("/")).resolve()
    if target != root and root not in target.parents:
        raise HTTPException(status_code=400, detail={"error": "invalid_path", "message": "Path escapes sandbox"})
    return target


def _entry_to_dict(entry: Path) -> dict[str, object]:
    stat = entry.stat()
    return {
        "name": entry.name,
        "type": "directory" if entry.is_dir() else "file",
        "size": stat.st_size,
        "mime": "inode/directory" if entry.is_dir() else _detect_mime(entry.read_bytes()[:2048]),
    }


def _detect_mime(data: bytes) -> str:
    try:
        return str(magic.from_buffer(data, mime=True))
    except Exception:
        return "application/octet-stream"
