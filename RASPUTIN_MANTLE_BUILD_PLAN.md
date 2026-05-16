# Rasputin Mantle — End-to-End Build Plan

> **Hand-off target:** OpenCode (Qwen3.5-27B served by vLLM) orchestrated by Sisyphus (oh-my-openagent).
> **Author handoff date:** 16 May 2026.
> **Inherits from:** `rasputin-omnitool` (kernel/catalog), `rasputin-omnitool-skill` (planner/executor/reviewer), `rasputin-memory` (LoCoMo 77.7% backend), OpenClaw (gateway/sandbox host).
> **Goal:** An open-source, self-hosted, Manus-equivalent agent platform with a gorgeous frontend and live computer display — designed to keep absorbing new techniques as they emerge.

The name **Rasputin Mantle** is a suggestion — the cloak that wraps the omnitool kernel into a product. Alternatives: `rasputin-prime`, `rasputin-atelier`. Pick one in §0 before Sisyphus starts.

---

## QUICK START — do these 3 things, then paste the kickoff

### Step 1 — Put the plan files in your working directory

Create an empty directory where Sisyphus will build the repo, and drop both files there:

```
~/dev/rasputin-mantle/          (or wherever you want it to live)
├── RASPUTIN_MANTLE_BUILD_PLAN.md      ← this file
├── AGENTS.md                          ← short Sisyphus-facing intro
└── KICKOFF.txt                        ← the paste-able prompt (also reproduced in this section)
```

### Step 2 — Add Athena to your OMO config

Athena is the frontend specialist subagent. She doesn't exist in stock `oh-my-openagent`, so add her once before launching. Open `~/.config/opencode/opencode.json` (create it if it doesn't exist) and merge in:

```json
{
  "plugins": ["oh-my-openagent"],
  "omo": {
    "orchestration": { "enabled": true, "ultrawork": true },
    "agents": {
      "sisyphus":   { "model": "anthropic/claude-opus-4-7", "fallback": ["moonshot/kimi-k2.6", "zai/glm-5.1", "local/qwen3.5-27b"] },
      "planner":    { "model": "anthropic/claude-opus-4-7", "fallback": ["moonshot/kimi-k2.6"] },
      "consultant": { "model": "anthropic/claude-opus-4-7" },
      "executor":   { "model": "openai/gpt-5.5",             "fallback": ["local/qwen3.5-27b"] },
      "frontend":   { "model": "anthropic/claude-sonnet-4-6", "fallback": ["anthropic/claude-opus-4-7"] },
      "research":   { "model": "anthropic/claude-opus-4-7" }
    },
    "background_tasks": { "max_concurrent_per_model": 4 }
  }
}
```

If you already have an `opencode.json`, just add `"frontend"` under `omo.agents` — the rest of your config is fine. If you're running Sisyphus against the local 27B only (no Anthropic/OpenAI keys configured), swap every model in the chain above for `local/qwen3.5-27b` — the plan is robust to that, frontend just takes longer.

### Step 3 — Start OpenCode and paste the kickoff

```bash
cd ~/dev/rasputin-mantle
opencode
```

Then paste this into the OpenCode TUI (also saved as `KICKOFF.txt` alongside this file):

```
@sisyphus Build Rasputin Mantle Phase 0 + Phase 1.

The full plan is at ./RASPUTIN_MANTLE_BUILD_PLAN.md in this directory.
A short Sisyphus-facing intro is at ./AGENTS.md — read that first, then the plan.

Deliverables before you stop:
1. Repo `rasputin-mantle` initialized with the layout in §5 of the plan.
2. Two submodules added and importable from apps/gateway:
   - kernel/  → https://github.com/jcartu/rasputin-omnitool
   - memory/  → https://github.com/jcartu/rasputin-memory
3. CI workflows (eval-nightly, absorb-nightly, license-gate) committed and passing on an empty repo.
4. packages/sandbox with ComputeSDK abstraction + local Docker backend + E2B Desktop backend behind a feature flag.
5. packages/codeact exposing execute_code({code}) and returning a structured result.
6. A passing Promptfoo suite at eval/promptfoo/codeact.yaml with 10 tasks. Minimum: 8/10 green.
7. docs/SECURITY.md populated from §8 of the plan.
8. AGENTS.md at repo root that points future sessions at the build plan.

Delegation hints (also in §7 of the plan):
- @planner: plan the file scaffold first; do not let @executor write code until @consultant has reviewed the plan.
- @executor: start with packages/sandbox; gateway and skills come later phases.
- @research: not needed yet — Phase 7.
- @frontend: not needed yet — Phase 4.

Hard limits:
- Cost ceiling: $40 for this run.
- Token budget per turn: 60k.
- If WebVoyager or any browser-touching test starts running in Phase 0/1, you've drifted. Stop and re-plan.

Definition of done: I can clone the repo, run `pnpm i && uv sync && docker compose -f infra/compose.dev.yml up`, then run `pnpm test` and see the CodeAct suite pass.

When done, write a short PHASE_0_1_DONE.md summarizing what shipped, what slipped, and what should change before Phase 2 starts. Then stop.
```

