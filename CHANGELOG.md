# Changelog

All notable changes to Rasputin Mantle are documented here. The format is adapted from [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] — 2026-05-18

### Added
- Brand identity and visual asset set (`assets/brand/`) regenerated with Nano Banana 2 (`gemini-3.1-flash-image-preview`) — teal-sage palette.
- Comprehensive `README.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `CHANGELOG.md`.
- `.github/ISSUE_TEMPLATE/` and `.github/PULL_REQUEST_TEMPLATE.md`.

### Changed
- `apps/gateway/src/gateway/routes/voice.py` — `/synthesize` now returns raw `audio/wav` `Response` instead of `resp.json()`, and both routes read `WHISPER_URL` / `KOKORO_URL` from the environment.
- `apps/gateway/src/gateway/memory_client.py` — duplicate lines removed, real HTTP calls to `rasputin-memory` for `store`, `query`, `stats`, and `reflect`, with Bearer-token auth.

### Fixed
- Voice round-trip `/synthesize` route no longer attempts to JSON-decode a streaming audio response.
- Memory client `stats()` and `reflect()` no longer always fall through to the stub.

## [1.0.0] — 2026-05-17

The v1 release. Seven phases (R0 → R6) shipped under a strict two-agent audit loop. Every phase passed Opus 4.7 with verdict `PERFECT`.

### Added — Phase R0 · Bootstrap & Protocol
- Monorepo structure with `pnpm` and `uv` workspaces.
- CI workflows: `license-gate.yml`, `eval-nightly.yml`, `absorb-nightly.yml`.
- `AGENTS.md`, `ARCHITECTURE.md`, `SECURITY.md`.
- Orchestrator scaffold with deterministic state machine and `state.json` `fsync`+`rename` durability.

### Added — Phase R1 · Audit Remediation
- Fixed five concrete bugs from the 2026-05-16 audit: browser backend syntax (B1), skills schema drift (B2), server-side cost ceiling (B3), real Wide Research (B4), session ↔ sandbox lifecycle (B5).
- Added `sandbox_id` to `SessionInfo`.
- `DELETE /{session_id}` now tears down the bound sandbox.

### Added — Phase R2 · Browser & Skills
- `PlaywrightBackend` with Chromium sandbox **on**.
- `SKILL.md` loader with Pydantic validation.
- `/api/agent/run` with SSRF-protected URL validation.
- WebVoyager-100 eval harness (100 tasks, 4-12 concurrent browsers).
- Multi-model benchmark across Qwen3-235B (12%), Sonnet 4.5 (26%), Kimi K2.6 (32%), Opus 4.7 (59%), GPT-5.5 (**63%, passes gate**).

### Added — Phase R3 · Gateway & Cost Wall
- `model_client.py` with direct Anthropic + vLLM calls via `httpx` (no LiteLLM).
- `cost_wall.py` writing to `gateway_costs` Postgres table.
- `CostCeilingMiddleware` returning `HTTP 429` on budget exceeded.
- Structured JSON logging per model call.
- 13/13 targeted tests passing.

### Added — Phase R4 · Frontend & Live Computer View
- `apps/web` — Next.js 15.1.0 + React 19.0.0 + Tailwind v4 dark-mode UI.
- Real Neko WebRTC iframe binding (not a placeholder).
- Real Server-Sent Events `EventSource` subscription.
- Resizable panels via `react-resizable-panels`.
- 2/2 Playwright E2E tests passing.

### Added — Phase R5 · Memory · Wide Research · Scheduler
- `packages/wide-research` with parallel `asyncio.gather` dispatch (up to 10 sandboxed workers).
- Brave Search + Exa backends with 10-template query fan-out.
- `packages/scheduler` — APScheduler `>=3.11` with Redis jobstore.
- Gateway `MemoryClient` with Qdrant + FalkorDB integration and in-process fallback.
- 5/5 integration tests passing.

### Added — Phase R6 · Voice · MCP · Desktop · Release
- `packages/voice` — async Faster-Whisper STT + Kokoro TTS HTTP clients.
- `packages/mcp-host` — MCP JSON-RPC 2.0 host over stdio + WebSocket (protocol `2024-11-05`).
- `apps/desktop` — Tauri 2 + React 19 (binary + DEB + RPM bundles).
- GAIA-mini eval harness (20 tasks).
- `MANTLE_V1_RELEASED.md` master release document.
- Voice latency verified: p50 = **365 ms**, p95 = 2153 ms.
- 4/4 integration tests passing.

### Performance summary at v1
- **WebVoyager-100 = 63%** (GPT-5.5), passes 60% gate.
- **CodeAct contract = 6/6 = 100%**.
- **CodeAct promptfoo = 10/10 = 100%** vs 8/10 gate.
- **Voice TTS p50 = 365 ms** vs 1500 ms gate.
- **rasputin-memory LoCoMo = 72.40%** on 1540 questions.
- **73 phase-reported passing checks** across 16 integration test files.

## Pre-1.0

Internal builds. Two prior incarnations (v0 and v2) preceded the present audit-loop architecture. Both were shelved when their auditor-less iterations produced Potemkin code. v1 is the first release under the strict two-agent audit loop.
