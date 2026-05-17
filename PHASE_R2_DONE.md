# Phase R2 — Browser & Skills (STATUS REPORT)

## Status: SYSTEM WORKS, GATE NOT MET

The R2 infrastructure is fully built and validated, but the WebVoyager-100 pass rate gate (≥60%) is not yet met at 10/100 (10%).

## What Ships

### Browser Backend (PlaywrightBackend)
- `packages/browser/browser/playwright_backend.py` — Async Playwright wrapper
- Chromium runs with **sandbox ON** (no `disable-sandbox flag`)
- Supports: `open`, `click`, `type_text`, `evaluate`, `get_state`, `close`
- Returns structured `BrowserState` with elements, title, URL, screenshot

### Skills Loader
- `packages/skills/` — SKILL.md loader with Pydantic validation
- 15/15 integration tests pass (`test_skills_loader.py`)
- Validates frontmatter shape, name patterns, file/description limits
- Rejects malformed skills loudly

### Sandbox Runtime
- `packages/sandbox/` — `LocalDockerBackend` spawns real containers
- 8/8 integration tests pass (`test_sandbox_runtime.py`)
- Supports: `create`, `destroy`, `exec_code`, `write_file`, `read_file`, `list_files`

### Agent Endpoint
- `apps/gateway/src/gateway/routes/agent.py` — `/api/agent/run` endpoint
- Drives `PlaywrightBackend` from natural-language task + start URL
- Plans next action via vLLM/Cerebras OpenAI-compatible API
- SSRF-protected URL validation, blocked private/local IPs
- Cleanup via `asyncio.shield` to guarantee browser+sandbox teardown

### Eval Infrastructure
- `eval/webvoyager-100/tasks.yaml` — 100 WebVoyager-style tasks
- `eval/webvoyager-100/runner.py` — Eval harness with judge-style scoring
- `outputs/webvoyager-100.json` — Full eval run results

## WebVoyager-100 Results

| Metric | Value |
|---|---|
| Total tasks | 100 |
| Passed | 10 |
| Pass rate | **10.0%** |
| Gate target | ≥60.0% |
| Status | ❌ GATE NOT MET |

### Tasks that passed (10/100)
- `wv-003` Wikipedia: Marie Curie's first Nobel Prize → **1903** ✅
- `wv-004` GitHub: linux/linux stars → **233k** ✅
- `wv-008` Hacker News: top story extracted ✅
- `wv-031` Cambridge Dictionary: example sentence for "resilient" ✅
- `wv-036` NFL: AFC East leader ✅
- `wv-069` Azure CLI: `az login` syntax ✅
- `wv-078` CUDA Toolkit: latest version → **13.2** ✅
- `wv-093` NASA on X: bio extracted ✅
- `wv-095` Kazakhstan capital → **Astana** ✅
- `wv-097` Tungsten: symbol **W**, atomic number **74** ✅

### Failure modes observed
1. **Google search consent screens** — `consent.google.com` interstitial blocks navigation. Click selectors timeout.
2. **Google search results parsing** — After typing+Enter, Google's knowledge panels use highly dynamic selectors (`data-attrid=...`) that the agent struggles to navigate.
3. **Multi-step navigation** — Agent loops on the same action when state doesn't change as expected (e.g., flights, complex forms).
4. **Dynamic JS content** — Pages requiring scroll, lazy-loading, or JavaScript interaction.

## What Works End-to-End

The 10 passing tasks demonstrate that the full pipeline works:
- Playwright opens real URLs with sandbox ON
- Agent reads page state (URL, title, 40 elements after compression)
- Cerebras Qwen3-235B model returns valid action JSON in <1s
- Agent executes click/type/evaluate/finish actions
- Page state updates and the loop converges to a `finish` with the correct answer

## Constraints Honored

- ✅ Chromium runs with sandbox ON (no `disable-sandbox flag`)
- ✅ SKILL.md loader rejects malformed skills
- ✅ Sandbox spawns real containers (verified with `docker ps`)
- ✅ Cost ceiling middleware enforces server-side limits
- ✅ No stubs, no synthetic data
- ✅ `_validated_http_url` blocks SSRF (loopback/private IPs)
- ✅ Forbidden patterns (`disable-sandbox flag`, stub backends) — none present in code

## Gap to Gate

To reach ≥60% WebVoyager pass rate, the agent loop needs:
1. **Better consent/cookie wall handling** — detect and dismiss interstitials before main task
2. **Multi-step planning** — fewer redundant retries, better awareness of when state hasn't changed
3. **Improved element selection** — fallback strategies when target element isn't in compressed top-40
4. **Tool use for evaluation** — extract structured data (text near search box, knowledge panel content) rather than blind JS

## Architecture Decisions

- **Cerebras for browser planning** (not local Qwen3.6-27B) — Qwen3.6-27B is a reasoning model that returns empty `content` field. Cerebras' `qwen-3-235b-a22b-instruct-2507` is non-reasoning, returns JSON in 300ms.
- **State compression to 40 elements** — was 191 elements / 41KB, caused 180s timeouts. Compressed to 1.8-2.5KB JSON.
- **`enable_thinking: false`** — disables Qwen's reasoning chain when calling local vLLM.

## Files Changed
- `apps/gateway/src/gateway/app.py` — added `.env` loading
- `apps/gateway/src/gateway/routes/agent.py` — `/api/agent/run` endpoint, state compression
- `packages/browser/browser/playwright_backend.py` — PlaywrightBackend with sandbox ON
- `packages/browser/SKILL.md`, `packages/skills/SKILL.md`, `packages/sandbox/SKILL.md`
- `eval/webvoyager-100/tasks.yaml` — 100 WebVoyager tasks
- `eval/webvoyager-100/runner.py` — eval harness
- `tests/integration/test_browser_navigate.py`
- `tests/integration/test_skills_loader.py` (15 tests)
- `tests/integration/test_sandbox_runtime.py` (8 tests)

## Honest Verdict

R2 has the **right architecture and a working end-to-end loop**, but the WebVoyager-100 gate is not met. The 10% baseline establishes that the infrastructure functions correctly; closing the gap to 60% requires:
- Significantly improved prompt engineering and action selection logic
- Consent screen detection middleware in the agent loop
- Better failure recovery (detect loops, try alternative approaches)

The code is honest: no stubs, no `disable-sandbox flag`, no Potemkin tests. The integration tests pass (23/23). The eval infrastructure runs and produces real numbers. But the model's browser navigation skill on heterogeneous real-world sites is the bottleneck.
