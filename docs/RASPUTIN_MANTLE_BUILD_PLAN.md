# Rasputin Mantle — Build Plan

Rebuild a self-hosted, OSS, Manus-equivalent agent platform on top of the existing Rasputin stack. Seven phases, two-agent audit loop, deterministic orchestrator. End state: a daemon that runs unattended for ~3 weeks on a QNAP NAS and lands `MANTLE_V1_RELEASED.md` with eval numbers when done.

## What Mantle is

A self-hosted agent platform you can hand a goal and have it work — browse, code, research, remember, watch you watch it work. Same shape as Manus, but the orchestration runs in your house and the model spend lives in your account.

## Capability matrix vs Manus

| Capability               | Manus                              | Mantle v1 target                                                  |
|--------------------------|-------------------------------------|---------------------------------------------------------------------|
| Tool calls               | Proprietary CodeAct dialect         | CodeAct (Wang et al. 2024) — Python action loop                    |
| Sandbox                  | Their own VMs                       | E2B Firecracker + Daytona Docker/Kata via ComputeSDK; one per task |
| Skills format            | Closed                              | SKILL.md standard (frontmatter + body)                              |
| Live computer view       | Yes                                 | Neko WebRTC virtual browser inside the sandbox                      |
| Memory                   | Internal                            | rasputin-memory (LoCoMo 77.7%)                                      |
| Wide research            | Yes                                 | Parallel subagent dispatch (R5)                                     |
| Voice                    | Yes, low-latency                    | Faster-Whisper STT + Kokoro TTS, p50 < 1.5s                         |
| Desktop app              | Browser only                        | Tauri 2 wrapper around apps/web                                     |
| MCP                      | No                                  | Yes (R6) — extensible via external MCP servers                      |
| Models                   | Theirs                              | Local 27B (Qwen) for execution; Opus for audit; Sonnet for frontend |

## What we won't ship in v1

- A Chromium fork. Neko + headless Chromium is plenty.
- Payments. You bring your own Anthropic key and vLLM box.
- A new memory format. rasputin-memory exists and is competitive.
- An app store. Skills as `SKILL.md` files in repos are sufficient.

## Phase breakdown

**R0 — Bootstrap & Protocol Install.** Orchestrator boots, talks to vLLM and Anthropic, runs `make verify` clean, prints the phase roadmap. Pre-commit hook live.

**R1 — Remediate Audit Findings.** Fix the five concrete bugs the 2026-05-16 audit found. CodeAct contract ≥ 0.80. The audit document is in `docs/AUDIT_2026_05_16.md`.

**R2 — Browser & Skills.** Playwright + Chromium with sandbox ON. SKILL.md loader with Pydantic validation. WebVoyager-100 ≥ 0.60.

**R3 — Gateway & Cost Wall.** FastAPI gateway calls Anthropic and vLLM directly via official SDKs. Real cost-wall enforcement (server-side, server-trusted token counts). HTTP 429 when budget exceeded. No LiteLLM service (dropped in v2).

**R4 — Frontend & Live Computer View.** Next.js 15 + React 19 + Tailwind 4 + shadcn/ui. Real Neko WebRTC embed, not a placeholder div. SSE event stream that actually subscribes. Sonnet 4.6 is the executor for this phase.

**R5 — Memory, Wide Research, Scheduler.** Wire rasputin-memory. Implement Wide Research as actually-parallel subagent dispatch. APScheduler on Redis jobstore. LoCoMo ≥ 0.75.

**R6 — Voice, MCP, Desktop, Release.** Faster-Whisper + Kokoro voice loop, p50 < 1.5s. MCP host. Tauri desktop. GAIA-mini ≥ 0.40. Writes the real `MANTLE_V1_RELEASED.md` over the orchestrator's stub.

## Repos in play

- **rasputin-mantle** (this build) — orchestrator + gateway + frontend + integration
- **rasputin-omnitool** — the 28-capability OSS catalog kernel; consumed as a library
- **rasputin-memory** — git submodule, exposed as an HTTP service in R5
- **OpenClaw** — not consumed directly; used as reference for spawn patterns

## Build invariants

1. **Strict mode auditor.** Maximally skeptical Opus 4.7 reviewing every phase's diff. No "looks good enough" shipping.
2. **27B does the work.** Local Qwen3.5-27B-Instruct on the user's cloud GPU box, parallel-dispatched up to 8-wide. Free per call.
3. **No verifier editing.** The pre-commit hook and the auditor both block edits to the Makefile, phase YAMLs, and verify scripts. The only legitimate way to make a failing check pass is to fix the underlying capability.
4. **Mechanical floor before audit.** `make verify-phase-RN` is the cheap gate. If it's red, Opus doesn't get called — 27B fixes the floor first.
5. **Atomic state.** Orchestrator can survive kill -9 mid-phase. State persists to `state.json` via fsync+rename.
6. **One Anthropic role.** Auditor (Opus). Frontend specialist (Sonnet) is the only other Anthropic surface, and only on apps/web and apps/desktop tickets.
7. **No Potemkin.** Routes return real data or 501. Tests test real behaviour. Never assert services are dead in a phase where they're supposed to be live.

## Reproduction recipe (after release)

```bash
# On a fresh QNAP (or any Linux box with Docker + Container Station equivalent)
unzip mantle-v2.zip && cd mantle-v2
cp .env.example .env && vi .env   # ANTHROPIC_API_KEY, VLLM_BASE_URL, VLLM_API_KEY
./UNATTENDED.sh                   # idempotent; works if interrupted

# When the loop completes (~3 weeks):
cat ~/dev/rasputin-mantle/MANTLE_V1_RELEASED.md
```

## Cost shape (estimated)

| Bucket                    | Source                        | Est. total       |
|---------------------------|-------------------------------|------------------|
| Local 27B (Qwen)          | Your GPU rental               | (sunk cost)      |
| Opus auditor              | Anthropic API                 | $5-15            |
| Sonnet frontend           | Anthropic API                 | $10-20           |
| Sonnet eval judges        | Anthropic API                 | $5-10            |
| **Total Anthropic**       |                               | **$20-45**       |

Falls well under typical workspace budgets. Daily soft cap is $40 in the orchestrator's defaults — raise via `.env` if you want faster wall-clock progress.
