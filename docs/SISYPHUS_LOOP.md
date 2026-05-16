# The Sisyphus-Driven Loop

The build runs entirely inside OpenCode. Sisyphus is the loop driver. Four custom subagents (`mantle-planner`, `mantle-executor`, `mantle-frontend`, `mantle-auditor`) are the workers. You watch every tick happen in the OpenCode chat panel — every TodoWrite update, every subagent dispatch, every commit, every audit verdict.

No Python orchestrator. No Docker container running a background loop. No `--restart unless-stopped`. The "state" lives in three places: git tags, `audit-log/*.json` files, and OMO's `boulder.json`. Sisyphus can resume from any kill point by reading those three.

## What you see in the OpenCode window

Roughly this, scrolling past for hours/days:

```
You: ultrawork: Build Rasputin Mantle v1 end to end. [pastes KICKOFF.txt]

Sisyphus: Reading the skill and docs...
          [reads .opencode/skills/mantle-build/SKILL.md]
          [reads docs/RASPUTIN_MANTLE_BUILD_PLAN.md]
          [reads docs/AUDIT_LOOP.md]
          [reads docs/SISYPHUS_LOOP.md]
          [reads protocol/phases/phase-R0.yaml]
          [runs git tag -l 'phase-*-shipped']

          Current phase: R0 (no prior tags). Expecting ~6 tickets for protocol install.
          ETA ~25 minutes. Starting.

          [TodoWrite] 6 todos created:
            ☐ 001-protocol-files-installed
            ☐ 002-pre-commit-hook
            ☐ 003-makefile-symlink
            ☐ 004-env-validation
            ☐ 005-health-check
            ☐ 006-phase-R0-done-report

Sisyphus: Delegating to @mantle-planner with phase-R0.yaml...
          [@mantle-planner: 2.3s, returned 6 tickets]
          [writes planning/phase-R0/iter-0/001-protocol-files-installed.md ... 006-...md]

Sisyphus: Dispatching tickets in parallel...
          [@mantle-executor 001-protocol-files-installed: 47s]
            ↳ diff applied, verify green, committed
          [@mantle-executor 002-pre-commit-hook: 28s]
            ↳ diff applied, verify green, committed
          ...
          [1/6] 001-protocol-files-installed — green · avg 47s/ticket · phase ETA 4m · spend $0.00
          [2/6] 002-pre-commit-hook — green · avg 37s/ticket · phase ETA 2m30s · spend $0.00
          ...
          [pushes 3 commits to origin]
          ...
          [6/6] 006-phase-R0-done-report — green · avg 41s/ticket · phase ETA 0s · spend $0.00

Sisyphus: Running make verify-phase-R0...
          ✓ green

Sisyphus: Delegating to @mantle-auditor with diff of phase-R0..HEAD...
          [@mantle-auditor: 18s, $0.14]

          ─────────────────────────────────────────────
           phase-R0 audit · iter 0 · verdict: PERFECT
           summary: All protocol files present and validated. Pre-commit hook active. 
                    Health check passes for vLLM and Anthropic.
          ─────────────────────────────────────────────

          [writes PHASE_R0_DONE.md]
          [git tag phase-R0-shipped]
          [git push origin main --tags]

          ✅ phase-R0 shipped in 1 iteration. Spend $0.14. Advancing to phase-R1…

          [TodoWrite] 6 R0 todos marked completed.
          [reads protocol/phases/phase-R1.yaml]
          ...
```

Visible. Auditable. Pause-able with `Esc`. Resumable.

## The four custom subagents

| Agent | Model | Mode | Role |
|---|---|---|---|
| `mantle-planner` | local-vllm/qwen3.5-27b | subagent (read-only) | Reads phase YAML + optional punch list. Returns JSON ticket array. |
| `mantle-executor` | local-vllm/qwen3.5-27b | subagent (read + bash) | Implements one backend ticket. Returns unified diff. |
| `mantle-frontend` | anthropic/claude-sonnet-4-6 | subagent (read + bash) | Implements one apps/web or apps/desktop ticket. Returns unified diff. |
| `mantle-auditor` | anthropic/claude-opus-4-7 | subagent (read-only) | Audits full phase diff vs rubric. Returns PERFECT or PUNCH_LIST JSON. |

They live as markdown files in `.opencode/agents/`. Frontmatter sets model, mode, tools, temperature. Body is the system prompt. Sisyphus calls them via `delegate_task(subagent_type="mantle-auditor", prompt="<phase rubric + diff + done draft>")` etc.

