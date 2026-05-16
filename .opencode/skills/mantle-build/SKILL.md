---
name: mantle-build
version: 1.0.0
description: Audit-loop discipline for the Rasputin Mantle build. Activates when working on phase-R*-* work, or any commit referencing protocol/phases/. Sisyphus uses this to drive the deterministic two-agent loop.
triggers:
  - phase-R
  - mantle
  - rasputin-mantle
  - audit loop
  - PUNCH_LIST
  - PERFECT
priority: high
---

# Mantle Build Loop

When the user kicks off Mantle build work, you (Sisyphus) drive the audit loop. Two agents, one feedback cycle:

```
mantle-planner (27B) → mantle-executor × N (27B, parallel) → make verify-phase → mantle-auditor (Opus)
                          (or mantle-frontend for apps/web)         │                      │
                                ↑                                   │                      │
                                │                                   │                      │
                                └────── PUNCH_LIST ←──────── PERFECT │                      │
                                                                    │                      │
                                                                    └─→ git tag, next phase
```

You are the loop driver. The four subagents are tools. The mechanical floor is `make verify-phase-RN`. The ship gate is `mantle-auditor` returning PERFECT.

# What to do at each phase

## 1. Determine current phase

Before anything: `git tag -l 'phase-*-shipped' | sort -V | tail -1`. The next phase is the one after that tag. If no tags exist, start at R0. The full phase list is fixed: R0 → R1 → R2 → R3 → R4 → R5 → R6.

Also check `state.json` if it exists (older runs) and `boulder.json` (your own resume state). If both exist and disagree, prefer git tags as ground truth.

## 2. Plan the phase

Read `protocol/phases/phase-RN.yaml`. If `audit-log/phase-RN-iter-*.json` files exist for this phase, find the latest and read it — that's the audit punch list driving this iteration's plan.

Delegate to **`mantle-planner`** with a single message containing:
- The full phase YAML
- The audit punch list (if iter > 0)
- "Output ONLY the JSON tickets array."

You get back a JSON tickets array. Write each ticket to `planning/phase-RN/iter-N/NNN-slug.md` (frontmatter + body).

## 3. Create todos

`TodoWrite` one todo per ticket. Slug as the todo content. Mark all as `pending`.

Also add overhead todos:
- "Run make verify-phase-RN"
- "Run mantle-auditor on diff"
- "Tag phase-RN-shipped on PERFECT"

## 4. Execute tickets in parallel

For each ticket, in parallel up to 8-wide:

- If `files_in_scope` contains `apps/web` or `apps/desktop`: delegate to `mantle-frontend`
- Otherwise: delegate to `mantle-executor`

Pass the ticket file's contents + the current contents of `files_in_scope` files. Expect a unified diff back.

For each diff:
1. Mark its todo `in_progress`
2. `git apply --whitespace=fix` the diff (fall back to `git apply --3way` on first failure)
3. Run `git diff --name-only HEAD` — verify it's a subset of `files_in_scope`. If not, `git reset --hard HEAD`, re-delegate with "scope violation: <files>" appended.
4. Run the ticket's `verify` command
5. **On green:** `git add -A && git commit -m "<structured message — see below>"`. Mark todo `completed`. Print status line.
6. **On red:** `git reset --hard HEAD`, re-delegate with verify output appended. Up to 2 retries per ticket. After third failure: mark todo `cancelled` (it goes back into the next plan as a fix ticket).
7. **Push to origin every 3 successful commits** (or after each phase audit-PERFECT, whichever comes first).

## 5. Commit message format

```
phase-RN.iterM: <package>/<file> — <one-line goal>

Goal: <full ticket goal>
Ticket: planning/phase-RN/iter-M/NNN-slug.md
Verify: <verify command>  ✓
Audit: pending

🤖 mantle-executor (or mantle-frontend) via Sisyphus
```

## 6. Status line format

After every ticket (success or failure), print to chat:

```
[N/M] <slug> — <green|red|cancelled> · avg <Xm>/ticket · phase ETA <YYhZm> · phase spend $<Z.ZZ> / $<budget>
```

Compute ETA from rolling average of completed ticket durations. Spend = your running estimate from Anthropic usage so far (auditor + frontend tickets; 27B is free).

## 7. Mechanical floor

