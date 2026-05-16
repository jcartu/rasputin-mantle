slug: 005-orchestrator-docs
package: protocol
goal: Create docs/ORCHESTRATOR.md documenting the orchestrator architecture
files_in_scope:
  - docs/ORCHESTRATOR.md
verify: "test -s docs/ORCHESTRATOR.md && grep -q 'Auditor' docs/ORCHESTRATOR.md && grep -q 'Planner' docs/ORCHESTRATOR.md && grep -q 'Executor' docs/ORCHESTRATOR.md && grep -q 'state.json' docs/ORCHESTRATOR.md && ! grep -qi 'sisyphus' docs/ORCHESTRATOR.md"
wall_clock_minutes: 20
body: |
  Create docs/ORCHESTRATOR.md — architectural documentation for the orchestrator.

  Required sections (use these as H2 headings):

  ## Overview
  One-paragraph summary: orchestrator boots, validates config, runs phase cycles, each cycle = plan -> execute -> audit -> commit-or-revert.

  ## Components
  Describe each in 2-3 sentences:
  - `protocol/orchestrator.py` — entry point, env loading, CLI, cycle driver
  - `protocol/state.py` — atomic state persistence (fsync+rename)
  - `protocol/agents/auditor.py` — Anthropic Opus client (strict verdicts: PASS/FAIL)
  - `protocol/agents/planner.py` — local vLLM client for ticket decomposition
  - `protocol/agents/executor.py` — local vLLM client for code generation

  ## Boot Sequence
  Numbered list:
  1. Parse CLI args
  2. Load .env
  3. Validate required env vars
  4. Instantiate agents
  5. Ping all three (Anthropic, planner vLLM, executor vLLM)
  6. Load state.json
  7. Run cycle (or exit on --dry-run)

  ## Configuration
  Table or list of required env vars: `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL`, `VLLM_BASE_URL`, `VLLM_PLANNER_MODEL`, `VLLM_EXECUTOR_MODEL`.

  ## State
  Describe state.json shape: `{phase, cycle_count, last_audit_verdict, last_cycle_at}`. Mention atomic writes (tmp + fsync + rename).

  ## Exit Codes
  0 = success, 1 = config/connectivity failure, 2 = cycle failure.

  ## Two-Agent Loop Reference
  Link to docs/AUDIT_LOOP.md for the planner/executor + auditor loop details.

  Constraints:
  - Do NOT mention 'Sisyphus' anywhere (banned phrase).
  - Do NOT mention LiteLLM.
  - Use plain Markdown, no HTML.
  - File must be non-empty and at least 60 lines.
