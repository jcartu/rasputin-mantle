# WebVoyager Failure Categories

Taxonomy S2 uses to classify the 37 failures from v1.0's WebVoyager-100 run (and any future run). Each failure is assigned exactly one category — the one that explains the root cause, not just the surface symptom.

Categories are ordered by what we can do about them (fixable → not fixable).

---

## DOM_FLAKY — race conditions and element-not-found

**Symptom:** the agent's tool call fails or returns wrong data because the page wasn't in the state the agent expected.

**Diagnostic signals:**
- `click` returns `Error: element not found at selector "..."` but the element exists when you check the screenshot manually
- `extract_text` returns empty string for a section that's clearly populated on the page
- Tool succeeds but with stale data from before the page navigated
- The same task succeeds on a re-run because timing happened differently

**Fix in S3:**
- Use `page.wait_for_load_state("networkidle")` after every navigation, before any subsequent action
- Add retry-with-backoff on element-not-found: 3 attempts, 500ms / 1s / 2s intervals
- Add explicit `wait_for_selector(..., state="visible")` before clicks
- Capture a screenshot before every action to confirm the page state matches the agent's mental model

**Expected gain:** 6-10 of the 37 failures.

---

## VLM_NEEDED — DOM is opaque, screenshot reasoning required

**Symptom:** the page renders content via canvas, virtual scrolling, lazy-loaded shadow DOMs, or so much JS that the DOM doesn't contain readable text where humans see text.

**Diagnostic signals:**
- `extract_text` returns mostly empty strings or only nav/footer chrome
- `query_selector("text=<thing the user sees>")` returns null even though "thing" is visible in the screenshot
- The page is a single `<canvas>` or has `aria-hidden="true"` on the meaningful content
- Charts, maps, custom data viz components

**Fix in S4:**
- After DOM extraction returns low confidence (`text.strip() == ""` or contains only nav/footer markers), capture screenshot
- Route screenshot + the user's question to Claude Sonnet 4.6 vision: "Where is X in this screenshot? Return bounding box."
- Hybrid mode: DOM-first (cheap), vision-fallback (expensive). Cap at 3 vision calls per task.

**Expected gain:** 5-10 of the 37 failures.

---

## MULTI_HOP_LOST — agent took wrong path, can't recover

**Symptom:** task requires 4+ tool calls to navigate; agent made a wrong choice early, then continued down that path without recognizing the mistake.

**Diagnostic signals:**
- Task succeeds on simpler benchmarks but fails when hop count > 3
- Agent's `step_log` shows backtracking attempts that don't actually navigate back
- Final answer is plausibly related to the task but factually wrong
- Agent confidently outputs an answer drawn from a similar but wrong page

**Fix in S5:**
- After every 3 tool calls, the agent self-evaluates: "Compared to the task goal, am I closer than I was 3 steps ago?"
- If self-eval returns "no" twice in a row, the agent must change strategy (new search query, navigate up the breadcrumb, try a different result)
- Add a "task progress" signal that the agent reports each step: `progress_score: 0.0-1.0`

**Expected gain:** 4-7 of the 37 failures.

---

## ANSWER_MALFORMED — right info found, wrong format reported

**Symptom:** agent's final answer contains the correct fact but in a format the LLM judge doesn't accept.

**Diagnostic signals:**
- Judge says FAIL but the agent's answer mentions the expected value
- "1903" expected, agent said "in the year 1903 Marie Curie shared the Nobel Prize"
- "C8H10N4O2" expected, agent said "The molecular formula of caffeine is C₈H₁₀N₄O₂" (with subscript Unicode)
- "144, 233, 377, 610, 987" expected, agent said "The first five Fibonacci numbers above 100: 144 (12th term), 233, 377, 610, 987"

**Fix in S5:**
- Better answer-extraction prompt: "Output ONLY the literal answer, no surrounding prose, no Markdown formatting, no parenthetical context."
- Normalize Unicode characters (subscripts, superscripts) to ASCII before grading
- Add a `final_answer` field to the agent's response separate from the `narration` field

**Expected gain:** 3-5 of the 37 failures.

---

## TOOL_BROKEN — actual bug in our browser primitives

**Symptom:** a specific tool consistently fails in a deterministic way that suggests our implementation, not the page.

**Diagnostic signals:**
- Every task using a specific tool fails identically
- The error message points to our code (stack trace shows our file, not Playwright internals)
- Manual replay of the page in a normal browser shows nothing weird

**Fix in S3:**
- Whichever tool is broken, fix it. This is just bugs.
- Add regression test for the specific failure scenario.

**Expected gain:** 1-4 of the 37 failures.

---

## LOGIN_WALL — site requires authentication

