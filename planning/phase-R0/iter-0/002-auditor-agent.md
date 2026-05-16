slug: 002-auditor-agent
package: protocol
goal: Create protocol/agents/auditor.py — Anthropic Opus client for audit verdicts
files_in_scope:
  - protocol/agents/__init__.py
  - protocol/agents/auditor.py
verify: "python -c 'from protocol.agents.auditor import Auditor; a=Auditor(api_key=\"test\", model=\"claude-opus-4\"); assert callable(a.audit)'"
wall_clock_minutes: 20
body: |
  Create protocol/agents/auditor.py implementing the Auditor agent that calls Anthropic's API for strict audit verdicts.

  Also create protocol/agents/__init__.py (empty file or with `__all__ = ["Auditor", "Planner", "Executor"]`).

  Requirements for Auditor:
  - Class `Auditor(api_key: str, model: str = "claude-opus-4", base_url: str = "https://api.anthropic.com", timeout: float = 120.0)`
  - Method `ping() -> bool` — sends a minimal request to verify connectivity and API key validity. Returns True on 200, False otherwise. Used by health-check.
  - Method `audit(system_prompt: str, user_message: str, max_tokens: int = 4096) -> dict` — sends an audit request to `/v1/messages` endpoint. Returns parsed JSON response with keys `verdict`, `reasoning`, `raw_text`.
  - Use `httpx.Client` with the given timeout. NO LiteLLM. NO anthropic SDK — direct HTTP only.
  - Headers: `x-api-key`, `anthropic-version: 2023-06-01`, `content-type: application/json`
  - Parse the verdict from the response text by looking for `PASS` or `FAIL` tokens (case-insensitive, first match wins). Default to `FAIL` if neither found (fail-closed).
  - Raise `AuditorError` (custom exception) on non-200 responses, including the status code and response body in the message.
  - Include type hints and docstrings.

  Do NOT include retry logic in this ticket (keep single-concern). Do NOT import from orchestrator or planner.
