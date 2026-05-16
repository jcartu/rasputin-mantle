slug: 003-planner-executor-agents
package: protocol
goal: Create protocol/agents/planner.py and protocol/agents/executor.py — vLLM clients
files_in_scope:
  - protocol/agents/planner.py
  - protocol/agents/executor.py
verify: "python -c 'from protocol.agents.planner import Planner; from protocol.agents.executor import Executor; p=Planner(base_url=\"http://localhost:8000/v1\", model=\"test\"); e=Executor(base_url=\"http://localhost:8000/v1\", model=\"test\"); assert callable(p.plan) and callable(e.execute)'"
wall_clock_minutes: 25
body: |
  Create two sibling files under protocol/agents/ that share an identical HTTP client shape but expose semantically distinct methods.

  Both call a local vLLM server using the OpenAI-compatible /v1/chat/completions endpoint via direct httpx (NO openai SDK, NO LiteLLM).

  === protocol/agents/planner.py ===
  - Class `Planner(base_url: str, model: str, api_key: str = "EMPTY", timeout: float = 300.0)`
  - Method `ping() -> bool` — GET `{base_url}/models`, return True on 200.
  - Method `plan(system_prompt: str, user_message: str, max_tokens: int = 8192, temperature: float = 0.2) -> dict` — POST to `/chat/completions`. Returns `{"text": str, "raw": dict}` where `text` is the assistant message content.
  - Raises `PlannerError` on non-200.

  === protocol/agents/executor.py ===
  - Class `Executor(base_url: str, model: str, api_key: str = "EMPTY", timeout: float = 600.0)`
  - Method `ping() -> bool` — same as Planner.
  - Method `execute(system_prompt: str, user_message: str, max_tokens: int = 16384, temperature: float = 0.1) -> dict` — same shape as plan(). Returns `{"text": str, "raw": dict}`.
  - Raises `ExecutorError` on non-200.

  Shared requirements:
  - Use `httpx.Client` with `Authorization: Bearer {api_key}` header.
  - Type hints and docstrings on all public methods.
  - Each module defines its own exception class (no shared base).
  - No retry logic. No state. Stateless clients only.

  Do NOT modify protocol/agents/__init__.py in this ticket (ticket 002 owns it). Do NOT import from orchestrator.