That's it. The rest of this document is the reference Sisyphus will read on its own.

---

## 0. TL;DR — the bet

We are not cloning Manus. We are taking its three architectural bets that have aged well, the UX bets that have aged well from Perplexity Computer, and wiring them on top of `rasputin-omnitool`:

| Bet | Source | Our choice |
|---|---|---|
| **CodeAct** over JSON tool calls | Manus, Wang et al. 2024, Microsoft Agent Framework | Yes. Execute Python in sandbox, expose tools as `call_tool(...)` inside the Python runtime. |
| **Per-task isolated Linux VM** with sleep/wake | Manus Sandbox (Jan 2026) | E2B (Firecracker microVM) for ephemeral + Daytona (Docker/Kata, sub-90ms, persistence) for stateful sessions. Unified by ComputeSDK abstraction so we can hot-swap. |
| **SKILL.md skills** | Manus / Anthropic Agent Skills standard | Yes. `rasputin-omnitool-skill` already speaks SKILL.md. Skills go in a Marketplace, not the prompt. |
| **Live computer view, background agents, voice handoff** | Perplexity Computer / Comet | Neko (WebRTC virtual browser) inside the sandbox + a session-streaming WebSocket for terminal/file tree/plan view. |
| **Multi-model orchestration (19 models)** | Perplexity | LiteLLM gateway in front of Sisyphus + vLLM (local) + OpenRouter (cloud fallback). |
| **Wide Research / parallel subagents** | Manus | Sisyphus already does this. Codify the channels (`research`, `web`, `code`, `data`, `design`, `slides`, `media`, `mail`, `shell`). |

Three things we will **not** do:

1. **Will not** build our own browser. Comet is a Chromium fork; we instead drive a remote Chromium *inside* the sandbox via CDP (browser-use + agent-browser). Same outcome, ~5% of the work.
2. **Will not** build a payments/credits system in v1. Open-source, self-hosted, BYO-keys. Add it later if Mantle becomes a product.
3. **Will not** invent our own memory format. `rasputin-memory` already exists and benchmarks well; integrate, don't replace.

**Time-to-MVP estimate (Sisyphus + Hephaestus + 27B coder):** Phase 0–3 in ~10 days of agentic work, Phase 4–7 in ~20 days. Total ~30 agent-days for a working clone with one nice frontend.

---

## 1. Non-negotiables (read before every PR)

1. **Everything self-hostable.** No required SaaS. Cloud APIs (Anthropic, OpenAI, OpenRouter) are *swappable backends*, never *required* dependencies.
2. **License-clean.** Every dependency goes through `rasputin_omnitool.licenses` review before being merged. MIT/Apache/BSD-2/BSD-3/MPL-2 are auto-green. AGPL/SSPL/non-OSI need a written rationale in the PR.
3. **CodeAct sandboxing is non-negotiable.** The agent never executes arbitrary code on the gateway/host. Every `exec` flows through a sandbox handle. (The OpenClaw audit in Feb 2026 is the cautionary tale — `--no-sandbox` on Chromium, root containers, passwordless VNC. We do not repeat those.)
4. **No agent loops without Langfuse traces and Promptfoo evals.** `rasputin-omnitool-skill` already wires both. Keep it that way.
5. **Reversible by default.** Any tool that mutates state outside the sandbox (sending email, posting to Slack, publishing) must require an explicit `confirm: true` in its action spec.
6. **Cost ceiling enforcement.** Every session has a hard token-and-dollar ceiling. Already in `rasputin-omnitool-skill`; do not regress.

---

## 2. Capability parity matrix

Mapped against Manus's published surface (web app + agent skills + computer use, May 2026). The "Owner" column points at the Sisyphus subagent that owns the slice.