**Symptom:** task requires accessing content behind a login the agent has no credentials for.

**Diagnostic signals:**
- Page redirects to `/login` or `/signin` after navigation
- 401 or 403 HTTP status on direct API access
- Page shows a "Please sign in" prompt

**Fix:** Not fixable without violating the benchmark. Two options:
1. Mark as `expected-fail: login_wall` in the task definition. The failure still counts against pass rate honestly.
2. (Optional, v1.2+) Add a session-cookie-injection mechanism for opted-in tasks where the user provides credentials. Out of scope for v1.1.

**Expected gain:** 0 (we honestly take this as a failure).

---

## CAPTCHA — bot detection triggered

**Symptom:** site presents a CAPTCHA or rate-limits the agent.

**Diagnostic signals:**
- Cloudflare interstitial page
- reCAPTCHA / hCaptcha widget
- HTTP 429 / 503 with bot-detection markers
- IP ban / IP block message

**Fix:** Per our security stance, we do NOT bypass CAPTCHAs. The agent reports the CAPTCHA and fails the task.

We CAN add: politer browsing (realistic delays, residential user agent, proper Accept-Language, no aggressive parallel requests to the same domain). This reduces false-positive bot detection without bypassing real bot detection.

**Expected gain:** 1-2 of the 37 failures (the false-positive cases).

---

## TIME_SENSITIVE — answer changes since benchmark was authored

**Symptom:** task asks for "current" or "latest" or "now" data, and the agent's correct answer doesn't match the expected_answer the benchmark stored.

**Diagnostic signals:**
- Task includes "today", "this week", "latest", "currently"
- expected_answer is a specific value (stock price, weather temp) that's volatile
- Agent's answer is also a specific value but different — both are valid for their moment

**Fix:** This is a benchmark grading flaw, not an agent flaw. Two options:
1. Mark as `grading: relative` in the task definition — the judge accepts any answer of the same TYPE and rough magnitude.
2. Mark as `expected-fail: time_sensitive` and exclude from the pass-rate computation.

For S6's release report we publish two numbers: raw pass rate AND time-adjusted pass rate that excludes TIME_SENSITIVE tasks.

**Expected gain:** 2-3 of the 37 failures (counted in the time-adjusted number).

---

## JUDGE_HARSH — LLM judge made a wrong call

**Symptom:** the agent gave a clearly correct answer, the judge said FAIL.

**Diagnostic signals:**
- Manual review of the agent's answer obviously matches the expected_answer
- Judge's reasoning (if available) shows a misunderstanding

**Fix:** We do NOT make the judge more lenient (that's cheating). We CAN:
1. Use a more capable judge model (Sonnet 4.6 instead of Sonnet 3.5).
2. Improve the judge prompt to specifically allow common acceptable variations (Unicode normalization, "the answer is X" wrapping, etc.).

These changes apply uniformly to ALL tasks, not just failing ones. That's not cheating.

**Expected gain:** 0-2 of the 37 failures.

---

# Output format for S2

S2 writes `outputs/v1_1/failure-taxonomy.json` with shape:

```json
{
  "source_run": "outputs/multi-model/gpt-5-5.json",
  "total_failures": 37,
  "categorized_at": "2026-05-17T...",
  "categorizer_model": "claude-sonnet-4-6",
  "by_category": {
    "DOM_FLAKY": 8,
    "VLM_NEEDED": 7,
    "MULTI_HOP_LOST": 6,
    "ANSWER_MALFORMED": 4,
    "TOOL_BROKEN": 3,
    "LOGIN_WALL": 2,
    "CAPTCHA": 1,
    "TIME_SENSITIVE": 3,
    "JUDGE_HARSH": 1,
    "UNCLASSIFIED": 2
  },
  "failures": [
    {
      "task_id": "wv-005",
      "task_description": "Find a cheap flight from JFK to LAX next month.",
      "agent_answer": "(agent's actual answer)",
      "expected_answer": "(from task def)",
      "category": "DOM_FLAKY",
      "evidence": "Step 3 returned element-not-found on 'select-departure-date' selector; screenshot at step 3 shows the date picker visible. Race condition on calendar widget hydration.",
      "fixable_in_phase": "S3",
      "estimated_fix_effort": "low"
    }
  ]
}
```

Every failure must have a category (no failure left unclassified) and evidence (a one-sentence explanation pointing at logs, screenshots, or step data). `UNCLASSIFIED` is allowed only when none of the above categories fit and we need to add a new one.

The categorizer is Sonnet 4.6 (not Opus — too expensive at this scale). The categorization itself is mechanical: read the task, read the agent's trace, pick the category that best matches the signals.
