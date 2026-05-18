#!/usr/bin/env python3
"""scripts/verify-readme-claims.py — verify every README "What ships" bullet matches the codebase.

Closes the v1.2 audit gap: README claimed Replay/Share/Onboarding, none in code.
The auditor verified each phase's commits but never cross-checked the README
against grep. This script does, deterministically.

Usage:
    python scripts/verify-readme-claims.py [README.md]
    python scripts/verify-readme-claims.py --explain [README.md]

Exit:
    0 = all bullets verified
    1 = at least one bullet has zero matches and no valid annotation
    2 = at least one bullet too vague, needs <!-- verify: pattern --> annotation
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


WHAT_SHIPS_HEADER_PATTERNS = [
    re.compile(r"^##\s+What ships in v\d+\.\d+\s*$", re.MULTILINE),
    re.compile(r"^##\s+What ships\s*$", re.MULTILINE),
    re.compile(r"^##\s+What's in v\d+\.\d+\s*$", re.MULTILINE),
]

ROADMAP_HEADER_PATTERNS = [
    re.compile(r"^##\s+On the roadmap\s*$", re.MULTILINE),
    re.compile(r"^##\s+Coming in v\d+\.\d+\s*$", re.MULTILINE),
    re.compile(r"^##\s+Roadmap\s*$", re.MULTILINE),
]

SEARCH_ROOTS = ["apps", "packages", "design-system", "scripts", "eval"]
EXCLUDE_DIRS = {"node_modules", ".next", "__pycache__", ".git", "dist", "build", ".turbo"}

VAGUE_KEYWORDS = {
    "accessibility", "performance", "quality", "polish", "details",
    "the", "rest", "more", "various", "many", "improved", "better",
    "comprehensive", "robust", "modern", "clean",
}


def find_section(readme: str, patterns: list[re.Pattern]) -> tuple[int, int] | None:
    for pat in patterns:
        m = pat.search(readme)
        if m:
            start = m.end()
            nxt = re.search(r"^##\s+", readme[start:], re.MULTILINE)
            end = start + nxt.start() if nxt else len(readme)
            return (start, end)
    return None


def extract_bullets(section: str) -> list[tuple[str, str | None]]:
    """Return list of (bullet_text, optional_annotation)."""
    out: list[tuple[str, str | None]] = []
    lines = section.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        m = re.match(r"^[-*]\s+(.+)$", line)
        if not m:
            i += 1
            continue
        bullet = m.group(1).strip()
        ann = None
        # Inline annotation in same line
        inline = re.search(r"<!--\s*verify:\s*(.+?)\s*-->", line)
        if inline:
            ann = inline.group(1).strip()
            # Strip the comment from bullet text for clean display
            bullet = re.sub(r"<!--\s*verify:.*?-->", "", bullet).strip()
        # Continuation lines
        j = i + 1
        while j < len(lines):
            nl = lines[j].rstrip()
            if not nl:
                break
            if re.match(r"^[-*]\s+", nl):
                break
            if re.match(r"^##?\s+", nl):
                break
            cm = re.search(r"<!--\s*verify:\s*(.+?)\s*-->", nl)
            if cm and not ann:
                ann = cm.group(1).strip()
            j += 1
        out.append((bullet, ann))
        i = j
    return out


def derive_keyword(bullet: str) -> str | None:
    # 1. Backtick code
    m = re.search(r"`([^`]+)`", bullet)
    if m:
        return m.group(1)
    # 2. Bold
    m = re.search(r"\*\*([^*]+)\*\*", bullet)
    if m:
        text = m.group(1).strip().rstrip(":")
        if text:
            return text.split()[0].lower()
    # 3. First capitalized word
    m = re.match(r"^([A-Z][a-zA-Z0-9-]+)\b", bullet)
    if m:
        return m.group(1).lower()
    return None


def grep_codebase(pattern: str) -> list[str]:
    args = ["grep", "-rliE", pattern]
    has_root = False
    for root in SEARCH_ROOTS:
        if Path(root).is_dir():
            args.append(root)
            has_root = True
    if not has_root:
        return []
    args.extend(f"--exclude-dir={d}" for d in EXCLUDE_DIRS)
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=30)
        files = [f for f in result.stdout.strip().splitlines() if f]
        return files[:5]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return _python_grep(pattern)


def _python_grep(pattern: str) -> list[str]:
    regex = re.compile(pattern, re.IGNORECASE)
    matches: list[str] = []
    for root in SEARCH_ROOTS:
        rp = Path(root)
        if not rp.is_dir():
            continue
        for p in rp.rglob("*"):
            if not p.is_file():
                continue
            if any(part in EXCLUDE_DIRS for part in p.parts):
                continue
            try:
                content = p.read_text(errors="ignore")
            except Exception:
                continue
            if regex.search(content):
                matches.append(str(p))
                if len(matches) >= 5:
                    return matches
    return matches


def verify_bullet(bullet: str, ann: str | None, explain: bool) -> tuple[str, str]:
    if ann:
        if ann.strip() == "skip":
            return ("pass", "skipped (annotation: skip)")
        patterns = [p.strip() for p in ann.split(",") if p.strip()]
        failed = [p for p in patterns if not grep_codebase(p)]
        if failed:
            return ("fail", f"annotation patterns with no matches: {', '.join(failed)}")
        return ("pass", f"annotation patterns all matched ({len(patterns)})")

    keyword = derive_keyword(bullet)
    if not keyword:
        return ("vague", "no derivable keyword and no verify annotation")
    if keyword.lower() in VAGUE_KEYWORDS:
        return ("vague", f"keyword '{keyword}' is too generic; add <!-- verify: pattern --> annotation")

    matches = grep_codebase(re.escape(keyword))
    if not matches:
        return ("fail", f"keyword '{keyword}' has zero matches in {SEARCH_ROOTS}")
    if explain:
        return ("pass", f"keyword '{keyword}' matched in {', '.join(matches[:3])}")
    return ("pass", f"keyword '{keyword}' matched ({len(matches)} files)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("readme", nargs="?", default="README.md")
    ap.add_argument("--explain", action="store_true", help="Verbose match locations")
    args = ap.parse_args()

    path = Path(args.readme)
    if not path.is_file():
        print(f"ERROR: {path} not found", file=sys.stderr)
        return 1

    text = path.read_text()
    section = find_section(text, WHAT_SHIPS_HEADER_PATTERNS)
    if not section:
        print(f"NOTICE: no '## What ships in vX.Y' section in {path}", file=sys.stderr)
        return 0

    start, end = section
    section_text = text[start:end]
    bullets = extract_bullets(section_text)
    if not bullets:
        print(f"NOTICE: 'What ships' section empty in {path}", file=sys.stderr)
        return 0

    print(f"Verifying {len(bullets)} bullet(s) from '## What ships' section of {path}")
    print()

    fail = 0
    vague = 0
    for bullet, ann in bullets:
        display = re.sub(r"\*\*([^*]+)\*\*", r"\1", bullet)
        display = re.sub(r"\s+", " ", display).strip()[:80]
        status, detail = verify_bullet(bullet, ann, args.explain)
        icon = {"pass": "✓", "fail": "✗", "vague": "?"}[status]
        print(f"  {icon} {display}")
        if status != "pass" or args.explain:
            print(f"      → {detail}")
        if status == "fail":
            fail += 1
        if status == "vague":
            vague += 1

    print()
    print(f"Summary: {len(bullets) - fail - vague} passed, {fail} failed, {vague} vague")

    if fail:
        print(f"\nFAIL: {fail} bullet(s) claim features not found in the codebase.", file=sys.stderr)
        print("Either ship the feature, remove the bullet, or move it to '## On the roadmap'.", file=sys.stderr)
        return 1
    if vague:
        print(f"\nVAGUE: {vague} bullet(s) need <!-- verify: pattern --> annotation.", file=sys.stderr)
        print("See docs/README_AUDIT_POLICY.md for examples.", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
