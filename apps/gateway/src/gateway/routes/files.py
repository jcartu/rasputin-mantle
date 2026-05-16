from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException

from gateway.config import settings

router = APIRouter()


@router.get("")
async def list_files(path: str = "/") -> list[dict[str, object]]:
    root = Path(settings.files_root).resolve()
    target = _safe_target(root, path)
    if not target.exists():
        raise HTTPException(status_code=404, detail={"error": "path_not_found", "message": "Path not found"})
    if not target.is_dir():
        raise HTTPException(status_code=400, detail={"error": "not_a_directory", "message": "Path is not a directory"})
    return [
        _entry_to_dict(root, entry)
        for entry in sorted(target.iterdir(), key=lambda item: (not item.is_dir(), item.name))
    ]


def _safe_target(root: Path, requested_path: str) -> Path:
    relative = requested_path.lstrip("/")
    target = (root / relative).resolve()
    if target != root and root not in target.parents:
        raise HTTPException(status_code=400, detail={"error": "invalid_path", "message": "Path escapes workspace"})
    return target


def _entry_to_dict(root: Path, entry: Path) -> dict[str, object]:
    stat = entry.stat()
    return {
        "name": entry.name,
        "path": f"/{entry.relative_to(root).as_posix()}",
        "type": "directory" if entry.is_dir() else "file",
        "size": stat.st_size,
        "modified_at": stat.st_mtime,
    }