`mantle-executor` and `mantle-frontend` can be parallel-dispatched. Sisyphus issues up to 8 concurrent `delegate_task` calls (configurable per OMO's concurrency settings). They run as parallel subagent sessions, each with its own context — no cross-talk.

`mantle-auditor` runs sequentially after the parallel batch resolves. It's the gate.

## State, persistence, resume

Three sources of truth, in order:

1. **Git tags** (`phase-RN-shipped`). The unambiguous record of what's shipped. Use `git tag -l 'phase-*-shipped' | sort -V | tail -1` to find the latest. Next phase = the one after.

2. **`audit-log/phase-RN-iter-N.json`**. Files written by Sisyphus after every auditor call. Counting these gives you the iteration count within the current phase. Reading the latest gives you the active punch list.

3. **OMO's `boulder.json`**. OMO's own resume state — what subagent was mid-call, which tools are in flight. Sisyphus reads this on session start and continues from the boulder.

If you kill the OpenCode session mid-phase: open OpenCode again on the same repo, paste KICKOFF.txt (or just say "continue the mantle build"). Sisyphus reads the three sources, figures out where it was, and resumes. No replanning of tickets that already shipped (it checks `git log --oneline phase-R(N-1)-shipped..HEAD`).

## Concurrency tuning

OMO's parallel agent settings control how wide Sisyphus dispatches:

```json
// In opencode.json or ~/.config/oh-my-opencode/oh-my-opencode.json
{
  "background_tasks": {
    "max_concurrent_per_provider": {
      "local-vllm": 8,
      "anthropic": 4
    }
  }
}
```

Match `local-vllm` concurrency to your vLLM's `--max-num-seqs` (i.e. how many concurrent requests your GPU can serve). For a 27B model on a single H100, 8 is comfortable. On 2x H100s with tensor parallel, 16. On a single A100 40GB, 4.

Anthropic concurrency is mostly for Sonnet (frontend tickets running in parallel during R4 and R6). Opus auditor runs sequentially anyway, so 4 is plenty.

## When Sisyphus stops on its own

Three terminal states:

**`MANTLE_V1_RELEASED.md` written.** R6 shipped and the planner replaced the orchestrator's stub release report with the real one (eval numbers, cost summary, dependency list, reproduction recipe). You're done. Read the file, push it, brag.

**`BLOCKED.md` written.** Sisyphus hit a wall — iteration cap (5 audit rounds without PERFECT), phase wall clock (4h default), or a structural issue the auditor keeps flagging. The file names the phase, iteration, reason, and pointer to the relevant `audit-log/phase-RN-iter-N.json`. Resume protocol:

1. Read `BLOCKED.md`.
2. Read the latest `audit-log/phase-RN-iter-N.json`. Is the auditor right? (Almost always yes.)
3. Fix the underlying issue manually OR refine the prompt OR split the phase rubric (use `ALLOW_VERIFIER_EDIT=1 git commit` if editing a phase YAML).
4. `rm BLOCKED.md`.
5. Say "resume mantle build" in the chat. Sisyphus picks up.

**Budget cap.** Soft daily budget hit ($40 default). Sisyphus prints a warning and either sleeps an hour and continues, or — if you're using Anthropic admin workspace budgets — gets 429'd and writes BLOCKED.md. The hard ceiling lives at Anthropic admin, not in this repo.

## What you do not do

- Don't edit `state.json` or `boulder.json` by hand. If you need a clean slate: `rm state.json boulder.json` (Sisyphus will re-derive from git tags).
- Don't `kill -9` an in-flight subagent call. Use `Esc` (or your configured `session_interrupt` keybind) — Sisyphus saves boulder state cleanly on SIGINT.
- Don't raise MAX_AUDIT_ITERATIONS to dodge BLOCKED. The cap exists so the build doesn't drift into infinite "fix this, no fix that" loops.
- Don't disable the pre-commit hook. It's the cheapest line of defense against verifier edits.
- Don't run two Sisyphus sessions against the same repo concurrently. The boulder won't merge cleanly. One session per repo.

## What "completely unattended" looks like

You won't watch every tick. The OpenCode chat window scrolls. You start it, sleep, wake up, scroll up to see what happened. That's fine:

- TodoWrite shows progress at a glance — completed todos persist.
- Status lines after every ticket give you scannable progress.
- Git tags (`phase-R0-shipped` through `phase-R6-shipped`) are the discrete milestones.
- Audit log files have full diagnostic info if you want to drill in.
- BLOCKED.md is the only thing that requires your attention.

Drop your laptop lid, walk away. When you come back, scroll the chat to see what shipped. Or just `git log --oneline` in the repo.
