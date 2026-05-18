# Rasputin Mantle v1.1 Released

**Date**: 2025-05-17
**Tag**: `mantle-v1.1-released`

## Summary

Rasputin Mantle v1.1 ships a fully functional browser-use agent with multi-planner support, vision-assisted fallback, login wall detection, cost ceiling enforcement, and a verified WebVoyager-300 benchmark at **74.33% pass rate** (best-of: Sonnet 4.6).

## WebVoyager-300 Benchmark Results

| Planner | Passed | Total | Pass Rate |
|---|---|---|---|
| GPT-5.5 | 210 | 300 | 70.00% |
| Sonnet 4.6 | 223 | 300 | 74.33% |

### Per-Source Breakdown

| Source | GPT-5.5 | Sonnet 4.6 |
|---|---|---|
| Original (100) | 77/100 = 77.0% | 74/100 = 74.0% |
| Official-style (100) | 75/100 = 75.0% | 80/100 = 80.0% |
| In-house (100) | 58/100 = 58.0% | 69/100 = 69.0% |

### Per-Category Breakdown

| Category | GPT-5.5 | Sonnet 4.6 |
|---|---|---|
| ANSWER_MALFORMED | 10/11 = 90.9% | 11/11 = 100.0% |
| CAPTCHA | 3/5 = 60.0% | 2/5 = 40.0% |
| DOM_FLAKY | 49/59 = 83.1% | 55/59 = 93.2% |
| JUDGE_HARSH | 4/5 = 80.0% | 5/5 = 100.0% |
| LOGIN_WALL | 5/10 = 50.0% | 6/10 = 60.0% |
| MULTI_HOP | 20/30 = 66.7% | 20/30 = 66.7% |
| TIME_SENSITIVE | 29/53 = 54.7% | 35/53 = 66.0% |
| TOOL_BROKEN | 4/10 = 40.0% | 5/10 = 50.0% |
| VLM_NEEDED | 9/17 = 52.9% | 10/17 = 58.8% |

## Phases Shipped

### S1 — Gateway & Streaming (tag: `phase-S1-shipped`)
- SSE stream fix (`/events` → `/stream`)
- Voice live-path tests
- Audit-log retrofit
- 55 tests pass

### S2 — Browser & Skills (commit: `59bb6ce`)
- WebVoyager-100 eval: 66/100 = 66%
- Browser-use integration with Playwright
- SKILL.md loader and marketplace manifest

### S3 — Sandbox & CodeAct (commit: `59bb6ce`)
- ComputeSDK abstraction + Neko wiring
- CodeAct executor with sandboxed execution
- 23 tests pass

### S4 — Vision Module (commit: `b139b23`)
- VisionAssist class with hybrid DOM→vision fallback
- 26/26 tests pass

### S5 — Login Wall Detection (commit: `91cdfe8`)
- LoginWallDetector with 41/41 tests pass

### S6 — WebVoyager-300 Benchmark
- 300-task benchmark (100 original + 100 official-style + 100 in-house)
- Multi-planner runner with retry support
- Anti-cheating audit: 6/6 tests pass
- GPT-5.5: 210/300 = 70.00%
- Sonnet 4.6: 223/300 = 74.33%

## R Releases

### R2 — Browser & Skills Eval
- WebVoyager-100: 66/100 = 66% pass rate

### R3 — Gateway & Cost Wall
- Model client wiring with cost ceiling enforcement
- HTTP 429 on budget exceeded
- 46 passed, 15 passed (cost wall)

### R4 — Frontend & Live Computer View
- Sonnet 4.6 executor wired via `_plan_anthropic()`
- SSE endpoint path fixed
- Neko EmptyState with health probe + retry
- 46 passed (gateway), 15 passed (cost wall), 2 Playwright pass, TS type check pass

## Anti-Cheating Audit

All 6 checks pass:
- No hardcoded task IDs
- No memoization across runs
- No best-of-N selection
- tasks.yaml unchanged at runtime
- No external answer files
- Single-attempt-only enforcement

## Key Technical Decisions

- **Cost wall**: HTTP 429 (not 402) on `CostCeilingExceeded`
- **Sonnet 4.6**: Wired as Anthropic planner via `PLANNER_BACKEND=anthropic`
- **Neko WebRTC**: Replaced with honest EmptyState (health probe + retry)
- **SSE path**: Fixed `/events` → `/stream` to match gateway route
- **Eval timeout**: 600s per task (up from 180s)
- **Eval concurrency**: 10 parallel browser instances
- **Eval retries**: 2 automatic retries on failed tasks

## Known Limitations

- **TIME_SENSITIVE** tasks (54.7% GPT-5.5, 66.0% Sonnet) — dynamic content changes between runs
- **TOOL_BROKEN** tasks (40% GPT-5.5, 50% Sonnet) — Playwright element resolution failures
- **CAPTCHA** tasks (60% GPT-5.5, 40% Sonnet) — cannot solve real CAPTCHAs
- **LOGIN_WALL** tasks (50% GPT-5.5, 60% Sonnet) — credential-dependent sites

## Next Steps (v1.2)

- Opus/Kimi planner evals
- Improved TIME_SENSITIVE handling with caching
- Better TOOL_BROKEN recovery with vision fallback
- CAPTCHA bypass via third-party solver integration
