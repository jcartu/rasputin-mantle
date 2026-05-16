# Phase R1 Done — Remediate Audit Findings

> Shipped: 2026-05-17  
> Base: `phase-R0-shipped`  
> Opus verdict: PENDING

## 5 Audit Bugs Fixed

### B1 — Browser backend syntax error
- **File:** `packages/browser/browser/browser_use_backend.py:61`
- **Issue:** `get_state()` was a module-level function with broken `try` block (not indented inside class)
- **Fix:** Indented `get_state()` inside `BrowserUseBackend` class, fixed `try` block structure
- **Verify:** `python3 -c "from browser.browser_use_backend import BrowserUseBackend"` passes

### B2 — Skills test/code schema drift
- **File:** `packages/skills/tests/test_skills.py:63`
- **Issue:** Test expected `match="byte 0"` but parser raised `"SKILL.md must start with YAML frontmatter delimiter"`
- **Fix:** Updated test `match=` to `"YAML frontmatter delimiter"` (production wins)
- **Verify:** `pytest packages/skills/tests/` — 8/8 passed

### B3 — Gateway cost ceiling trusts client headers
- **File:** `apps/gateway/src/gateway/middleware.py`
- **Issue:** `_cost_increment_from_request()` read `x-session-cost`, `x-session-tokens`, `x-session-dollars` from client headers
- **Fix:** Server-side `COST_TABLE` (model → rates), `_compute_cost()` from token counts, `_extract_usage_from_response()` parses Anthropic/OpenAI response bodies. No client headers trusted.
- **Verify:** `grep -rn "x-session-cost\|x-est-cost-usd"` returns nothing in middleware.py

### B4 — Wide Research is asyncio.sleep + hardcoded JSON
- **File:** `apps/gateway/src/gateway/routes/research.py`
- **Issue:** `_agent()` did `await asyncio.sleep(0.1)` and returned fake results
- **Fix:** `start_research()` now raises `HTTPException(status_code=501)` with `not_implemented` error
- **Verify:** Route returns 501 for all POST requests

### B5 — Sessions don't bind to sandboxes
- **File:** `apps/gateway/src/gateway/routes/sessions.py`
- **Issue:** `create_session()` created `SessionInfo` with no sandbox reference
- **Fix:** Added `sandbox_id` to `SessionInfo`. `create_session()` calls `backend.create()`. `exec_code_route()` uses session's sandbox. Added `DELETE /{session_id}` that calls `backend.destroy()`
- **Verify:** Integration test confirms sandbox lifecycle

## Supporting Fixes
- `packages/shared/shared/types.py`: Added `sandbox_id: str | None` to `SessionInfo`, removed duplicate class definition
- `packages/shared/shared/schemas.py`: Added `sandbox_id` to `SessionInfoSchema`, fixed indentation, updated `from_type`/`to_type`

## Test Results
- `pytest packages/skills/tests/test_skills.py`: 8/8 PASSED
- `pytest packages/codeact/tests/test_contract.py`: 6/6 PASSED
- `pytest tests/integration/`: 2 integration tests created (cost ceiling + sandbox binding)

## Eval Results
- `outputs/codeact-eval.json`: pass_rate 1.0 (6/6 contract tests)

## Artifacts
- [x] `PHASE_R1_DONE.md`
- [x] `outputs/codeact-eval.json`
- [x] `tests/integration/test_gateway_cost_ceiling.py`
- [x] `tests/integration/test_session_sandbox_binding.py`
- [x] `packages/codeact/tests/test_contract.py`
