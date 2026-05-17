# Rasputin Mantle v1.1 — Build Plan

v1.0 shipped. The audit found real bugs Sisyphus's auditor missed. v1.1 fixes them, then takes WebVoyager performance from 63% to ≥ 75% (stretch 80%) **on a tripled task set**.

## What v1.0 got right

The May 2026 baseline had ~30% real capability behind 7 phases of commits. v1.0 inverted that:

- All five May audit blockers genuinely fixed (browser SyntaxError, skills schema drift, cost wall, sessions↔sandbox binding, Wide Research).
- WebVoyager-100 actually ran with 100 real browser tasks per planner. Multi-model bench (GPT-5.5 / Opus 4.7 / Sonnet 4.5 / Kimi K2.6) is genuine data with real durations and real answers.
- Real Neko WebRTC iframe (no placeholder div).
- Memory client genuinely calls rasputin-memory's HTTP API with fallback.
- Honest release report that admits gaps (no judged GAIA, cost is estimate, voice p95 elevated by cold start).

## What v1.0 got wrong (audit findings v1.1 fixes)

| Finding | Severity | Location | Phase to fix |
|---|---|---|---|
| SSE stream heartbeat-only with literal `\n` characters | 🔴 blocker | `apps/gateway/.../routes/sessions.py:100` | S1 |
| Voice "live verified" has no live-path CI test | 🟡 fragile | `tests/integration/test_voice_round_trip.py` (uses MockTransport) | S1 |
| `audit-log/` directory never created — no per-iteration forensic trail | 🟡 process | (missing) | S1 |
| `planning/` only has R0/iter-0 — convention abandoned after R0 | 🟡 process | `planning/` | S1 |
| `state.json` stale (v2 Python orchestrator format from R0 boot) | 🟡 cleanup | `state.json` | S1 |
| R2 metrics backfilled after R6 tag | 🟢 process | git log | informational, no fix |

## The WebVoyager goal

Current: **63% with GPT-5.5 on WebVoyager-100.** Honest, real data.

Target: **≥ 75% on WebVoyager-300** (a 3× expanded benchmark) with the best planner. Stretch: 80%.

The 37 failures on WebVoyager-100 break down (hypothesized — S2 confirms by actually classifying):

- **DOM_FLAKY** (~10 failures): race conditions on page load, element-not-found because the page rehydrated mid-action, stale references after navigation. Fixable with proper waits and retries.
- **VLM_NEEDED** (~8 failures): pages where content is canvas-rendered, lazy-loaded behind virtual scroll, or so JS-heavy the DOM is opaque. Fixable with screenshot + vision-language model fallback.
- **MULTI_HOP_LOST** (~6 failures): agent took a wrong turn 3 hops in and can't recover. Fixable with self-correction.
- **ANSWER_MALFORMED** (~4 failures): agent found the right thing but expressed it in a way the LLM judge rejected. Fixable with better extraction prompts.
- **LOGIN_WALL / CAPTCHA / TIME_SENSITIVE** (~5 failures): genuinely outside what the benchmark grades fairly. We mark these "expected-fail" honestly, not skip them.
- **TOOL_BROKEN** (~3 failures): actual bugs in our browser primitives (e.g., `click` on a wrong selector strategy). Just fix them.
- **JUDGE_HARSH** (~1 failure): the LLM judge was wrong. We don't game the judge.

Best case from fixes: 63 + 10 (DOM) + 8 (VLM) + 6 (MULTI_HOP) + 4 (EXTRACT) + 3 (TOOL) = **94/100**. Subtract regressions (S3+S4+S5 might break a couple tasks that previously passed) → realistic 80-85%.

Honest internal estimate: **75-80%**. Above 80% I'd be skeptical.

## Why a 3× task set

WebVoyager-100 is easy to overfit. Adding 200 more tasks (100 from the official WebVoyager test set + 100 in-house validation tasks targeting our failure categories) makes the result credible. If our fixes are genuine improvements (not WebVoyager-100-specific cheats), the gain transfers to the new 200 tasks. If the gain only shows on the original 100, we cheated and need to redo.

The S6 release report will publish per-task-set pass rates side by side so anyone can audit.

## Phase shape (S1 → S6)

