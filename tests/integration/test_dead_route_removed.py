"""Verify the dead session/[id] route was removed (W0 ticket 3)."""

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_dead_route_removed():
    """apps/web/app/session/[id]/page.tsx must NOT exist (dead code)."""
    dead = REPO_ROOT / "apps" / "web" / "app" / "session" / "[id]" / "page.tsx"
    assert not dead.exists(), (
        f"Dead route still exists: {dead}. "
        "The canonical route is apps/web/app/(app)/session/[id]/page.tsx"
    )


def test_canonical_route_still_exists():
    """apps/web/app/(app)/session/[id]/page.tsx MUST exist (canonical route)."""
    canonical = REPO_ROOT / "apps" / "web" / "app" / "(app)" / "session" / "[id]" / "page.tsx"
    assert canonical.exists(), (
        f"Canonical route missing: {canonical}. "
        "The (app) group route is the live session page."
    )


def test_no_react_resizable_panels_in_session_route():
    """The dead route imported react-resizable-panels incorrectly. Ensure no leak."""
    dead = REPO_ROOT / "apps" / "web" / "app" / "session" / "[id]" / "page.tsx"
    if dead.exists():
        content = dead.read_text()
        assert "react-resizable-panels" not in content, (
            "Dead route still imports react-resizable-panels"
        )
    # If dead route doesn't exist (expected), this is a pass
