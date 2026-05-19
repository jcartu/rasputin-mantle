from __future__ import annotations

from pathlib import Path
from typing import Any

MODEL_NAME = "claude-sonnet-4-6"


def judge_structure(task: dict[str, Any], produced_files: list[Path], metadata: dict[str, Any]) -> dict[str, Any]:
    expected = dict(task.get("expected") or {})
    names = {path.name for path in produced_files}
    required = set(expected.get("files") or ([expected["file"]] if expected.get("file") else []))
    file_match = required.issubset(names)
    structural_match = file_match
    if expected.get("min_slides") is not None:
        structural_match = structural_match and metadata.get("slide_count", 0) >= int(expected["min_slides"])
    if expected.get("min_sheets") is not None:
        structural_match = structural_match and len(metadata.get("sheets", [])) >= int(expected["min_sheets"])
    if expected.get("sheets") is not None:
        structural_match = structural_match and set(expected["sheets"]).issubset(set(metadata.get("sheets", [])))
    if expected.get("formulas"):
        structural_match = structural_match and bool(metadata.get("has_formulas"))
    return {
        "judge_model": MODEL_NAME,
        "file_match": file_match,
        "structural_match": structural_match,
        "score": 1.0 if structural_match else 0.0,
    }
