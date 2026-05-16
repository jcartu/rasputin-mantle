# The Audit Loop

The whole build runs on one feedback cycle:

```
27B does the work  →  Opus audits  →  PERFECT or PUNCH_LIST  →  loop until PERFECT
```

Two agents. One verdict. Either ship it or fix it. The orchestrator drives the loop from inside the OpenCode chat — you watch every tick.

## Why this shape

The first attempt at this build (May 2026) shipped seven phases of commits and delivered ~30% of the intended capability. The reason was a category error: the same agent that wrote the code was also the agent that "reviewed" it. Without an adversarial reviewer, every Potemkin route looked like a shipped feature.

This build separates execution from audit. The auditor (`mantle-auditor`, Opus 4.7) only sees finished work — the full diff vs the previous phase tag, the phase rubric, and the phase-done draft. It never participates in planning or coding. Its only output is a JSON verdict.

The executors (`mantle-executor` for backend, `mantle-frontend` for apps/web and apps/desktop) do all the actual work. They write code, one ticket each, returning unified diffs. The planner (`mantle-planner`) decomposes phase rubrics into tickets and converts audit punch lists into fix tickets.

The orchestrator is the dispatcher. It owns the state machine — what phase, what iteration, what tickets are in flight. It uses native TodoWrite to track ticket progress so you can see what's happening at a glance. It uses `delegate_task` to call the four mantle-* subagents. It runs the mechanical floor (`make verify-phase-RN`) as a cheap pre-audit gate.

## The verdicts

The auditor returns exactly one of two verdicts:

**PERFECT.** Every rubric item is genuinely satisfied. No Potemkin code, no lazy tests, no dead paths, no skipped error handling, no security smells, no scope creep, no naming drift. The orchestrator tags the phase, advances.

**PUNCH_LIST.** Anything less than PERFECT. Each item gets:

- **severity**: blocker | nit
- **file**: path the issue lives at
- **line**: optional line number
- **issue**: one sentence stating what's wrong
- **fix_hint**: one concrete instruction the executor applies verbatim

The orchestrator passes the punch list back to `mantle-planner`, which converts each blocker into a fix-ticket, groups related nits, and emits the new ticket list. The orchestrator then dispatches the fix tickets in parallel just like any other batch. Audit again. Loop until PERFECT or until iteration cap (5 default) blows.

## Strict mode

This build runs in strict mode by default. The auditor is aggressive. It flags 16 specific patterns as blockers, listed in full in `.opencode/agents/mantle-auditor.md`. Highlights:

1. Routes returning hardcoded synthetic data (the `asyncio.sleep` + fake JSON pattern from the May 2026 audit)
2. Tests asserting services are dead (`status_code == 503` for services that should be live)
3. Tests passing by tautology (assertions on stubbed return values)
4. Routes returning 200 with empty payloads when they should return 501
5. Edits to the verifier (Makefile, phase YAMLs, verify-phase.sh) — flat-out fraud
6. Skipped error handling, swallowed exceptions
7. Functions with no real implementation behind a passing test
8. Dead code paths (unused imports, unreachable branches)
9. Hardcoded secrets, paths, ports, URLs
10. New dependencies without license review
11. Direct anthropic/openai SDK imports outside the designated client
12. Security smells (`--no-sandbox`, `eval`/`exec`, `shell=True` with interpolation)
13. Naming drift (skill named X in plan, Y in code)
14. Scope creep (files touched outside declared packages)
15. Missing phase artifacts
16. Stubbed or skipped eval suites

Nits are reserved for genuinely embarrassing issues (typos, dead imports). The auditor doesn't moralize about taste.

Every audit verdict is persisted to `audit-log/phase-RN-iter-N.json`. Forensic trail.

## The iteration cap

After `MAX_AUDIT_ITERATIONS` (default 5) failed audits in a single phase, the orchestrator writes `BLOCKED.md` and stops. This isn't a failure mode — it's a deliberate floor. If five rounds of "plan fix → execute → audit" haven't reached PERFECT, the issue is probably:

- The rubric is too aggressive for this phase's actual capability
- A core architectural decision is wrong and a single fix-ticket can't repair it
- The 27B is repeatedly hallucinating the same wrong fix
- A dependency or service is broken in a way the executor can't fix in scope

Any of these requires human judgment. Raise the cap only after reading the audit log and deciding the issue is genuinely close-but-not-quite.

## Mechanical floor

Before each audit, the orchestrator runs `make verify-phase-RN`. This is a cheap mechanical gate that catches the obvious failures without spending Opus tokens:

- All declared packages pass their own `make verify` or pytest suite
- All declared `artifacts` exist and are non-empty
- All `integration_tests` pass
- All `eval_suites` meet their `minimum_pass_rate` (read from each suite's output JSON)
- No `forbidden_patterns` appear in the code (grep)

If the floor fails, the orchestrator skips the audit and synthesizes a punch list from the verify output, then re-plans — so the executors fix the obvious before Opus weighs in on the subtle.

## Cost shape

Per phase, typical Anthropic spend at default settings:

| Activity | Calls | $ per call | Subtotal |
|---|---|---|---|
| Audit (Opus 4.7) | 3-5 | ~$0.15 | $0.50-0.75 |
| Frontend (Sonnet 4.6, R4+R6 only) | 6-12 | ~$0.10 | $0.60-1.20 |
| Judge for evals (Sonnet) | 100-200 | ~$0.005 | $0.50-1.00 |
| **Total per phase** | varies | | **$2-5** |

Local 27B is free (your GPU rental is sunk cost). Across all seven phases the full run lands around **$20-40** of Anthropic spend.

The KICKOFF.txt sets a soft daily cap (`DAILY_BUDGET_USD`, default 40). The real ceiling lives in Anthropic admin's per-workspace daily budget.

## Resuming after a block

`BLOCKED.md` contains:

- Current phase and iteration
- The reason the loop bailed
- The full state dump
- Pointer to the audit log

Typical resume flow:

1. Read the latest `audit-log/phase-RN-iter-N.json`
2. Decide: is the auditor right? (almost always yes — the strict prompt has very few false positives)
3. If yes: fix the underlying issue manually, then `rm BLOCKED.md` and say "resume mantle build" in the OpenCode chat. The orchestrator picks up at the same phase/iteration and re-audits.
4. If the auditor is wrong about something subtle: refine `.opencode/agents/mantle-auditor.md` (the change will be visible in the next audit), commit, then resume.
5. If the phase is structurally too hard: split it. Edit the YAML rubric to scope smaller, commit with `ALLOW_VERIFIER_EDIT=1 git commit`, then resume.

You don't raise `MAX_AUDIT_ITERATIONS` to make BLOCKED go away. Read the log.
