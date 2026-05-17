# PHASE_S1_DONE.md — Fix v1.0 audit findings

## Summary

S1 addresses every blocker and warning from the v1.0 audit. All existing tests remain green; new tests for SSE and voice live-path are green.

## Tickets Completed

### 1. SSE real broker (blocker)
- **Before:** `apps/gateway/src/gateway/routes/sessions.py:100` — heartbeat-only SSE with literal `\n` characters (`\\n` in f-string). SSE clients could not parse events.
- **After:** Replaced with `EventBroker` (asyncio.Queue per session). `broker.publish()` called on every exec. SSE generator reads from queue with 30s heartbeat timeout. Real `\n` newlines in yield strings.
- **Files changed:** `apps/gateway/src/gateway/sessions.py` (EventBroker class), `apps/gateway/src/gateway/routes/sessions.py` (stream_session, exec_code_route)
- **Test:** `tests/integration/test_sse_real_events.py` (5 tests — broker events, real newlines, 404, publish/queue, remove)

### 2. Voice live-path CI tests (warning)
- **Before:** Only `_when_unavailable` tests (asserting 503). No live-path coverage.
- **After:** Added `tests/integration/test_voice_live_path.py` with `*_when_available` tests gated on `/health` checks. Old `_when_unavailable` tests now skip when services are running.
- **Files changed:** `tests/integration/test_voice_live_path.py` (new), `apps/gateway/tests/test_gateway.py` (added health-gate skip + pytest import)

### 3. Retrofit audit-log/ (process)
- **Before:** `audit-log/` directory never created.
- **After:** `audit-log/` contains R0-R6 verdict JSONs retrofitted from git history.
- **Files created:** `audit-log/phase-R{0..6}-iter-0.json`

### 4. Clean state.json (cleanup)
- **Before:** `state.json` stale (v2 Python orchestrator format from R0 boot).
- **After:** Removed. `boulder.json` is the real state.

### 5. v1.1 protocol files installed (process)
- **Files installed:** `protocol/phases/phase-S{1..6}.yaml`, `protocol/prompts/auditor-strict.md` (patterns 17-23), `.opencode/agents/mantle-auditor.md` (updated body), `docs/NO_CHEATING_POLICY.md`, `docs/V1_1_BUILD_PLAN.md`, `docs/FAILURE_CATEGORIES.md`, `scripts/categorize-failures.py`

## Test Results

```
55 passed, 2 skipped, 0 failed
```

Skipped: `test_voice_transcribe_returns_503_when_unavailable` (Whisper running), `test_voice_synthesize_returns_503_when_unavailable` (Kokoro running) — correct behavior per auditor pattern #2.

## Artifacts

- [x] `PHASE_S1_DONE.md`
- [x] `audit-log/` (7 verdict files, R0-R6)
- [x] `docs/NO_CHEATING_POLICY.md`
- [x] `docs/V1_1_BUILD_PLAN.md`
- [x] `docs/FAILURE_CATEGORIES.md`
- [x] `tests/integration/test_sse_real_events.py`
- [x] `tests/integration/test_voice_live_path.py`
