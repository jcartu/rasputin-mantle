#!/usr/bin/env python3
"""scripts/sisyphus-state-check.py — detect drift between Sisyphus's claimed state and reality.

When Sisyphus runs on local 27B (qwen3.5-27b), state can drift across long
runs: boulder.json claims phase W4 while git tags say W2, or claims an audit
PERFECT while open tickets remain. This script catches drift in <1s.

Run every 5 tickets per the 27B Orchestrator Guide. Exit 0 = drift-free.

Usage:
    python scripts/sisyphus-state-check.py
    python scripts/sisyphus-state-check.py --json     # machine-readable
    python scripts/sisyphus-state-check.py --quiet    # only fail output

Exit:
    0 = drift = 0; safe to continue
    1 = drift > 0; STOP and reconcile before proceeding
    2 = state files missing / unreadable; can't determine drift
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


BOULDER_CANDIDATES = ["boulder.json", ".sisyphus/boulder.json", "state/boulder.json"]
PLANNING_DIR = Path("planning")
AUDIT_LOG_DIR = Path("audit-log")


def find_boulder() -> Path | None:
    for p in BOULDER_CANDIDATES:
        if Path(p).is_file():
            return Path(p)
    return None


def latest_phase_tag() -> str | None:
    try:
        result = subprocess.run(
            ["git", "tag", "-l", "phase-W*-shipped"],
            capture_output=True, text=True, timeout=10
        )
        tags = sorted(
            (t for t in result.stdout.strip().splitlines() if t),
            key=lambda t: int(re.search(r"W(\d+)", t).group(1)) if re.search(r"W(\d+)", t) else 0,
        )
        return tags[-1] if tags else None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def commits_ahead_of_origin() -> int:
    try:
        result = subprocess.run(
            ["git", "rev-list", "--count", "@{upstream}..HEAD"],
            capture_output=True, text=True, timeout=10
        )
        return int(result.stdout.strip() or "0")
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
        return 0


def latest_commit_subject() -> str:
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%s"],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""


def open_planning_tickets() -> list[str]:
    """Return list of unfinished ticket files (those whose phase isn't yet tagged shipped)."""
    if not PLANNING_DIR.is_dir():
        return []
    out: list[str] = []
    for phase_dir in sorted(PLANNING_DIR.glob("phase-W*")):
        phase_name = phase_dir.name.replace("phase-", "")
        # Is this phase shipped?
        shipped = False
        try:
            result = subprocess.run(
                ["git", "tag", "-l", f"phase-{phase_name}-shipped"],
                capture_output=True, text=True, timeout=10
            )
            shipped = bool(result.stdout.strip())
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        if shipped:
            continue
        # Phase not shipped — list its tickets
        for ticket in phase_dir.rglob("*.md"):
            if ticket.name in ("PHASE_DONE.md", "BLOCKED.md"):
                continue
            out.append(str(ticket))
    return out


def latest_audit_verdict() -> str | None:
    """Return the verdict from the most recent audit-log/*.json file."""
    if not AUDIT_LOG_DIR.is_dir():
        return None
    audits = sorted(AUDIT_LOG_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime)
    if not audits:
        return None
    try:
        data = json.loads(audits[-1].read_text())
        return data.get("verdict")
    except (json.JSONDecodeError, OSError):
        return None


def compute_drift(state: dict) -> tuple[int, list[str]]:
    """Compare boulder.json claims to git/file reality. Return (drift_count, reasons)."""
    drift = 0
    reasons: list[str] = []

    boulder_phase = state.get("boulder_phase")
    tag_phase = state.get("tag_phase")
    open_tickets = state.get("open_tickets", [])
    audit_verdict = state.get("audit_verdict")
    commits_ahead = state.get("commits_ahead", 0)

    # 1. boulder.json phase must match the latest shipped tag + 1 (or equal if in-progress)
    if boulder_phase and tag_phase:
        bn = int(re.search(r"W(\d+)", boulder_phase).group(1))
        tn = int(re.search(r"W(\d+)", tag_phase).group(1)) if re.search(r"W(\d+)", tag_phase) else -1
        # boulder phase should be tn+1 (next to ship) OR tn (just shipped, transitioning)
        if bn not in (tn, tn + 1):
            drift += 1
            reasons.append(
                f"boulder claims phase {boulder_phase}, latest shipped tag is {tag_phase} "
                f"(expected boulder to be W{tn} or W{tn+1})"
            )

    # 2. If boulder claims "shipped" but ticket files still open in current phase, drift
    boulder_status = state.get("boulder_status")
    if boulder_status == "shipped" and open_tickets:
        drift += 1
        reasons.append(
            f"boulder status=shipped but {len(open_tickets)} ticket(s) still open: {open_tickets[:3]}"
        )

    # 3. If audit verdict is PUNCH_LIST but no new tickets/commits since, Sisyphus is stuck
    if audit_verdict == "PUNCH_LIST" and commits_ahead == 0 and not open_tickets:
        drift += 1
        reasons.append(
            "audit returned PUNCH_LIST but no new tickets opened and no commits ahead — stuck"
        )

    # 4. Too many commits ahead of origin (push discipline violated)
    if commits_ahead > 5:
        drift += 1
        reasons.append(
            f"{commits_ahead} commits ahead of origin (rule: push every 3 commits)"
        )

    return drift, reasons


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--json", action="store_true", help="JSON output for auditor consumption")
    ap.add_argument("--quiet", action="store_true", help="Only print on failure")
    args = ap.parse_args()

    state: dict = {}

    # Boulder state
    boulder_path = find_boulder()
    if boulder_path:
        try:
            boulder_data = json.loads(boulder_path.read_text())
            state["boulder_phase"] = boulder_data.get("current_phase") or boulder_data.get("phase")
            state["boulder_status"] = boulder_data.get("status")
            state["boulder_iter"] = boulder_data.get("current_iter") or boulder_data.get("iter")
        except (json.JSONDecodeError, OSError) as e:
            state["boulder_error"] = str(e)

    # Git state
    state["tag_phase"] = latest_phase_tag()
    state["commits_ahead"] = commits_ahead_of_origin()
    state["last_commit"] = latest_commit_subject()

    # Planning state
    state["open_tickets"] = open_planning_tickets()

    # Audit state
    state["audit_verdict"] = latest_audit_verdict()

    drift, reasons = compute_drift(state)
    state["drift"] = drift
    state["drift_reasons"] = reasons

    if args.json:
        print(json.dumps(state, indent=2))
        return 0 if drift == 0 else 1

    if args.quiet and drift == 0:
        return 0

    print("🧭 Sisyphus state check (v1.3)")
    print(f"  Current phase per boulder.json:  {state.get('boulder_phase') or 'unknown'}")
    if state.get("boulder_iter") is not None:
        print(f"  Current iteration:               {state.get('boulder_iter')}")
    if state.get("boulder_status"):
        print(f"  Boulder status:                  {state.get('boulder_status')}")
    print(f"  Latest shipped tag:              {state.get('tag_phase') or 'none'}")
    print(f"  Commits ahead of origin:         {state['commits_ahead']}")
    print(f"  Open tickets:                    {len(state['open_tickets'])}")
    if state["open_tickets"]:
        for t in state["open_tickets"][:3]:
            print(f"      · {t}")
        if len(state["open_tickets"]) > 3:
            print(f"      · …and {len(state['open_tickets']) - 3} more")
    print(f"  Last audit verdict:              {state.get('audit_verdict') or 'none'}")
    print(f"  Last commit:                     {state.get('last_commit') or 'none'}")
    print()
    print(f"  Drift: {drift}")
    if drift > 0:
        for r in reasons:
            print(f"    ✗ {r}")
        print()
        print("STOP. Reconcile before continuing. See docs/27B_ORCHESTRATOR_GUIDE.md "
              "section 'State recovery after interrupt'.", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
