# 27B Orchestrator Guide

How to run Sisyphus on local `qwen3.5-27b` for v1.3, with maximum reliability
and minimum Anthropic spend.

## Why this matters

v1.0-v1.2 ran Sisyphus on Opus 4.7. That cost ~$30-50 of orchestration per
sprint out of total $200-600 spends. Opus is rock-solid at long state tracking
but expensive.

v1.3 runs Sisyphus on local-vllm/qwen3.5-27b. Local = free. The trade-off is
reliability: 27B drifts on long state.

## Model assignment for v1.3

```
                      Model                          Used for
─────────────────────────────────────────────────────────────────────────
Sisyphus              local-vllm/qwen3.5-27b         Orchestration
mantle-planner        local-vllm/qwen3.5-27b         Ticket planning
mantle-executor       local-vllm/qwen3.5-27b         Code writing
mantle-frontend       local-vllm/qwen3.5-27b         UI components
mantle-auditor        anthropic/claude-opus-4-7       Audit ONLY
Vision fallback       anthropic/claude-sonnet-4-6     Browser tool vision
Productivity judge    anthropic/claude-sonnet-4-6     W7 benchmark
```

Total Anthropic spend should be: auditor passes (9 phases × 1-3 audits avg = ~20
Opus calls), plus W7's 30 Sonnet judge calls, plus W8's WV-300 regression
(judge runs across 300 tasks). Estimated $59-112 total.

## OMO configuration

Your `~/.config/opencode/oh-my-opencode.json` should have:

```jsonc
{
  "agents": {
    "sisyphus": {
      "model": "local-vllm/qwen3.5-27b",
      "fallback_models": ["anthropic/claude-opus-4-7"]
    }
  },
  "background_task": {
    "defaultConcurrency": 4,
    "providerConcurrency": {
      "local-vllm": 8,
      "anthropic":  3
    },
    "modelConcurrency": {
      "anthropic/claude-opus-4-7": 2
    },
    "staleTimeoutMs": 600000
  }
}
```

Key settings explained:

- `sisyphus.fallback_models: ["anthropic/claude-opus-4-7"]` — if 27B errors or
  returns gibberish on a specific turn, OMO bounces THAT turn to Opus and
  continues. You won't see it; the build doesn't stall.
- `defaultConcurrency: 4` — lower than the v1.1 setting of 5. 27B-Sisyphus
  tracks 4 parallel executor tickets reliably; 5+ causes coordination drift.
- `staleTimeoutMs: 600000` (10 min) — 27B can be slow on hard tickets; don't
  reap prematurely.

## What 27B-Sisyphus is good at

- **Following the SKILL.md loop discipline.** It reliably calls planner →
  executor → make verify-phase → auditor → ship.
- **JSON parsing from subagents.** The planner returns ticket arrays as JSON;
  27B handles 4-6 ticket batches fine.
- **TodoWrite updates.** Marking items completed/in-progress is reliable.
- **Commit message format.** As long as the format is in the SKILL.md, 27B
  produces it.
- **Parallel dispatch via `delegate_task`.** 27B handles 4 parallel tickets
  cleanly.

## What 27B-Sisyphus is bad at (and how to compensate)

### 1. Long horizon planning

**Problem:** 27B forgets it's at phase W4 when context grows past ~32k tokens.
It starts re-planning phases it already completed, or skipping ahead.

**Compensation:** `scripts/sisyphus-state-check.py` runs every 5 tickets. It
reads boulder.json, git tags, recent commits, and reports drift. If drift > 0,
stop and reconcile before continuing.

The state check is fast (<1s). Running it costs nothing. Skipping it costs
hours of rework.

### 2. Multi-step audit loops

**Problem:** After @mantle-auditor returns PUNCH_LIST with 5 items, 27B
sometimes dispatches fixes for items 1-3, then forgets items 4-5 exist.

