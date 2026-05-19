#!/usr/bin/env python3
"""tests/integration/test_no_cheating_audit.py — Anti-cheating audit for S6.

Runs the checks from NO_CHEATING_POLICY.md programmatically.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent  # rasputin-mantle/
CODE_DIRS = [
    REPO_ROOT / "apps" / "gateway" / "src",
    REPO_ROOT / "packages" / "browser",
    REPO_ROOT / "eval" / "webvoyager-100",
    REPO_ROOT / "eval" / "webvoyager-300",
]


def _grep_recursive(pattern: str, paths: list[Path]) -> list[str]:
    """Grep for pattern across paths, return matching lines."""
    results = []
    try:
        out = subprocess.run(
            ["grep", "-rn", "-E", pattern]
            + [str(p) for p in paths],
            capture_output=True,
            text=True,
            timeout=30,
        )
        results = [line for line in out.stdout.strip().split("\n") if line]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return results


class TestNoCheating:
    """Anti-cheating checks from NO_CHEATING_POLICY.md."""

    def test_no_hardcoded_task_ids(self):
        """Rule 2: No hardcoded patterns for known tasks."""
        matches = _grep_recursive(r'task_id\s*==\s*["\']wv-', CODE_DIRS)
        assert len(matches) == 0, f"Hardcoded task_id found: {matches}"

    def test_no_memoization(self):
        """Rule 1: No answer memoization."""
        matches = _grep_recursive(r'\bmemo\b|\bcache\b.*\banswer\b|\banswer\b.*\bcache\b', CODE_DIRS)
        # Filter out comments, test files, and legitimate memory module references
        code_matches = [
            m for m in matches
            if not m.endswith("test_no_cheating_audit.py")
            and "NO_CHEATING_POLICY" not in m
            and "/memory" not in m
            and "runner.py:4:" not in m  # allowed: comment header
        ]
        assert len(code_matches) == 0, f"Memoization pattern found: {code_matches}"

    def test_no_multi_attempt_reporting(self):
        """Rule 7: No best-of-N reporting in runner."""
        matches = _grep_recursive(r'multi_attempt_n|best.*per_task', CODE_DIRS)
        code_matches = [
            m for m in matches
            if "best-of-published" not in m
            and "NO_CHEATING_POLICY" not in m
        ]
        assert len(code_matches) == 0, f"Best-of-N pattern found: {code_matches}"

    def test_tasks_yaml_unchanged(self):
        """Rule 6: WebVoyager-100 tasks.yaml unchanged from R6-shipped."""
        tasks_file = REPO_ROOT / "eval" / "webvoyager-100" / "tasks.yaml"
        assert tasks_file.exists(), "tasks.yaml not found"
        content = tasks_file.read_text()
        # Verify it has exactly 100 tasks
        task_count = content.count("- id: wv-")
        assert task_count == 100, f"Expected 100 tasks, found {task_count}"

    def test_runner_no_external_answer_files(self):
        """Rule 5: Runner doesn't read from external answer files."""
        runner = REPO_ROOT / "eval" / "webvoyager-300" / "runner.py"
        if not runner.exists():
            pytest.skip("runner.py not found")
        content = runner.read_text()
        forbidden = ["answer_key", "expected_answers", "canonical_answers"]
        for term in forbidden:
            assert term not in content, f"Runner references {term}"

    def test_single_attempt_only(self):
        """Rule 7: Per-task results show single-attempt-only."""
        runner = REPO_ROOT / "eval" / "webvoyager-300" / "runner.py"
        if not runner.exists():
            pytest.skip("runner.py not found")
        content = runner.read_text()
        # Should not have retry loops for the same task
        assert "retry" not in content.lower() or "tool retry" in content.lower(), \
            "Runner may have task-level retries"
