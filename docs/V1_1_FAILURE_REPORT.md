# V1.1 WebVoyager-100 Failure Report

**Source run:** `outputs/v1_1/webvoyager-100-baseline.json`
**Taxonomy:** `outputs/v1_1/failure-taxonomy.json`
**Categorized:** 2026-05-17 (claude-sonnet-4-6)

## Executive Summary

- **Total tasks:** 100
- **Failures:** 37
- **Pass rate:** 63%
- **Top categories:** UNCLASSIFIED (18), LOGIN_WALL (9), DOM_FLAKY (5), TOOL_BROKEN (5)
- **Phase distribution:** S3 = 27, S4 = 1, S5 = 9

Roughly half of the failures (18/37) carry no trace evidence and surface as empty errors with zero tool calls. The remaining 19 cluster cleanly into three actionable buckets: auth-gated sites, Playwright execution-context races, and tool-level timeouts.

## Category Breakdown

| Category | Count | Fixable Phase | Effort |
|----------|------:|---------------|--------|
| UNCLASSIFIED | 18 | S3 | low (trace plumbing) |
| LOGIN_WALL | 9 | S5 | medium |
| DOM_FLAKY | 5 | S3/S4 | low |
| TOOL_BROKEN | 5 | S3 | low |
| VLM_NEEDED | 0 | - | - |
| MULTI_HOP_LOST | 0 | - | - |
| ANSWER_MALFORMED | 0 | - | - |
| CAPTCHA | 0 | - | - |
| TIME_SENSITIVE | 0 | - | - |
| JUDGE_HARSH | 0 | - | - |

## Representative Examples

### TOOL_BROKEN (5)

Playwright runtime failures (screenshot timeouts, destroyed execution contexts) where the tool itself, not the agent's reasoning, broke.

- `wv-002` Find the population of Tokyo, Japan. Playwright screenshot timeout.
- `wv-010` On Reddit, find a recent post in r/python with > 100 upvotes. `Page.evaluate: Execution context was destroyed`.
- `wv-064` On LinkedIn, search for Coursera's company page and report the employee count range. Playwright execution-context error.
- `wv-095` On Wikipedia, find the capital city of Kazakhstan. Screenshot timeout during capture.
- `wv-096` On Wikipedia, find the winner of the 2022 FIFA World Cup. `Page.screenshot: Timeout 30000ms exceeded`.

### LOGIN_WALL (9)

Sites that require authentication or aggressively block unauthenticated bots. The agent typically returns an empty error after being redirected or blocked.

- `wv-026` Booking.com hotel search. Blocking page (likely CAPTCHA or auth wall) before any interaction.
- `wv-060` Khan Academy lesson lookup. Blocked before any content retrieval.
- `wv-063` LinkedIn Microsoft company page. Destroyed context after redirect to login.
- `wv-066` Medium machine-learning article. Auth/paywall barrier.
- `wv-084` Pinterest minimalist home office board. Pinterest auth required to browse boards.
- `wv-085` Pinterest salmon recipe pin. Blocked by Pinterest auth/bot-detection.
- `wv-092` X (Twitter) OpenAI latest post. Auth wall blocks public posts.
- `wv-093` X (Twitter) NASA profile bio. Login wall.
- `wv-094` X (Twitter) WebAssembly search. Auth wall blocks search.

### DOM_FLAKY (5)

Race conditions where the page navigated or reloaded mid-`evaluate`, destroying the JS execution context. These are recoverable with retry-on-navigation logic.

- `wv-061` Khan Academy SAT math section. Execution-context race during DOM read.
- `wv-062` LinkedIn OpenAI company page. Stale execution context on navigation.
- `wv-086` Reddit r/MachineLearning top post. Navigation mid-evaluate.
- `wv-087` Reddit r/travel Japan thread. Same race condition.
- `wv-088` Reddit r/AskHistorians rules. Execution-context destroyed during evaluation.

### UNCLASSIFIED (18)

See section below. No representative subset is meaningful because every entry has identical evidence: empty error, zero tool calls.

## UNCLASSIFIED Section

18 failures are tagged UNCLASSIFIED because the underlying run produced **no tool calls and an empty error string**. The categorizer had nothing to work with beyond "the agent crashed or timed out before doing anything observable."

Affected tasks span Amazon (`wv-014`, `wv-015`, `wv-016`), Apple (`wv-018`), Cambridge Dictionary (`wv-030`), ESPN (`wv-035`, `wv-036`, `wv-037`), Google Flights (`wv-044`, `wv-045`, `wv-046`), Hacker News (`wv-051`), IMDb (`wv-057`), Microsoft Learn (`wv-068`), MDN (`wv-072`), OpenAI Docs (`wv-081`), Stack Overflow (`wv-089`), and a generic flight task (`wv-005`).

**Why unclassifiable:** the v1.1 trace pipeline only captured the final answer and a top-level error string. No intermediate tool-call log, no browser-state snapshot, no stderr. With identical "empty error, no tool calls" evidence, there's no signal to distinguish a startup crash from an auth wall from a silent timeout.

**Fix:** S3 trace plumbing must persist (a) every tool-call attempt with arguments and outcome, (b) the browser console and network errors, and (c) the agent's last reasoning step before failure. Once traces land, re-categorize this bucket.

## Recommendations for S3–S5

**S3 (priority 1, unblocks everything else):**
- Land trace plumbing. Until UNCLASSIFIED shrinks, we cannot tell whether the real failure rate is 19 or 37, nor where to invest.
- Fix TOOL_BROKEN: add screenshot retry with longer timeout and fallback to text-only extraction; wrap `Page.evaluate` calls in a navigation-aware retry. Covers 5 failures directly and likely a chunk of UNCLASSIFIED.
- Fix DOM_FLAKY: detect "Execution context was destroyed" and retry on the new context. Covers 4 of 5 DOM_FLAKY plus the LinkedIn TOOL_BROKEN entries that share the same root cause.

**S4:**
- One DOM_FLAKY case (`wv-062`) is flagged for S4, suggesting it needs the richer DOM-stability layer rather than a simple retry.

**S5:**
- Tackle LOGIN_WALL: 9 failures concentrated on LinkedIn, Pinterest, X, Booking, Medium, Khan Academy. Options: authenticated session fixtures, a "skip if auth required" judge accommodation, or swapping these tasks for sites that don't require login. Decide policy before investing in auth automation.

**Expected impact if S3 fixes land cleanly:**
- TOOL_BROKEN (5) and DOM_FLAKY (4) directly resolved: +9 tasks.
- Trace plumbing likely reveals that a substantial fraction of UNCLASSIFIED (18) is also TOOL_BROKEN or LOGIN_WALL.
- Plausible pass rate after S3: 72–80%. After S5 LOGIN_WALL policy: 80–88%.