| # | Manus capability | Mantle component | OSS tools | Owner |
|---|---|---|---|---|
| 1 | Agent loop with planner/executor/reviewer | `rasputin-omnitool-skill` (existing) | — | Sisyphus |
| 2 | Per-task sandboxed Linux VM | `mantle-sandbox` adapter | E2B + Daytona via ComputeSDK | Hephaestus |
| 3 | CodeAct executor | `mantle-codeact` | langgraph-codeact OR custom shim around E2B Code Interpreter | Hephaestus |
| 4 | Browser automation | `mantle-browser` | `browser-use` (primary) + `agent-browser` (rust CLI, token-efficient) | Prometheus → Hephaestus |
| 5 | Wide Research (parallel subagents) | Sisyphus channels | Sisyphus + background task system | Sisyphus |
| 6 | Web App Builder | `mantle-webdev` skill | Next.js scaffolder + Tailwind + shadcn + Supabase or Postgres | Hephaestus |
| 7 | AI slides | `mantle-slides` skill | python-pptx (already in `rasputin-omnitool.deliverables`) + Marp for HTML decks | Hephaestus |
| 8 | AI image gen | `mantle-image` skill | ComfyUI (local) + FLUX.1.1-Pro / SDXL via Replicate fallback | Hephaestus |
| 9 | AI music | `mantle-music` skill | AudioCraft / MusicGen local; ElevenLabs SFX optional | Hephaestus |
| 10 | Voice (TTS+STT) | `mantle-voice` skill | Faster-Whisper (STT) + Kokoro-82M / Piper (TTS) | Hephaestus |
| 11 | Document handling | Already in kernel | Docling + Crawl4AI (smoke-tested in `library_smoke`) | — |
| 12 | Data analysis | `mantle-data` skill | pandas + DuckDB + Plotly inside CodeAct | Hephaestus |
| 13 | Mail | `mantle-mail` skill | google-api-python-client + Microsoft Graph SDK | Hephaestus |
| 14 | Slack/Telegram bridge | `mantle-messaging` | slack-bolt + python-telegram-bot | Hephaestus |
| 15 | Scheduling | Existing scheduler (kernel catalog #25) | APScheduler + RRULE | — |
| 16 | Web search | Existing | SearXNG (local) + Exa fallback | — |
| 17 | Memory | `rasputin-memory` | (already exists) | — |
| 18 | Long-term knowledge | Mem layer | Mem0 graph or `rasputin-memory` graph branch | — |
| 19 | MCP server hosting | `mantle-mcp-host` | MCP Python SDK + the registry from oh-my-openagent | Sisyphus |
| 20 | Agent Skills marketplace | `mantle-skills` registry | Anthropic Agent Skills Open Standard SKILL.md, served as static manifest | Sisyphus |
| 21 | Frontend | `mantle-web` | Next.js 15 + React 19 + Tailwind + shadcn/ui + Liveblocks for collab | Athena (frontend specialist subagent — see §7) |
| 22 | Live computer view | `mantle-view` | Neko (WebRTC virtual browser) + xterm.js + Monaco file viewer | Athena |
| 23 | Background tasks | Sisyphus background system | — | Sisyphus |
| 24 | Spaces (collab) | `mantle-spaces` | Liveblocks or Yjs CRDT | Athena |
| 25 | Auth + multi-tenancy | `mantle-auth` | better-auth or Authelia + Postgres | Hephaestus |
| 26 | Observability | Langfuse (existing) | — | — |
| 27 | Evals | Promptfoo (existing) + new harness | — | — |
| 28 | Continuous capability absorption | `mantle-absorb` (new!) | rasputin-omnitool bakeoff + cron + LLM curator | Oracle |

That's 28 capabilities, mapped to the 28 in your existing kernel catalog. Nothing invented; everything composed.

---

## 3. Architecture

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

**Why this shape:**

- The gateway is the only thing the frontend talks to. It enforces cost ceilings, auth, and RBAC. Every audit failure in `OpenClaw` (Feb 2026) maps to a gateway-level fix here: the gateway never binds 0.0.0.0 unless `MANTLE_PUBLIC=true`; sandbox VNC is token-authenticated with a short-lived URL; Chromium runs with full sandbox (we put it inside the VM, not a container with `--no-sandbox`).
- Sisyphus owns task planning *only*. `rasputin-omnitool-skill` owns the tactical inner loop (the planner/executor/reviewer triad you already wrote). Sisyphus calls into the skill, not the other way around. This preserves your existing evals.
- The sandbox is abstracted via ComputeSDK so we can switch E2B ↔ Daytona ↔ local Docker without rewriting agent code. Default: Daytona for sessions that need persistence (the "My Computer" pattern), E2B for one-shot CodeAct.
- Neko gives us a smooth WebRTC video stream of the live browser, with audio and multi-user takeover — strictly better than noVNC for the "watch the agent work" UX.

---

## 4. Component choices, with rationale

### 4.1 LLM serving

- **Local serving:** vLLM (continuous batching, Firecracker-friendly, OpenAI-compatible). Qwen 3.5 27B as the default coder; Qwen 3.5 235B-A22B MoE for the orchestrator when GPU allows.
- **Gateway:** LiteLLM. One key, many providers, budget caps, automatic fallback. Sisyphus has a configured chain — preserve it: `claude-opus-4.7 → kimi-k2.6 → glm-5.1 → qwen3.5-27b-local`.
- **Why not SGLang as the default:** SGLang wins on multi-turn prefix-cached workloads. We will ship a SGLang config behind a feature flag; default is vLLM for ecosystem maturity.

### 4.2 Orchestration

- **Sisyphus** (oh-my-openagent) is the conductor. Prometheus plans, Metis consults, Hephaestus deep-works, Athena (new — see §7) owns frontend, Oracle does research.
- **Agent loop kernel:** keep `rasputin-omnitool-skill`'s planner→executor→reviewer triad. Sisyphus calls this as a subroutine for any task that ends in "write code & ship".
- **CodeAct executor:** Use Microsoft Agent Framework's `execute_code` shape (a single tool, returns one consolidated result) instead of a thicker langgraph-codeact dependency. Wire it via E2B Code Interpreter — it already gives Python + Jupyter kernels and shared state.

### 4.3 Sandbox

- **Primary:** E2B Desktop (microVM, has full graphical environment, made specifically for LLM computer use). MIT-equivalent OSS license. Self-hostable via E2B Infra.
- **Persistent:** Daytona (sub-90ms cold starts, supports Computer Use across Linux/macOS/Windows desktops, MIT).
- **Abstraction:** ComputeSDK (open source, unified API across E2B/Daytona/Modal/Vercel/CodeSandbox). One line to swap providers.
- **Live display:** Neko (`m1k1o/neko`, Apache 2.0) bakes a WebRTC virtual browser into a Docker container. Smoother than noVNC, supports audio + multi-user takeover. Run inside the sandbox, expose only the Neko port to the gateway. Token-auth on the gateway side; Neko itself never sees the public internet.

### 4.4 Browser automation

- **Primary library:** `browser-use` (89.1% WebVoyager, MIT, has a SKILL.md drop-in for Claude Code that we adapt for Sisyphus's skill loader).
- **Token-efficient CLI:** `agent-browser` (Vercel Labs, Rust, MIT). Use this when the model is the 27B local — its accessibility-tree-with-refs output is ~10× more token-efficient than DOM dumps.
- **Stealth/CAPTCHA:** BrowserAct (open-sourced 14 May 2026, fingerprint+network+session isolation, free hCaptcha/reCAPTCHA/Turnstile solvers). Add as an optional skill, not a default — fingerprint rotation has policy implications.
- **CDP escape hatch:** raw Chrome DevTools Protocol for the cases where higher-level libs fail. The model can `await sandbox.cdp.send(...)`.

### 4.5 Memory

- **Use `rasputin-memory`.** It already benchmarks at 77.7% on LoCoMo with fact extraction + foundation-model reranking. Mem0's published 67.13% is lower; Letta's filesystem-baseline 74.0% is also lower. You have a winner already — don't replace it.
- **Two-layer plan:** `rasputin-memory` for persistent user/project facts; sandbox-local SQLite for session state. The CodeAct runtime always has read access to both via `mem.get(...)` / `session.get(...)`.

### 4.6 Tool / skill layer

- **Inherit:** `rasputin-omnitool` catalog. The 28 capabilities are your source of truth.
- **Skill format:** Anthropic Agent Skills Open Standard (SKILL.md + bundled scripts/resources). Manus and Claude Code both speak it. So does `rasputin-omnitool-skill`. Make this the single skill format Mantle understands.
- **Skill marketplace:** A static JSON manifest served by the gateway, listing skills with their SHA, license, and trust level. v1 is filesystem-based; v2 can be a remote registry. (Don't build a marketplace UI in v1 — show the JSON in the settings page.)

### 4.7 Frontend

- **Stack:** Next.js 15 (App Router) + React 19 + Tailwind 4 + shadcn/ui. Bun for tooling.
- **Layout:** four-pane Linear/Cursor-style — chat (left), live computer view (center, Neko WebRTC iframe), plan tree + file tree (right), terminal+console drawer (bottom).
- **Realtime:** Server-Sent Events for token-stream and plan updates; WebRTC for the live computer; Liveblocks (free tier OK for personal use, or self-host with Yjs) for collaborative spaces.
- **Theming:** Pull from `theme-factory` (you have this as a skill). Default theme: dark, with electric blue accent (#5F8DFF) — the user can swap.
- **Voice:** WebRTC mic → Faster-Whisper STT → Sisyphus → Kokoro TTS → WebRTC speaker. Optional. Off by default.
- **Mobile:** Same Next.js as a PWA. No native app in v1.

### 4.8 Observability & evals

- **Langfuse** (already wired in `rasputin-omnitool-skill`). Add session replay so the live computer view can be re-played from trace.
- **Promptfoo** (already wired). Add a `mantle-eval` harness that runs WebVoyager-100 nightly against the agent and posts to Langfuse. Regression budget: ≤2 percentage points week-over-week.
- **OpenTelemetry** for the gateway itself. Export to Grafana Cloud free tier or self-hosted Tempo.

### 4.9 Auth & multi-tenancy

- **Auth:** `better-auth` (TypeScript-native, OSS, supports SSO/OAuth/passkeys). Or Authelia if you want a heavier-weight forward-auth.
- **Tenancy model:** Single-tenant in v1 (you are the only user). Schema is multi-tenant-ready (every row has a `tenant_id`) so v2 doesn't require migration.
- **Secrets:** Vault or `sops`-managed `.env`. Never raw in Docker compose.

---

## 5. Repository layout

A pnpm + uv monorepo. One repo, many packages. Mirrors the OpenCode + Tauri pattern.

```
rasputin-mantle/
├── apps/
│   ├── web/                     # Next.js 15 frontend
│   ├── gateway/                 # FastAPI server, the only thing /web talks to
│   └── desktop/                 # Tauri shell wrapping the web app (Phase 6)
├── packages/
│   ├── sandbox/                 # ComputeSDK abstraction + Neko wiring
│   ├── codeact/                 # CodeAct executor + tool-as-Python shim
│   ├── browser/                 # browser-use + agent-browser + BrowserAct wrappers
│   ├── skills/                  # Skill loader, SKILL.md parser, marketplace manifest
│   ├── voice/                   # Faster-Whisper + Kokoro adapters
│   ├── mcp-host/                # MCP server hosting + discovery
│   └── shared/                  # Types, Zod schemas, error classes
├── skills/                      # Bundled SKILL.md skills (one folder each)
│   ├── webdev/
│   ├── slides/
│   ├── data-analysis/
│   ├── image-gen/
│   ├── mail/
│   ├── browser-research/
│   └── ... (one per kernel capability)
├── kernel/                      # GIT SUBMODULE → rasputin-omnitool
├── memory/                      # GIT SUBMODULE → rasputin-memory
├── eval/
│   ├── webvoyager-100/
│   ├── gaia-mini/
│   └── promptfoo/
├── infra/
│   ├── docker-compose.yml       # Local single-host stack
│   ├── compose.dev.yml          # Dev with hot reload
│   ├── helm/                    # Optional, for k8s users
│   └── sandbox-images/          # Daytona base image + E2B template
├── docs/
│   ├── ARCHITECTURE.md
│   ├── SECURITY.md              # Read this before opening ports
│   └── SKILL_AUTHORING.md
├── .github/workflows/
│   ├── eval-nightly.yml         # WebVoyager-100 + GAIA-mini
│   ├── absorb-nightly.yml       # mantle-absorb capability scan
│   └── license-gate.yml         # Blocks PRs that introduce non-OSI deps
├── AGENTS.md                    # Sisyphus-readable top-level instructions
└── README.md
```

The two submodules (`kernel/`, `memory/`) keep your existing repos sovereign — Mantle consumes them, doesn't fork them.

---

## 6. Phased build plan

Phases are sized so each one is a single Sisyphus session (1–3 agent-days of ultrawork). Each phase has a **single owning subagent** and a **single ship gate**.

### Phase 0 — Repo + CI scaffold (Day 1, Hephaestus)

- Init monorepo with pnpm + uv workspaces.
- Wire submodules: `kernel/` → `rasputin-omnitool`, `memory/` → `rasputin-memory`.
- Add the three GH workflows (eval-nightly, absorb-nightly, license-gate).
- Add `AGENTS.md` with this build plan inline as the top section.
- **Gate:** `pnpm i && uv sync` clean on a fresh clone; `kernel/` and `memory/` import OK from `apps/gateway`.

### Phase 1 — Sandbox abstraction + first CodeAct cell (Days 2–3, Hephaestus)

- `packages/sandbox`: ComputeSDK wrapper, default backend = local Docker, secondary = E2B Desktop.
- `packages/codeact`: thin shim exposing `execute_code({code: string})` → returns `{stdout, stderr, results, files_changed}`.
- Smoke test: `agent.run("compute the first 50 prime numbers, save them to primes.txt")` must produce primes.txt inside the sandbox and surface its path.
- **Gate:** Promptfoo CodeAct suite passes (10 tasks; add to repo as fixtures).

### Phase 2 — Browser + skills (Days 4–6, Hephaestus + Prometheus)

- `packages/browser`: wrap `browser-use` and `agent-browser`. Default to `agent-browser` when the active model is the 27B local (token efficiency); switch to `browser-use` when the active model is Opus/Sonnet/K2.6.
- `packages/skills`: SKILL.md loader. Parse the existing skills folder into a registry. Bundle the first six skills: `webdev`, `slides`, `data-analysis`, `mail`, `browser-research`, `image-gen` (image-gen MCP-out to ComfyUI, no local GPU required for v1).
- **Gate:** `webvoyager-100` nightly hits ≥ 60% pass rate. (Manus is reportedly in the 70s. We'll close the gap in later phases.)

### Phase 3 — Gateway + Sisyphus wiring (Days 7–8, Hephaestus)

- `apps/gateway`: FastAPI with SSE endpoints `/api/session/{id}/stream`, `/api/session/{id}/exec`, `/api/skills`, `/api/files`.
- Sisyphus speaks to the gateway via a thin client in `packages/shared`. The gateway never embeds Sisyphus — Sisyphus is a process Sisyphus runs (turtles all the way down — yes, this is fine; OpenCode is the orchestrator harness, Sisyphus is the meta-agent inside it).
- Cost ceiling middleware: per-session token + dollar caps, hard 4xx when exceeded.
- **Gate:** End-to-end: a Sisyphus task that says "create primes.txt, screenshot example.com, summarize the screenshot to /summary.md" completes with all three artifacts present and a Langfuse trace that costs < $0.10.

### Phase 4 — Web frontend, MVP (Days 9–13, Athena)

- `apps/web`: Next.js 15 + Tailwind + shadcn. Four-pane layout. SSE-driven chat. File tree pulled from `/api/files`. Plan tree pulled from `/api/session/{id}/plan`.
- Live computer view via embedded Neko iframe with token-gated URL.
- Voice mode behind a feature flag, default off.
- Theme: dark mode, accent #5F8DFF, IBM Plex Mono for code, Inter for chat.
- **Gate:** A user can submit a goal in the chat pane, watch the plan tree populate, see the agent open Chrome in the center pane and click things, and see files appear in the right pane. End-to-end on one screen.

### Phase 5 — Wide Research, memory hookup, scheduler (Days 14–17, Sisyphus + Hephaestus)

- Hook `rasputin-memory` MCP server into the gateway. Wire memory reads into the planner's context-build step. Wire memory writes into the reviewer's post-step.
- Parallel subagents: codify Sisyphus channels into a `/api/session/{id}/wide-research` endpoint that fans out 3–10 parallel Hephaestus instances and merges results.
- APScheduler for `/api/schedules` — user can say "every Monday at 9am, give me a market brief" and the gateway persists the cron.
- **Gate:** Memory recall test (LoCoMo subset, 20 questions) ≥ 75% in-product. Wide-research test ("compare 10 AI agent platforms launched in Q1 2026, output a markdown table") completes in < 15 min with sources cited.

### Phase 6 — Polish: voice, desktop shell, MCP marketplace (Days 18–22, Athena + Hephaestus)

- Voice mode on by default. Faster-Whisper-large-v3 + Kokoro-82M for snappy roundtrip.
- `apps/desktop`: Tauri shell so Mantle has a Mac/Windows/Linux app surface. Same Next.js, just packaged.
- MCP marketplace UI in settings — list installed MCP servers, add by URL, show health checks.
- **Gate:** End-to-end voice loop ≤ 1.5 s p50 (user stop-talking → agent first audio token).

### Phase 7 — mantle-absorb (Days 23–25, Oracle)

This is the answer to "constantly absorbing new ideas and techniques as they emerge."

- A nightly GH Actions cron (`absorb-nightly.yml`):
  1. Pull a curated list of agentic-tool RSS feeds + GH-trending repos with relevant topics (`ai-agent`, `agent-tools`, `mcp`, `agent-skills`, `browser-agent`, `computer-use`, `codeact`, `sandbox`).
  2. For each new repo: run the existing `rasputin_omnitool.bakeoff` (PyPI/npm + import smoke) and `rasputin_omnitool.licenses` review.
  3. LLM curator (Oracle with Opus 4.7) classifies each survivor into one of the 28 catalog buckets and writes a one-line "would this displace our current pick?" verdict.
  4. Output: a `CAPABILITY_DELTA.md` artifact in the run + an issue auto-opened tagged `capability-absorb` if Oracle's verdict is "yes" or "consider".
- Add a `/api/absorb/feed` SSE endpoint that surfaces the delta in the web UI's settings page so you see what's new each morning.
- **Gate:** A real OSS release from the previous week (e.g. BrowserAct on 14 May) shows up in the next morning's `CAPABILITY_DELTA.md` with a correct license and a sensible Oracle verdict.

---

## 7. Sisyphus delegation map

| Subagent | Model fallback chain | Owns | Lives in OMO config as |
|---|---|---|---|
| **Sisyphus** | opus-4.7 → k2.6 → glm-5.1 → qwen3.5-27b-local | Top-level orchestration, plan files, multi-channel delegation | `agents.sisyphus` |
| **Prometheus** | opus-4.7 → k2.6 | Planning, decomposing the build plan into TODOs | `agents.planner` |
| **Metis** | opus-4.7 | Reviewing plans before execution starts | `agents.consultant` |
| **Hephaestus** | gpt-5.5 → qwen3.5-27b-local | Deep coding work (packages, gateway, sandbox) | `agents.executor` |
| **Athena** *(new — add to your OMO config)* | sonnet-4.6 → opus-4.7 | Frontend (apps/web, apps/desktop) | `agents.frontend` |
| **Oracle** | opus-4.7 | Research, capability absorption, eval design | `agents.research` |

The reason Athena is a new subagent and not a generic Hephaestus task: frontend work has its own taste vocabulary (component composition, animation timing, layout density) that benefits from a dedicated prompt and a Sonnet/Opus model. Don't make the 27B local model design your UI.

**Suggested initial OMO config delta** (drop into `~/.config/opencode/opencode.json`):

```json
{
  "plugins": ["oh-my-openagent"],
  "omo": {
    "orchestration": { "enabled": true, "ultrawork": true },
    "agents": {
      "sisyphus":   { "model": "anthropic/claude-opus-4-7", "fallback": ["moonshot/kimi-k2.6", "zai/glm-5.1", "local/qwen3.5-27b"] },
      "planner":    { "model": "anthropic/claude-opus-4-7", "fallback": ["moonshot/kimi-k2.6"] },
      "consultant": { "model": "anthropic/claude-opus-4-7" },
      "executor":   { "model": "openai/gpt-5.5",            "fallback": ["local/qwen3.5-27b"] },
      "frontend":   { "model": "anthropic/claude-sonnet-4-6", "fallback": ["anthropic/claude-opus-4-7"] },
      "research":   { "model": "anthropic/claude-opus-4-7" }
    },
    "background_tasks": { "max_concurrent_per_model": 4 }
  }
}
```

---

## 8. Security checklist (the OpenClaw-audit reminder)

Each item below is a CI-enforced gate. PRs that violate them block merge.

- [ ] Gateway binds to `127.0.0.1` unless `MANTLE_PUBLIC=true` is explicitly set.
- [ ] Sandbox containers run as a non-root UID. No `--no-sandbox` on Chromium ever; if a sandbox image needs it to function, the image is broken — fix the image.
- [ ] Neko/VNC is gated by short-lived signed tokens issued by the gateway. URL fragment, not query string. Expires in 5 minutes; auto-renews while the session is active.
- [ ] No world-writable state directories. `umask 077` in every Dockerfile.
- [ ] Secrets via env or sops; never committed; never logged in Langfuse spans.
- [ ] CORS allowlist is explicit, not `*`.
- [ ] Every external network call from inside a sandbox is logged with destination host and byte count, surfaced in the live computer view's "network" tab. (Helps catch a prompt-injected exfiltration attempt.)
- [ ] Prompt-injection canaries in every skill — a tripwire string the model is told to never repeat. If it appears in a tool call, the session is killed and an alert fires.

---

## 9. The first 48 hours

The literal Sisyphus kickoff prompt is in the **Quick Start** at the top of this document, and reproduced verbatim in `KICKOFF.txt` next to this file. Don't re-author it — just paste.

The phases that follow (2 through 7) reuse the same shape: pick a phase, ask Sisyphus to execute it, point at this document. Each phase has a single owning subagent and a single ship gate — that's deliberate, it keeps cost predictable.

---

## 10. What's not in this plan (and why)

- **Mobile native apps.** PWA is enough for v1. Native Comet-style mobile browser is a 12-month project of its own.
- **Custom inference engine.** vLLM and SGLang are not commodities yet — but they're close enough that the marginal value of rolling our own is negative. Revisit in 2027.
- **A credits / payments system.** We are self-hosted. If Mantle gets users, add Stripe + Workos in a separate phase 8. Not in v1.
- **A skills marketplace UI with installs/uninstalls/ratings.** A static JSON registry shipped with the repo is enough. UI is Phase 6 if there's time, else Phase 8.
- **Anything that would require Chromium fork maintenance.** Comet is a Chromium fork; we drive Chromium from inside a sandbox instead. The end-user experience is ~95% the same and the maintenance burden is ~5%.
- **A 19-model "Model Council" gimmick.** LiteLLM lets you call any model; Sisyphus already routes intelligently. We do not advertise a count.

---

## Appendix A — License snapshot (May 2026)

| Component | License | Notes |
|---|---|---|
| vLLM | Apache 2.0 | Green |
| SGLang | Apache 2.0 | Green |
| LiteLLM | MIT | Green |
| oh-my-openagent (Sisyphus) | MIT | Green |
| OpenCode (sst) | MIT | Green |
| browser-use | MIT | Green |
| agent-browser (Vercel Labs) | MIT | Green |
| BrowserAct skills | MIT | Green (verify on each release) |
| E2B SDK + Infra | Apache 2.0 | Green |
| Daytona | Apache 2.0 | Green |
| ComputeSDK | Apache 2.0 | Green |
| Neko | Apache 2.0 | Green |
| Next.js | MIT | Green |
| shadcn/ui | MIT | Green |
| Liveblocks (free tier) | Proprietary (SaaS) | Yellow — fallback to Yjs (MIT) for self-hosted |
| Faster-Whisper | MIT | Green |
| Kokoro-82M | Apache 2.0 | Green |
| ComfyUI | GPL-3.0 | **Yellow** — keep as a sidecar service called over HTTP, do not link against ComfyUI source. |
| Langfuse | MIT (self-host) | Green |
| Promptfoo | MIT | Green |
| Docling | MIT | Green |
| Crawl4AI | Apache 2.0 | Green |
| FastAPI / Hono | MIT | Green |
| better-auth | MIT | Green |
| Tauri | Apache 2.0 / MIT dual | Green |

Run `python -m rasputin_omnitool license-review` after every dependency add. The CI gate (`license-gate.yml`) calls the same code path.

---

## Appendix B — When to revisit this plan

Pin a calendar event for **15 August 2026**. By then we'll have ~90 days of mantle-absorb data, the LLM landscape will have moved, and at least three of the choices above will be wrong. Use the `CAPABILITY_DELTA.md` accumulation since launch as the input. Specifically watch:

- Whether SGLang's RadixAttention is winning enough on agent workloads to displace vLLM as default.
- Whether one of the BYOC sandbox vendors has shipped a credible Daytona+E2B alternative.
- Whether the Anthropic Agent Skills standard has fragmented or stayed singular.
- Whether Manus (now Meta) has open-sourced anything material — they ship to documentation, they don't ship to GitHub. Don't hold your breath, but check.

That's the plan. Hand it to Sisyphus.
