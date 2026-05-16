from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
for package_path in (ROOT / "packages" / "codeact", ROOT / "packages" / "sandbox"):
    package_path_text = str(package_path)
    if package_path_text not in sys.path:
        sys.path.insert(0, package_path_text)

from codeact.executor import execute_code  # noqa: E402


async def call_api(prompt: str, options: dict[str, Any], context: dict[str, Any] | None) -> dict[str, str]:
    vars_payload = (context or {}).get("vars", {})
    code = vars_payload.get("code", prompt)
    if not isinstance(code, str):
        return {"error": "Promptfoo test case must provide Python code as a string"}

    result = await execute_code(code)
    return {"output": json.dumps(asdict(result), sort_keys=True)}
