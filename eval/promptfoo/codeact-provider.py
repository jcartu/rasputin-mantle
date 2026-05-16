"""eval/promptfoo/codeact-provider.py — Promptfoo custom provider.

Invokes the local CodeAct catalog through the gateway. The gateway must be running
(make dev) and reachable at MANTLE_GATEWAY_URL (default http://127.0.0.1:8000).

Promptfoo calls call_api(prompt, options) and expects {"output": ...}.
"""
from __future__ import annotations

import json
import os
import re

import httpx


GATEWAY = os.environ.get("MANTLE_GATEWAY_URL", "http://127.0.0.1:8000")


def call_api(prompt: str, options: dict, context: dict) -> dict:
    """Promptfoo entrypoint."""
    # Parse "Use the X tool to Y" → ("X", "Y")
    m = re.match(r"Use the (\S+) tool to (.+?)\.", prompt.strip())
    if not m:
        return {"output": json.dumps({"error": "could not parse prompt", "prompt": prompt})}
    tool, action = m.group(1), m.group(2)

    try:
        r = httpx.post(
            f"{GATEWAY}/api/catalog/invoke",
            json={"tool": tool, "input": action, "format": "json"},
            timeout=30,
        )
        if r.status_code != 200:
            return {"output": json.dumps({
                "error": f"gateway returned {r.status_code}",
                "body": r.text[:500],
            })}
        return {"output": r.text}
    except httpx.RequestError as e:
        return {"output": json.dumps({"error": f"connection failed: {e}"})}