**Compensation:** MAX_AUDIT_ITERATIONS = 3 (down from v1.1's 5). After 3
iterations, write BLOCKED.md and stop. Better to surface the failure than
let 27B run in circles.

Also: when @mantle-auditor returns PUNCH_LIST, IMMEDIATELY write each item
to a ticket file under `planning/phase-W*/iter-N/`. Don't trust yourself to
remember; the file is the source of truth.

### 3. Boundary recognition

**Problem:** 27B sometimes blurs the boundary between "this phase" and "next
phase" — it'll start touching W3 code while in W2.

**Compensation:** Every phase YAML has an explicit `packages_required` list.
The auditor pattern #14 (scope creep) flags any commit that touches files
outside that list. 27B will get the flag; if you see it, stop touching
those files.

### 4. State recovery after interrupt

**Problem:** If the OpenCode session gets interrupted (laptop sleep, network
glitch), 27B-Sisyphus on resume often miscounts where it was.

**Compensation:** Run `scripts/sisyphus-state-check.py` IMMEDIATELY on resume.
It tells you the actual state. Trust the script over your memory.

### 5. Commit cadence drift

**Problem:** 27B sometimes batches commits ("I'll commit when I finish this
phase") instead of pushing every 3.

**Compensation:** Hard rule in KICKOFF: push every 3 commits. Set a personal
mental rule: after every 3 ticket completions, run `git push origin main`.

## Decision tree: when to manually escalate to Opus

You can manually swap Sisyphus to Opus for a single turn if you hit any of
these:

- **State check reports drift > 0 twice in a row.** Something is genuinely
  confused. Bounce to Opus for the reconcile turn.

- **Audit loop hits iteration 2 with same items unfixed.** 27B is stuck in a
  loop. Bounce to Opus for the next dispatch.

- **You're starting a new phase and the prior phase had > 5 audit iterations.**
  State complexity is high. Start the new phase on Opus, then swap back.

- **Vision tasks fail repeatedly.** Probably means the executor needs Sonnet
  vision, not Sisyphus model. Different problem.

To manually swap for one turn, in OpenCode chat:

```
/model anthropic/claude-opus-4-7
[do the work]
/model local-vllm/qwen3.5-27b
```

OMO handles the swap; subsequent turns go back to 27B.

## When the fallback chain fires automatically

OMO's fallback_models config means if 27B:

- Returns HTTP 5xx from vLLM
- Times out (> staleTimeoutMs)
- Returns malformed JSON for an agent that's expected to return JSON
- Returns content that's clearly broken (loops, control tokens leaking)

...then OMO automatically retries that ONE turn on Opus. The build continues.
You see a small `[fallback: opus-4-7]` annotation in the OpenCode log.

This is your safety net. With the fallback enabled, the worst case isn't a
broken build — it's slightly higher Anthropic spend than projected.

## Cost monitoring

After every phase, run:

```bash
# Approximate Anthropic spend so far this sprint
grep -r "fallback: opus" .opencode/logs/ | wc -l       # fallback fires
grep -r "mantle-auditor" .opencode/logs/ | wc -l       # auditor calls
```

Each fallback fire ≈ $0.05-0.15. Each auditor call ≈ $0.30-1.00. If those
numbers add up to > 50% of the phase's projected budget, surface to user
before continuing.

## Self-check ritual

Every 5 tickets (regardless of which phase):

```bash
python3 scripts/sisyphus-state-check.py
```

Output looks like:

```
🧭 Sisyphus state check (v1.3)
  Current phase per boulder.json:  W2
  Current phase per git tags:      W2 (phase-W1-shipped is latest)
  Open tickets per planning/:      3 (W2 iter-2)
  Commits ahead of origin:         1
  Drift: 0

  Next expected action: dispatch executor for ticket 003
  Last audit verdict:   PUNCH_LIST (2 items remaining)
```

Drift > 0 means stop. Don't continue until it's 0.

## Quick-reference: 27B run rules

1. ✅ Read every phase YAML before starting it (don't trust your memory)
2. ✅ Write every ticket to disk under planning/phase-W*/iter-N/
3. ✅ Run state-check every 5 tickets
4. ✅ Push every 3 commits
5. ✅ MAX_AUDIT_ITERATIONS = 3, no exceptions
6. ✅ When in doubt about "did I do X already", check git, not memory
7. ✅ Surface fallback fires in chat ("fallback fired on turn X, Opus handled it")
8. ✅ Auditor stays Opus (mantle-auditor's model is set in .opencode/agents/)
9. ❌ Don't manually escalate to Opus on every turn (defeats the purpose)
10. ❌ Don't skip the state check because "I know where I am" (you don't)
