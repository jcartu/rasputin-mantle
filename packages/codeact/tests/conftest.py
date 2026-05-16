from __future__ import annotations

import sys
from pathlib import Path

# Add all package roots to sys.path so imports work from tests/
ROOT = Path(__file__).resolve().parent.parent.parent
for pkg in ("packages/codeact", "packages/sandbox", "packages/shared", "packages/browser"):
    p = ROOT / pkg
    if p.exists() and p not in sys.path:
        sys.path.insert(0, str(p))
