from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
WORKSPACE_IMPORT_PATHS = [
    ROOT / "apps" / "gateway" / "src",
    ROOT / "packages" / "browser",
    ROOT / "packages" / "codeact",
    ROOT / "packages" / "sandbox",
    ROOT / "packages" / "shared",
    ROOT / "packages" / "skills",
]

for path in reversed(WORKSPACE_IMPORT_PATHS):
    path_text = str(path)
    if path.exists() and path_text not in sys.path:
        sys.path.insert(0, path_text)
