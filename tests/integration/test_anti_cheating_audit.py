from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SEARCH_ROOTS = [REPO_ROOT / "apps", REPO_ROOT / "packages", REPO_ROOT / "eval"]
SOURCE_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".mjs", ".cjs"}
EXCLUDED_PARTS = {".git", ".venv", "node_modules", "dist", "__pycache__", "tests"}


def _source_files() -> list[Path]:
    files: list[Path] = []
    for root in SEARCH_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.suffix not in SOURCE_SUFFIXES:
                continue
            if not path.is_file():
                continue
            if EXCLUDED_PARTS.intersection(path.relative_to(REPO_ROOT).parts):
                continue
            files.append(path)
    return files


def _matches(needle: str, files: list[Path]) -> list[str]:
    found: list[str] = []
    for path in files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for line_number, line in enumerate(text.splitlines(), start=1):
            if needle in line:
                found.append(f"{path.relative_to(REPO_ROOT)}:{line_number}:{line.strip()}")
    return found


def test_w9_anti_cheating_forbidden_patterns_are_absent() -> None:
    files = _source_files()
    forbidden = {
        'task_id == "wv-': files,
        "task_id == 'wv-": files,
        'task_id == "prod-': files,
        "task_id == 'prod-": files,
        "best_of": files,
        "MockTransport": [path for path in files if path.is_relative_to(REPO_ROOT / "eval")],
    }

    failures = {needle: _matches(needle, scoped_files) for needle, scoped_files in forbidden.items()}
    failures = {needle: matches for needle, matches in failures.items() if matches}

    assert failures == {}
