# No-Cheating Policy

v1.1's headline goal is moving WebVoyager from 63% to ≥ 75%. That number only matters if it's earned. This document lists what is and isn't legitimate improvement. The S6 auditor uses it as a checklist.

## Why this exists

It is trivially easy to "improve" a benchmark by gaming the benchmark instead of the underlying capability. Examples we want to NEVER do, drawn from the AI agents literature and from things we've seen in past Mantle runs:

- **Memoization**: caching the agent's previous answer for a task and returning it on re-runs without re-doing the work.
- **Hardcoding**: matching the agent's response generation against known WebVoyager task IDs or `expected_answer` patterns.
- **Test-set contamination**: training the planner on WebVoyager tasks specifically.
- **Cherry-picking**: running each task multiple times, reporting only the best result.
- **Threshold gaming**: switching from a strict judge to a lenient judge.
- **Set substitution**: calling something "WebVoyager-100" when it's actually a different, easier set of 100 tasks.

The point of v1.1 isn't a number on a dashboard. It's an agent that genuinely works better on web tasks. If we hit 80% by cheating, we've built nothing. If we hit 72% honestly, we've built something worth building on.

## Hard rules

### CHEATING — auditor flags any of these as v1.1 BLOCKER

1. **Answer memoization.** Any code path that stores per-task answers and returns them on a subsequent run with the same task ID. This includes "warm cache" optimizations, "smart retry from previous result", or any other framing.

2. **Hardcoded patterns for known tasks.** Any agent logic that branches on `task_id` or pattern-matches WebVoyager-specific `description` strings. The agent must treat every task as if it's never seen it.

3. **Skipping hard tasks.** Removing tasks from the active set because they're failing. If a task is genuinely ungradable (e.g., TIME_SENSITIVE with a stored numerical answer that's now stale), mark it `expected-fail` and exclude from pass-rate denominator with that exclusion clearly noted. Don't silently delete.

4. **Lowering the success threshold.** Changing the judge model to a more lenient one specifically because failures need to pass. Note: upgrading the judge to a MORE capable model is fine (Sonnet 3.5 → Sonnet 4.6) as long as the change applies uniformly to all tasks.

5. **Pre-fetching from an answer key.** Any code that consults an external file, database, or API that contains the canonical WebVoyager answers.

6. **Task set substitution.** Calling something WebVoyager-100 when it's not. The 100 tasks must be exactly the 100 from `eval/webvoyager-100/tasks.yaml` as of v1.0's R6 ship.

7. **Best-of-N reporting.** Running each task K times and reporting only the run that passed. Single-attempt only, unless multi-attempt is a permanent feature of the agent (in which case it counts as the agent's normal behavior and the K runs use the same compute budget for all tasks, including ones that pass on the first try).

8. **Judge bias.** Modifying the judge prompt to be more accepting of borderline answers specifically when the agent is borderline. Judge prompt improvements must be ablation-tested: do they change which tasks pass in a way unrelated to task difficulty?

9. **Result selection.** Running with multiple planners, choosing the best per task, reporting an oracle-best aggregate as if it were a single agent. We can publish per-planner results side by side. We cannot publish a "best of all planners per task" as one number.

10. **Vague success.** Reporting "approximately 75%" or "consistently in the 70s" when the actual number is below 75. Numbers are exact or they're meaningless.

### NOT CHEATING — auditor accepts these as legitimate improvements

1. **Better browser primitives.** Waits, retries, multi-strategy element selectors, screenshot capture, session persistence, smarter scrolling. These apply uniformly to all tasks and they reflect real engineering improvements.

2. **Vision-language fallback.** When the DOM doesn't contain the information the agent needs, falling back to screenshot + VLM is a legitimate capability. It costs more, but it works on tasks that previously couldn't.

3. **Self-correction loops.** Agent re-evaluates its progress and changes strategy on its own. This is general reasoning, not task-specific cheating.

4. **Better planner prompting.** Improving the system prompt for the planner to be clearer about how to break down tasks. As long as the prompt doesn't mention WebVoyager or any specific task structure, it's just better engineering.

5. **Better judge prompting.** Improving the judge's prompt to normalize obvious format issues (Unicode normalization, "the answer is X" → "X", etc.) is fair — but the change must apply uniformly and be ablation-tested.

6. **Stronger general-purpose models.** Using GPT-5.5 instead of GPT-4 is fine. Using Sonnet 4.6 vision instead of Sonnet 4.5 vision is fine. The model upgrade applies to everything, not just hard tasks.

7. **Expanding the test set.** Adding more tasks makes the benchmark harder, not easier. WebVoyager-300 (100 original + 100 from the official test set + 100 in-house validation) is more credible than WebVoyager-100. We expand, never contract.

8. **Parallel verification.** Running two strategies in parallel and voting on the answer when they disagree. This is the agent's normal behavior on all tasks. Costs 2× compute, gives 1× compute-equivalent reliability. Fine.

9. **Caching infrastructure.** Caching DOM parses, screenshot OCR, search results — anything that's task-independent. Cache must NOT key on task ID.

10. **Reading the WebVoyager paper.** Understanding what the benchmark tests and why is encouraged. Reading the test set to overfit on it is not.

## The grey area

Some things are subtle. The auditor's job is to call these out and have the planner think through whether they're cheating or not:

- **Failure category-specific fixes.** S3 fixes DOM_FLAKY failures. Is that overfitting to WebVoyager? Answer: no, if the fix (better waits, retries) applies to ALL web tasks, not just WebVoyager. Yes, if the fix is "when task is wv-005, use selector X." The line: does the fix generalize?

- **Prompt engineering on the planner.** Making the planner better at "find a specific value on a webpage" is fine. Making the planner better at "WebVoyager-style multi-hop research" is borderline — if the WebVoyager test set was the only example used to derive that phrasing, it's overfitting.

- **Increasing tool retry budget.** Going from 1 retry to 3 retries per tool is fine if it applies uniformly. Going from 3 to 10 specifically because some WebVoyager tasks need it is borderline — does the 10-retry budget actually help in real use, or only when the agent is trying to game a benchmark?

When in doubt: ask. The agent during S3-S5 should surface decisions like this to the user, not silently implement them.

## Auditor mechanics

At S6 audit time, `mantle-auditor` checks for:

- `grep -rn 'task_id\\s*==\\s*"wv-'` (hardcoding)
- `grep -rn 'memo\\|cache.*answer\\|answer.*cache'` (memoization)
- `eval/webvoyager-100/tasks.yaml` unchanged from R6-shipped tag (no task substitution)
- `eval/webvoyager-100/runner.py` doesn't read from external answer files (no answer-key pre-fetch)
- Judge model in S6 same family or stronger than R6 baseline (no leniency switch)
- Per-task results in S6 output show single-attempt-only (no best-of-N inflation)

Plus the auditor reads `MANTLE_V1_1_RELEASED.md` and verifies the numbers stated there match the actual eval output files. Any discrepancy is a BLOCKER.

## What if we honestly can't hit 75%?

If after S5 the WebVoyager-100 number is 70-74%, we have two honest options:

1. **Ship at 72%.** Update the release report to say `WebVoyager-100 = 72% (target was 75%; we missed it; here's the per-category breakdown showing what we couldn't fix)`. This is more valuable than gaming to 75%.

2. **Keep working.** Identify the largest remaining failure cluster from the S2 taxonomy, add an S7 phase that targets specifically that cluster, run the loop.

Option 1 is the better engineering call most of the time. A real 72% beats a gamed 75%.
