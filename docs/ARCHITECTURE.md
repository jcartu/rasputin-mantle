# Architecture

```
   your dev machine                                          cloud
   ────────────────                                          ─────
                                                            
   OpenCode Desktop 1.3.7                                    vLLM (your GPU box)
   ├── Sisyphus (Opus 4.7, OMO orchestrator)                 Qwen3.5-27B-Instruct
   │     │
   │     ├── delegate_task(subagent_type="mantle-planner")   ─── HTTP ──→ vLLM
   │     ├── delegate_task(subagent_type="mantle-executor")  ─── HTTP ──→ vLLM (×N parallel)
   │     ├── delegate_task(subagent_type="mantle-frontend")  ─── HTTPS ─→ api.anthropic.com (Sonnet 4.6)
   │     ├── delegate_task(subagent_type="mantle-auditor")   ─── HTTPS ─→ api.anthropic.com (Opus 4.7)
   │     │
   │     ├── TodoWrite (built-in)
   │     ├── bash: git apply, git commit, git push, make verify-phase-RN
   │     ├── file ops on ~/dev/rasputin-mantle/
   │     └── boulder.json (OMO resume state)
   │
   └── (terminal: chat panel shows every step in real time)
                                                            
                                                            
                                                            
                 docker compose support services    (localhost or QNAP)
                 ──────────────────────────
                 ├── postgres (cost wall, memory, scheduler state)
                 ├── redis (APScheduler jobs)
                 ├── neko (Live Computer View, R4)
                 ├── faster-whisper (STT, R6)
                 ├── kokoro (TTS, R6)
                 └── rasputin-memory (LoCoMo memory service, R5)
```

## Why this shape

**OpenCode is the runtime.** Sisyphus drives the entire build from inside the OpenCode chat. There's no separate orchestrator daemon, no container running a Python loop, no `--restart unless-stopped`. If OpenCode is open, the build is running. If you close it, it stops. If you reopen it, you say "resume" and Sisyphus picks up from boulder + git tags.

**vLLM is your existing infrastructure.** You already run a Qwen3.5-27B-Instruct via vLLM somewhere. The four `mantle-planner` / `mantle-executor` subagents talk to it via OpenCode's openai-compatible provider. If you swap vLLM for sglang or your own stack, change `VLLM_BASE_URL` — nothing else.

**Anthropic is the paid surface.** Opus auditor: ~$0.15/call, 3-5 calls per phase. Sonnet frontend: ~$0.10/call, only for apps/web and apps/desktop tickets. Sonnet judges: pennies. Total $20-45 across the full build.

**Support services live on docker compose.** Wherever you have Docker and want a stable home for postgres/redis/neko/STT/TTS/memory — your dev machine, the QNAP, a cheap VPS, doesn't matter. `infra/compose.dev.yml` is environment-agnostic.

## The four custom subagents

| Agent | Model | Mode | Tools | Role |
|---|---|---|---|---|
| `mantle-planner` | local-vllm/qwen3.5-27b | subagent | read-only | Reads phase YAML + optional punch list. Returns JSON tickets. |
| `mantle-executor` | local-vllm/qwen3.5-27b | subagent | read + bash | One backend ticket → unified diff. |
| `mantle-frontend` | anthropic/claude-sonnet-4-6 | subagent | read + bash | One apps/web or apps/desktop ticket → unified diff. |
| `mantle-auditor` | anthropic/claude-opus-4-7 | subagent | read-only | Audits phase diff vs rubric. JSON verdict. |

Defined in `.opencode/agents/<name>.md` — YAML frontmatter (mode, model, tools) + system prompt body. OpenCode loads them at session start. Sisyphus sees them in its tool list and routes work to them via `delegate_task`.

## Data flow during a phase

1. **PLANNING.** Sisyphus reads `protocol/phases/phase-RN.yaml`. Delegates to `mantle-planner` with the rubric (and last audit punch list, if any). Receives JSON ticket array. Writes one ticket file per entry to `planning/phase-RN/iter-N/NNN-slug.md`. Calls TodoWrite with one todo per ticket.

2. **EXECUTING.** Sisyphus dispatches tickets in parallel via `delegate_task(..., run_in_background=true)`. For each ticket: agent receives ticket body + files in scope, returns unified diff. Sisyphus `git apply`s it, checks scope, runs verify, commits on green or rolls back and retries.

3. **VERIFYING.** Sisyphus shells `make verify-phase-RN`. On red: synthesize punch list from verify output, write to `audit-log/`, increment iteration, goto step 1. On green: advance to AUDITING.

4. **AUDITING.** Sisyphus computes the diff vs previous phase tag, delegates to `mantle-auditor` with rubric + diff + phase-done draft. Auditor returns JSON. Sisyphus persists to `audit-log/phase-RN-iter-N.json`. On PERFECT: SHIPPING. On PUNCH_LIST: increment iter, goto step 1.

5. **SHIPPING.** Sisyphus writes/finalizes `PHASE_RN_DONE.md`. `git add -A && git commit -m "phase-RN: shipped" && git tag phase-RN-shipped && git push origin main --tags`. Advances current_phase. If R6 just shipped: write `MANTLE_V1_RELEASED.md`, stop.

## Failure containment

- **A ticket fails:** up to 2 retries with verify feedback. After exhaustion: the ticket is recorded as red and the next planning round emits a fix-ticket.
- **>50% tickets fail in a round:** treat as planning problem. Synthesize punch list from failures and re-plan.
- **Phase exceeds wall clock:** write BLOCKED.md, stop.
- **MAX_AUDIT_ITERATIONS hit:** same.
- **vLLM unreachable:** subagent fails, normal retry path.
- **Anthropic unreachable:** subagent retries with backoff. After three failures, BLOCKED.

## Repo invariants

- `.opencode/` is owned by the protocol — never edited at runtime by phase work.
- `protocol/` likewise — never edited at runtime except via `ALLOW_VERIFIER_EDIT=1`.
- `apps/` and `packages/` are where phase tickets live.
- `infra/` is docker compose for support services. Phase tickets shouldn't modify this.
- `eval/` holds benchmark harnesses. Each writes `outputs/<name>.json`.
- `audit-log/` and `planning/` are Sisyphus-managed. Don't commit by hand.
- `outputs/` is gitignored except for the final eval results bundled into PHASE_RN_DONE.md.
