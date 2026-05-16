# Architecture

> Current intent — not all components are implemented yet. See `RASPUTIN_MANTLE_BUILD_PLAN.md` §6 for phase status.

## Overview

Rasputin Mantle is a self-hosted, open-source, Manus-equivalent agent platform with a live computer view, built on top of `rasputin-omnitool` (kernel), `rasputin-memory` (memory), and `oh-my-openagent` (orchestration).

## Component Architecture

```
                                                            ┌─────────────────────────────────┐
                                                            │           USER (you)            │
                                                            └──────────────┬──────────────────┘
                                                                           │
                                                ┌──────────────────────────▼─────────────────────────┐
                                                │             mantle-web  (Next.js 15)               │
                                                │  chat • live computer view • plan tree • files     │
                                                │  voice • spaces (Liveblocks) • skills marketplace  │
                                                └──────────────┬──────────────────────┬──────────────┘
                                                               │ WebSocket            │ WebRTC (Neko)
                                                               │                      │
                                                ┌──────────────▼──────────────────────▼──────────────┐
                                                │           mantle-gateway (FastAPI + Hono)          │
                                                │   auth • sessions • SSE • cost ceilings • RBAC     │
                                                └──────────────┬─────────────────────────────────────┘
                                                               │
                          ┌─────────────────────┬──────────────┴─────────────┬──────────────────────────┐
                          │                     │                            │                          │
            ┌─────────────▼──────────┐  ┌───────▼──────────┐  ┌──────────────▼─────────────┐  ┌─────────▼──────────┐
            │   LiteLLM Gateway      │  │  Sisyphus        │  │  rasputin-memory           │  │  mantle-absorb     │
            │   vLLM(Qwen3.5-27B)    │  │  (orchestrator,  │  │  (LoCoMo 77.7%, MCP,       │  │  (nightly cron)    │
            │   + Opus/Sonnet/K2.6   │  │   plan + ralph   │  │   graph + fact extraction) │  │  catalog refresh   │
            │   + OpenRouter        │  │   loop + delegate)│  │                            │  │                    │
            └────────────────────────┘  └───────┬──────────┘  └────────────────────────────┘  └────────────────────┘
                                                │
              ┌─────────────────────────────────┼──────────────────────────────────────────┐
              │                                 │                                          │
   ┌──────────▼─────────┐         ┌─────────────▼────────────┐                ┌────────────▼────────────┐
   │ Subagents (channels)│         │   rasputin-omnitool-     │                │   mantle-mcp-host       │
   │ Prometheus (plan)   │◄────────┤   skill (planner /       ├───────────────►│   MCP servers per skill │
   │ Hephaestus (build)  │         │   executor / reviewer    │                │   ┌─────────────────┐   │
   │ Athena (frontend)   │         │   loop, 18+ tools)       │                │   │ browser-use     │   │
   │ Oracle (research)   │         └─────────────┬────────────┘                │   │ docling         │   │
   │ Metis (consultant)  │                       │                             │   │ pptx, xlsx, pdf │   │
   └─────────────────────┘                       │                             │   │ mail, slack     │   │
                                                  │                             │   └─────────────────┘   │
                                                  │                             └───────┬─────────────────┘
                                                  │                                     │
                                ┌─────────────────▼─────────────────────────────────────▼──────────────┐
                                │                    mantle-sandbox  (ComputeSDK abstraction)          │
                                │                                                                       │
                                │   ┌─────────────────┐    ┌──────────────────┐    ┌────────────────┐  │
                                │   │ E2B Desktop      │    │ Daytona          │    │ Local Docker   │  │
                                │   │ Firecracker      │    │ Docker/Kata      │    │ (dev)          │  │
                                │   │ ephemeral, fast  │    │ persistent       │    │                │  │
                                │   └────────┬────────┘    └────────┬─────────┘    └────────┬───────┘  │
                                │            │                       │                       │           │
                                │   ┌────────▼───────────────────────▼───────────────────────▼────────┐ │
                                │   │   Per-sandbox: Chromium (Neko/WebRTC), shell, Jupyter, file FS  │ │
                                │   │   CodeAct runtime (Python 3.12 + 200 preinstalled packages)     │ │
                                │   └─────────────────────────────────────────────────────────────────┘ │
                                └───────────────────────────────────────────────────────────────────────┘
                                                  │
                                ┌─────────────────▼──────────────────┐
                                │      Langfuse  +  Promptfoo        │
                                │    (traces, evals, regression)     │
                                └────────────────────────────────────┘
```

## Key Design Decisions

### CodeAct over JSON tool calls
Execute Python in sandbox, expose tools as `call_tool(...)` inside the Python runtime. Based on Wang et al. 2024, Microsoft Agent Framework.

### Per-task isolated Linux VM with sleep/wake
E2B (Firecracker microVM) for ephemeral + Daytona (Docker/Kata, sub-90ms, persistence) for stateful sessions. Unified by ComputeSDK abstraction so we can hot-swap.

### SKILL.md skills
`rasputin-omnitool-skill` already speaks SKILL.md. Skills go in a Marketplace, not the prompt.

### Live computer view
Neko (WebRTC virtual browser) inside the sandbox + a session-streaming WebSocket for terminal/file tree/plan view.

### Multi-model orchestration
LiteLLM gateway in front of Sisyphus + vLLM (local) + OpenRouter (cloud fallback).

### What we will NOT do
1. Will not build our own browser. We drive a remote Chromium inside the sandbox via CDP.
2. Will not build a payments/credits system in v1. Open-source, self-hosted, BYO-keys.
3. Will not invent our own memory format. `rasputin-memory` already exists and benchmarks well.

## Phase Status

| Component | Phase |
|---|---|
| Repo + CI scaffold | Phase 0 |
| Sandbox abstraction + CodeAct | Phase 1 |
| Browser + skills | Phase 2 |
| Gateway + Sisyphus wiring | Phase 3 |
| Web frontend, MVP | Phase 4 |
| Wide Research, memory hookup | Phase 5 |
| Voice, desktop shell, MCP marketplace | Phase 6 |
| mantle-absorb | Phase 7 |