After all tickets resolve (green, red-and-fixed, or cancelled): `make verify-phase-RN`.

- **Green:** advance to audit.
- **Red:** synthesize a punch-list from the verify output, write it to `audit-log/phase-RN-iter-N.json` with `{verdict: "PUNCH_LIST", summary: "verify-phase failed", items: [...]}`, increment iteration, goto step 2.

## 8. Audit

Delegate to **`mantle-auditor`** with:
- The phase rubric (`protocol/phases/phase-RN.yaml`)
- The full diff: `git diff phase-R(N-1)-shipped..HEAD` (or root commit if R0). Truncate diff to ~40 KB if it's bigger; tell the auditor it's truncated.
- The phase-done draft (`PHASE_RN_DONE.md` if exists, else blank)

Parse the JSON verdict. Write to `audit-log/phase-RN-iter-N.json`.

- **PERFECT:** advance to ship.
- **PUNCH_LIST:** increment iteration. If iteration ≥ 5: write `BLOCKED.md` and STOP. Otherwise: goto step 2 (planner reads the punch list and emits fix tickets).

## 9. Ship

On PERFECT:
1. Write/finalize `PHASE_RN_DONE.md` (~1 page: tickets shipped, eval numbers from outputs/, cost summary from your tally, audit excerpt).
2. `git add -A && git commit -m "phase-RN: shipped"`
3. `git tag phase-RN-shipped`
4. `git push origin main --tags`
5. Mark all phase todos `completed`. Print:
   ```
   ✅ phase-RN shipped. Audit: PERFECT in M iteration(s). Total spend $X.XX. Advancing to phase-R(N+1).
   ```
6. If N < 6: goto step 1 for the next phase.
7. If N == 6: write/finalize `MANTLE_V1_RELEASED.md` over the stub. Print release summary. STOP.

## 10. Resume after interrupt

If the session is interrupted (user closes OpenCode, hits Esc, restart, etc.) and the user comes back saying "continue the mantle build":
1. Read `git tag -l 'phase-*-shipped'` → current phase
2. Check `audit-log/phase-RN-iter-*.json` → current iteration
3. Check `planning/phase-RN/iter-N/*.md` → tickets that were planned
4. Check `git log --oneline phase-R(N-1)-shipped..HEAD` → which tickets already landed
5. Resume at the right step. Don't replan tickets that already shipped.

# What you do NOT do

- **Don't edit the verifier.** `Makefile`, `protocol/phases/*.yaml`, `verify-phase.sh`, `banned-phrases.txt`. The pre-commit hook blocks this. The auditor flags it. There is no shortcut to PERFECT through the verifier.
- **Don't `kill -9` an in-flight tool call.** Wait for completion. If genuinely stuck, the user can `/session interrupt` and you resume per step 10.
- **Don't raise MAX_AUDIT_ITERATIONS (currently 5) to dodge BLOCKED.** Read the audit log. If iter 5 still has blockers, the issue is structural and needs human review.
- **Don't add `--no-sandbox`.** Ever. On any browser.
- **Don't `import anthropic` outside `apps/gateway/src/gateway/model_client.py`.**

# Where things live

- `protocol/phases/phase-RN.yaml` — rubrics. Read-only for you.
- `protocol/prompts/*.md` — the body text of the four mantle-* agents. Don't edit at runtime.
- `planning/phase-RN/iter-N/*.md` — your ticket files. You write these.
- `audit-log/phase-RN-iter-N.json` — auditor verdicts. You write these.
- `outputs/*.json` — eval results. The eval suites write these.
- `state.json` (legacy) — older orchestrator's state. Ignore unless resuming a v2 run.
- `boulder.json` (OMO) — your own resume state. Managed by OMO.

# Budgets

- **MAX_AUDIT_ITERATIONS:** 5 per phase before BLOCKED.
- **PHASE_WALL_CLOCK:** 4 hours per phase. Soft cap — print a warning at 3h, BLOCK at 4h.
- **DAILY_BUDGET_USD:** $40 default. Soft cap — pause for an hour if hit. Hard cap is your Anthropic admin workspace budget.

When you hit a budget cap, write `BLOCKED.md` with:
- Current phase, iteration, status
- Reason
- Last audit verdict
- Pointer to relevant audit-log file
- Restart instruction: "rm BLOCKED.md, then say 'resume mantle build' to me"
