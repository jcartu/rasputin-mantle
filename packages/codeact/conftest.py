from __future__ import annotations

import sys
from pathlib import Path

# Add all package roots to sys.path so cross-package imports work
ROOT = Path(__file__).resolve().parent.parent.parent  # repo root
for pkg in ("packages/sandbox", "packages/shared", "packages/browser", "packages/codeact"):
    p = ROOT / pkg
    if p.exists():
        sys.path.insert(0, str(p))
