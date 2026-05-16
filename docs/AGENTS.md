# AGENTS.md

The orchestration map for whoever (human or LLM) lands in this repo.

## What this repo is

Rasputin Mantle is a self-hosted Manus-equivalent: an agent platform you can give a goal and have it work, with a live computer view, parallel research, voice, and a desktop app. The build is being assembled across seven phases (R0 → R6) by **Sisyphus** (OMO's orchestrator agent, running on Opus 4.7) driving a two-agent audit loop: 27B Qwen does the work, Opus audits.

## Map

```
~/dev/rasputin-mantle/
├── apps/
│   ├── gateway/        FastAPI; routes Anthropic + vLLM + cost wall + sessions
│   ├── web/            Next.js 15; user-facing UI; Live Computer View
│   └── desktop/        Tauri 2; native wrapper around apps/web
├── packages/
│   ├── browser/        Playwright + Chromium; agent's browser tool
│   ├── codeact/        Python action-loop primitives
│   ├── sandbox/        ComputeSDK wrapper (E2B + Daytona)
│   ├── skills/         SKILL.md loader and registry
│   ├── voice/          Faster-Whisper + Kokoro pipeline
│   ├── mcp-host/       MCP server host
│   ├── scheduler/      APScheduler + Redis jobs
│   ├── wide-research/  Parallel subagent dispatcher
│   └── shared/         Pydantic schemas
├── kernel/             git submodule → rasputin-omnitool (28 capabilities)
├── memory/             git submodule → rasputin-memory (LoCoMo 77.7%)
├── infra/              Docker support stack (postgres, neko, STT, TTS, memory)
├── eval/               WebVoyager-100, GAIA-mini, CodeAct contract
├── protocol/           phase rubrics, scripts, the four agent prompts
├── .opencode/          ← the agent definitions Sisyphus calls (read this first)
└── docs/               strategy, audit, ops
```

## Who reads what

**You're a human starting the build.**

1. `README.md` → fill in `.env` → run `setup.sh` → open OpenCode on the repo
2. Paste `KICKOFF.txt` into Sisyphus's chat
3. Watch the loop run in the OpenCode chat window
4. When `MANTLE_V1_RELEASED.md` lands: done. When `BLOCKED.md` lands: read it, fix the issue, say "resume mantle build."

**You're Sisyphus, just started a session.**

1. Read `.opencode/skills/mantle-build/SKILL.md` — that's your contract.
2. Read `docs/RASPUTIN_MANTLE_BUILD_PLAN.md`, `docs/AUDIT_LOOP.md`, `docs/SISYPHUS_LOOP.md`.
3. Determine current phase from git tags. Read that phase's YAML in `protocol/phases/`.
4. Use `TodoWrite` for every ticket. Use `delegate_task(subagent_type="mantle-...")` to dispatch work.
5. Commit per ticket with the structured message format. Push every 3 commits.

**You're one of the mantle-* subagents.**

Your system prompt is your `.opencode/agents/<name>.md` body. The user message from Sisyphus contains the ticket (or the rubric + diff if you're the auditor). Output what your prompt says to output, nothing else.

**You're an LLM debugging the loop itself.**

- Start at `.opencode/agents/*.md` (the four subagent definitions)
- Then `.opencode/skills/mantle-build/SKILL.md` (the loop logic Sisyphus runs)
- Then `docs/SISYPHUS_LOOP.md` and `docs/AUDIT_LOOP.md` for the conceptual model
- `audit-log/*.json` is the forensic trail of every audit verdict
- `planning/phase-RN/iter-N/*.md` is every ticket Sisyphus ever generated

## How phases work

Each phase has a YAML rubric in `protocol/phases/phase-RN.yaml`. The rubric declares:

- `packages_required` — what must pass each package's own verify
- `artifacts` — files that must exist and be non-empty
- `integration_tests` — test files that must pass repo-wide
- `eval_suites` — benchmarks with `minimum_pass_rate` against an output JSON
- `forbidden_patterns` — regexes that must NOT appear in code

Sisyphus reads the rubric, plans tickets via `mantle-planner`, dispatches executors in parallel, runs `make verify-phase-RN` (cheap mechanical floor), then calls `mantle-auditor`. PERFECT → tag and advance. PUNCH_LIST → fix and re-audit.

## How to make changes safely

- **Editing a phase rubric** (tightening it): `ALLOW_VERIFIER_EDIT=1 git commit ...` — and expect the auditor to flag the edit and explain why it's legitimate. The auditor sees the diff and is allowed to disagree.
- **Tuning the auditor:** edit `.opencode/agents/mantle-auditor.md`. Add specific failure patterns from new audits. Don't loosen — only sharpen.
- **Adding a new subagent role:** create `.opencode/agents/<name>.md`, mention it in the SKILL.md, mention it in KICKOFF.txt.

## What you do not do

- Don't edit `state.json` (legacy from v2) or `boulder.json` (OMO's resume state) by hand. If you need a clean slate: `rm state.json boulder.json` — Sisyphus re-derives from git tags.
- Don't run two Sisyphus sessions against the same repo concurrently. One session per repo.
- Don't raise `MAX_AUDIT_ITERATIONS` to dodge BLOCKED. Read the audit log.
- Don't disable the pre-commit hook. Cheapest line of defence.
- Don't add `--no-sandbox` to any browser. Ever.
- Don't `import anthropic` outside `apps/gateway/src/gateway/model_client.py`.
- Don't add tests that assert services are dead.

## Where the strict-mode auditor lives

`.opencode/agents/mantle-auditor.md`. Read this when something feels too aggressive — it lists the 16 patterns the auditor flags as blockers, with rationale. Two things to internalize:

1. The auditor is the cop. The first run of this build had no cop. That's why 30% of the planned capability actually shipped. v3 changes that.
2. Every PUNCH_LIST item has a `fix_hint` that gets handed verbatim to the next executor. Be specific. The 27B is competent but literal.