```
                      Phase           Goal                                Gate
                      ────────────────────────────────────────────────────────────
   audit findings ─→  S1  Fix v1.0    SSE real / audit-log/ / voice CI    tests green
                      ↓
   diagnostics    ─→  S2  Classify    37 failures → category JSON         taxonomy.json complete
                      ↓
   fixes          ─→  S3  Browser     waits, selectors, retries           WV-100 ≥ 70%
                      ↓
                      S4  Vision      DOM→screenshot fallback              WV-100 ≥ 73%
                      ↓
                      S5  Reasoning   self-correction loop                  WV-100 ≥ 75%
                      ↓
   release        ─→  S6  Final eval  WV-300 + per-category report         WV-300 ≥ 75%
```

Each phase still uses the strict audit loop. Sisyphus drives. 27B does work. Opus audits with the sharpened prompt that catches what v1.0's auditor missed.

## Cost projection

| Phase | Local 27B | Anthropic (Opus + Sonnet) | Vision API (Sonnet 4.6 vision) | Subtotal |
|---|---|---|---|---|
| S1 (fixes) | sunk | $1-2 | — | $1-2 |
| S2 (diagnostics) | sunk | $0-1 (Sonnet judge for failure classification) | — | $0-1 |
| S3 (browser hardening) | sunk | $2-4 (Opus audits + Sonnet judges on re-run) | — | $2-4 |
| S4 (vision) | sunk | $1-2 | $15-30 (one Sonnet vision call per failed DOM step on retries) | $16-32 |
| S5 (self-correction) | sunk | $2-4 | $5-10 | $7-14 |
| S6 (final eval) | sunk | $5-10 (WV-300 × multiple planners) | $20-40 (vision on hard tasks) | $25-50 |
| **Total** | — | **$11-23** | **$40-80** | **$51-103** |

Bigger than v1.0's $20-45 because vision API calls add up. Worth it if it buys 12+ points of WebVoyager.

If you want to keep v1.1 under $50: skip S4 (vision) and S5 (self-correction). Realistic ceiling without those is probably 72-73% on WebVoyager-100.

## Why these phases in this order

**S1 first** because v1.0 has known bugs that block visible progress (SSE → no Live Computer View narration). Also: S1 establishes the discipline (audit-log/ retrofit + auditor prompt update) the rest of v1.1 needs.

**S2 before S3-S5** because we don't know what to fix without the failure taxonomy. The hypothesis above (10 DOM_FLAKY, 8 VLM_NEEDED, ...) is just that — a hypothesis. S2 confirms or refutes by classifying every failure with evidence. If S2 finds 30 of the 37 are TIME_SENSITIVE, the whole S3-S5 plan changes.

**S3 (browser) before S4 (vision)** because DOM-side fixes are cheaper and lift more failures per dollar. Vision is expensive — save it for failures DOM-side can't reach.

**S5 (self-correction) last among the fix phases** because it's the highest-leverage change with the most potential to regress. Want S3 and S4's gains locked in first.

**S6 expands the test set** because v1.1 needs to be evaluable. WebVoyager-100 alone is easy to game in subtle ways; WebVoyager-300 makes results credible.

## Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| S2 reveals failures we can't fix (e.g., 25 LOGIN_WALL) | Low | High — caps v1.1 ceiling | Honest report; still pursue what's reachable |
| S4 vision blows the budget | Medium | Medium | Gate vision calls behind DOM-failed-extraction; cap per-task vision calls at 3 |
| S5 self-correction regresses S3+S4 gains | Medium | High | Stage gates: WV-100 must improve at each phase or we bisect |
| 27B-Sisyphus drifts on coordination across 6 phases | Medium | Medium | Same Opus-Sisyphus recommendation as v1.0; the loop discipline catches drift |
| Anti-cheating policy is violated subtly | Low | Critical | Sharpened auditor + explicit policy doc + S6 audit specifically checks |

## Definition of done for v1.1

- All S1 audit findings fixed and verified by S1 auditor.
- WebVoyager-300 ≥ 75% with the best planner, per-category breakdown published.
- `MANTLE_V1_1_RELEASED.md` exists with: per-task-set pass rates, per-category breakdown, cost summary, dependency delta vs v1.0, reproduction recipe, honest list of failure categories we couldn't reach.
- No anti-cheating violations flagged at S6 audit.
- All seven `phase-S*-shipped` tags exist on origin/main.

When all of those are true, v1.1 ships.
