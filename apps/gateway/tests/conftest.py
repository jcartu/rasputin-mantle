from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent

# Gateway src
sys.path.insert(0, str(ROOT / "apps" / "gateway" / "src"))

# Workspace Workspace  packages
for pkg in ("shared", "skills", "codeact", "sandbox", "browser"):
    p = ROOT / "packages" / pkg
    if p.exists():
        sys.path.insert(0, str(p))
