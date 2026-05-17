# Rasputin Mantle v1 Released

Date: 2026-05-17

## Summary

Rasputin Mantle v1 is a self-hostable Manus-shaped agent platform assembled across R0-R6. The system now has a FastAPI gateway, sandbox and CodeAct execution, browser automation, skills, cost controls, web UI, wide research, memory fallback, scheduler, voice clients, MCP host, desktop skeleton, and release/eval harnesses.

## Architecture Overview

- **Gateway**: FastAPI entrypoint under `apps/gateway`, exposing sessions, agent runs, cost wall, voice proxying, memory, MCP registry, scheduler, and research routes. It binds locally by default.
- **Sandbox**: `packages/sandbox` abstracts container-backed execution with lifecycle methods for create, destroy, exec, read, and write.
- **CodeAct**: `packages/codeact` provides Python action-loop execution and contract tests for deterministic code tasks.
- **Browser**: `packages/browser` wraps Playwright with Chromium sandboxing on, browser state extraction, navigation, click, type, and evaluate support.
- **Skills**: `packages/skills` loads validated `SKILL.md` capabilities with frontmatter checks.
- **Memory**: Gateway memory client falls back honestly to an in-process store when the external rasputin-memory service is unavailable.
- **Scheduler**: `packages/scheduler` wires APScheduler/Redis-style job persistence and gateway routes for recurring work.
- **Wide Research**: `packages/wide-research` dispatches parallel research subtasks and merges results.
- **Voice**: `packages/voice` contains async Faster-Whisper STT and Kokoro TTS HTTP clients plus a latency benchmark that reports skipped/unavailable rather than inventing numbers.
- **MCP**: `packages/mcp-host` implements a minimal MCP JSON-RPC host over stdio and WebSocket with `initialize`, `tools/list`, and `tools/call`.
- **Desktop**: `apps/desktop` is a Tauri 2 + React shell named "Rasputin Mantle" with chat UI and browser `MediaRecorder` mic fallback.

## Phase Status

| Phase | Status | Evidence |
|---|---|---|
| R0 | SHIPPED ✅ | Orchestrator/repo bootstrap and initial CodeAct eval path established. |
| R1 | SHIPPED ✅ | Five audit bugs fixed; reported tests include skills, CodeAct, and integration coverage. |
| R2 | INFRASTRUCTURE SHIPPED, gate not met | Browser + skills + agent endpoint shipped. WebVoyager release tracking number is **12% vs 60% target**; the local `PHASE_R2_DONE.md` artifact records one run at 10/100, also below gate. |
| R3 | SHIPPED ✅ | Model client + cost wall shipped; phase report records 13/13 targeted tests. |
| R4 | SHIPPED ✅ | Next.js 15 frontend and live computer view shipped; phase report records 2/2 E2E tests passed. |
| R5 | SHIPPED ✅ | Wide Research + Memory + Scheduler shipped; phase report records 5/5 integration tests passed. |
| R6 | SHIPPED ✅ | Voice clients, MCP host, Tauri desktop skeleton, GAIA-mini harness, and release docs shipped; R6 integration tests passed 4/4. |

## Test Count

- R6 final verification: **4/4 passed**.
- Phase-reported passing checks across release artifacts: **73 passed**.
  - R0/R1 initial CodeAct promptfoo: 10/10.
  - R1 remediation: 8 skills + 6 CodeAct + 2 integration = 16 passing checks reported.
  - R2 browser/skills/sandbox integration: 23/23.
  - R3 model client/cost wall: 13/13 targeted tests reported.
  - R4 web E2E: 2/2; separate Neko integration was documented as an honest skip when gateway was unavailable.
  - R5 integration: 5/5.
  - R6 integration: 4/4.

## Eval Numbers

