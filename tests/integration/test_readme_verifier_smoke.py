"""Smoke test for scripts/verify-readme-claims.py (W0 ticket 1)."""

import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFY_SCRIPT = REPO_ROOT / "scripts" / "verify-readme-claims.py"
README = REPO_ROOT / "README.md"


def test_verify_script_exists():
    """scripts/verify-readme-claims.py must exist and be executable."""
    assert VERIFY_SCRIPT.exists(), "verify-readme-claims.py not found"
    assert VERIFY_SCRIPT.stat().st_mode & 0o111, "verify-readme-claims.py not executable"


def test_verify_script_syntax():
    """The script must parse as valid Python."""
    code = VERIFY_SCRIPT.read_text()
    compile(code, str(VERIFY_SCRIPT), "exec")


def test_readme_verifier_exits_zero():
    """Running verify-readme-claims.py README.md must exit 0."""
    result = subprocess.run(
        [sys.executable, str(VERIFY_SCRIPT), str(README)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, (
        f"verify-readme-claims.py failed (exit {result.returncode}):\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


def test_readme_verifier_output_has_summary():
    """The script output must contain a summary line."""
    result = subprocess.run(
        [sys.executable, str(VERIFY_SCRIPT), str(README)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    assert "Summary:" in result.stdout, (
        f"Expected 'Summary:' in output, got:\n{result.stdout}"
    )
    assert "passed" in result.stdout, (
        f"Expected 'passed' in output, got:\n{result.stdout}"
    )
