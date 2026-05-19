#!/usr/bin/env python3
"""Verify that .env.example documents every env var used in the codebase.

Scans apps/, packages/, scripts/ for env var access patterns.
Compares found vars against .env.example keys.
Exit 0 if all code vars are documented. Exit 1 if any are missing.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_EXAMPLE = ROOT / ".env.example"

PATTERNS = [
    (r"os\.environ\.get\(\s*['\"](\w+)['\"]", re.IGNORECASE),
    (r"os\.getenv\(\s*['\"](\w+)['\"]", re.IGNORECASE),
    (r"os\.environ\[\s*['\"](\w+)['\"]", re.IGNORECASE),
    (r"process\.env\.(\w+)", 0),
    (r"import\.meta\.env\.(\w+)", 0),
]

EXCLUDE_VARS = {
    "PATH", "HOME", "USER", "LANG", "TERM", "SHELL", "EDITOR",
    "HOSTNAME", "PWD", "OLDPWD", "SHLVL", "LC_ALL", "LC_CTYPE",
    "PYTHONPATH", "PYTHONIOENCODING", "PIP_NO_INPUT", "NODE_ENV",
    "npm_config_yes", "CI", "GITHUB_ACTIONS", "npm_lifecycle_event",
    "CUDA_VISIBLE_DEVICES", "npm_lifecycle_event",
}

EXCLUDE_DIRS = {
    ".git", ".next", "node_modules", "__pycache__", ".venv", "venv",
    "playwright-report", "test-results", ".opencode", "_venv",
}


def find_env_vars_in_code() -> set[str]:
    found = set()
    scan_dirs = [ROOT / "apps", ROOT / "packages", ROOT / "scripts"]
    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for ext in ("*.py", "*.ts", "*.tsx", "*.js", "*.jsx"):
            for f in scan_dir.rglob(ext):
                if any(excl in f.parts for excl in EXCLUDE_DIRS):
                    continue
                try:
                    content = f.read_text(encoding="utf-8", errors="ignore")
                except (OSError, UnicodeDecodeError):
                    continue
                for pattern, flags in PATTERNS:
                    for match in re.finditer(pattern, content, flags):
                        var_name = match.group(1).upper()
                        if var_name not in EXCLUDE_VARS:
                            found.add(var_name)
    return found


def parse_env_example() -> set[str]:
    if not ENV_EXAMPLE.exists():
        return set()
    documented = set()
    content = ENV_EXAMPLE.read_text(encoding="utf-8")
    for line in content.splitlines():
        # Handle both active and commented-out vars (e.g., "# ANTHROPIC_API_KEY=...")
        stripped = line.lstrip("#").strip()
        if not stripped:
            continue
        match = re.match(r"([\w_]+)\s*=", stripped)
        if match:
            documented.add(match.group(1).upper())
    return documented


def main():
    print("Scanning source tree for env var usage...")
    code_vars = find_env_vars_in_code()
    print(f"  Found {len(code_vars)} env vars in code")

    print("Parsing .env.example...")
    documented = parse_env_example()
    print(f"  Found {len(documented)} documented vars")

    missing = sorted(code_vars - documented)
    dead = sorted(documented - code_vars)

    if missing:
        print(f"\nFAIL: {len(missing)} env vars used in code but missing from .env.example:")
        for var in missing:
            print(f"    {var}")
        sys.exit(1)

    if dead:
        print(f"\nNIT: {len(dead)} vars in .env.example but not found in code:")
        for var in dead:
            print(f"    {var}")

    if not missing:
        print("\nPASS: All env vars in code are documented in .env.example")
        sys.exit(0)


if __name__ == "__main__":
    main()