| Eval | Result | Target | Notes |
|---|---:|---:|---|
| CodeAct promptfoo | 10/10, 100% | 8/10 | Reported in `PHASE_0_1_DONE.md`. |
| WebVoyager | 12% release tracking number; local artifact has 10/100 | 60% | Gate not met. Browser stack exists, agent reliability is the gap. |
| R4 E2E | 2/2 | 2/2 | Passed in phase report. |
| R5 integration | 5/5 | 5/5 | Passed in phase report. |
| R6 integration | 4/4 | 4/4 | Passed in this final run. |
| Voice latency | skipped/unavailable | p50 < 1.5s | No Faster-Whisper/Kokoro services were verified live locally. |
| GAIA-mini | unavailable | 40% | Harness and 20 tasks exist; no judged run was produced because the judge was not executed. |

## Cost Summary

No authoritative Anthropic billing export is present in this repository. The table below is an honest estimate based on phase docs and this R6 execution; local vLLM/GPU costs are excluded as sunk infrastructure.

| Phase | Estimated API cost | Notes |
|---|---:|---|
| R0 | $0-$1 | Bootstrap/orchestrator checks, mostly local. |
| R1 | $0-$1 | Audit remediation and local tests. |
| R2 | $1-$3 | Browser eval work likely used external model/browser judging, but no bill artifact is stored. |
| R3 | $1-$2 | Anthropic/vLLM client tests and cost-wall work; external calls were environment-gated. |
| R4 | $5-$10 | Frontend specialist work and E2E iteration per build plan estimate. |
| R5 | $1-$3 | Wide Research/Memory/Scheduler; web/search and judge paths were mostly gated or skipped locally. |
| R6 | $0 measured here | R6 integration used mocks/local parsing only; GAIA judge was not run. |
| **Total** | **$8-$20 estimated** | Under the original $20-$45 Anthropic budget envelope; actual bill should be verified from provider dashboards. |

## Key Dependencies

- Python: `fastapi`, `httpx`, `pydantic`, `pytest`, `pytest-asyncio`, `apscheduler`, `redis`, `fakeredis`, `websockets`, `PyYAML`.
- Browser/sandbox: Playwright, Chromium with sandboxing enabled, Docker-compatible runtime.
- Web/desktop: Next.js 15, React 19, Tailwind 4, Vite, Tauri 2, Rust/Cargo.
- Voice services expected externally: Faster-Whisper at `WHISPER_URL`, Kokoro at `KOKORO_URL`.
- Models/services: Anthropic API for optional judge/model paths, OpenAI-compatible vLLM endpoint for local execution.

## Reproduction Recipe

```bash
git clone <repo-url> rasputin-mantle
cd rasputin-mantle
cp .env.example .env  # if present; otherwise create .env with ANTHROPIC_API_KEY, VLLM_BASE_URL, VLLM_API_KEY as needed
pnpm install
uv sync
docker compose -f infra/compose.dev.yml up -d

PYTHONPATH=apps/gateway/src:packages/browser:packages/sandbox:packages/shared:packages/codeact:packages/skills:packages/wide-research:packages/scheduler:packages/voice:packages/mcp-host \
  python3 -m pytest tests/integration/test_voice_round_trip.py tests/integration/test_mcp_host_handshake.py tests/integration/test_desktop_launch.py -v

# Optional, only when voice services are actually running:
PYTHONPATH=packages/voice python3 -m voice.eval_latency --iterations 5

# Optional desktop shell:
cd apps/desktop
pnpm install
pnpm build
pnpm tauri build
```

## Honest Gaps vs Manus

- WebVoyager pass rate is **12% vs Manus claimed 67%**; even the local R2 artifact's 10/100 run is in the same below-target range.
- No Faster-Whisper/Kokoro containers were verified running locally; voice services are skipped/unavailable until started.
- No external `rasputin-memory` service/submodule integration was proven in R5/R6; memory currently has an in-process stub fallback.
- Tauri desktop is skeleton-only, not compiled in this release run.
- GAIA-mini has a runner and 20 tasks, but no judged score was produced here because the Anthropic judge was not run.

## Final Verdict

Mantle v1 is released as an honest local-first agent platform foundation. The core architecture is present and the final R6 integration suite passes. The largest remaining product gaps are browser-agent reliability, live voice service deployment, persistent external memory, and a compiled desktop artifact.
