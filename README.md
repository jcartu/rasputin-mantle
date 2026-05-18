<!--
  Rasputin Mantle - README v1.2
  -----------------------------------------------------------------------------
  Visual identity:  deep charcoal #0C1217, teal-sage #14B8A6 / #0D9488,
                    paperwhite #FAFBFC
  Fonts:            Geist Sans + IBM Plex Mono
  Animations:       CSS-only, respects prefers-reduced-motion
  -->

<br/>

<p align="center">
  <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect width="48" height="48" rx="10" fill="#0C1217"/>
    <path d="M14 34V14h4v16h-4zm10 0V14h4v16h-4zm10 0V14h4v16h-4z" fill="#14B8A6"/>
  </svg>
</p>

<h1 align="center">Rasputin Mantle</h1>

<p align="center">
  <strong>Self-hosted autonomous agent platform.</strong>
</p>

<p align="center">
  Give it a goal. It browses, codes, researches, and shows you its work. You keep the keys.
</p>

<br/>

<p align="center">
  <a href="#quick-start">Quick Start</a> ·
  <a href="#architecture">Architecture</a> ·
  <a href="#performance">Performance</a> ·
  <a href="#what-ships-in-v1.2">v1.2 Release</a> ·
  <a href="#engineering-invariants">Invariants</a> ·
  <a href="#honest-gaps">Gaps</a>
</p>

<br/>

---

## Quick start

```bash
curl -sSL https://mantle.dev/install | sh
```

One line. The installer clones the repo, configures your API keys, brings up the Docker stack, and opens `http://localhost:3000`. Re-running is idempotent.

**Requirements:** Docker, Python ≥3.11, Node ≥18, `pnpm`, `uv`, and an LLM API key (Anthropic, OpenAI, or a local vLLM endpoint).

<p align="center">
  <a href="https://demo.mantle.dev/v1.2/walkthrough.mp4">
    <img src="https://img.shields.io/badge/watch-90s_walkthrough-14B8A6?style=for-the-badge&labelColor=0C1217" alt="Watch the walkthrough" />
  </a>
  <img src="https://img.shields.io/badge/license-MIT-14B8A6?style=for-the-badge&labelColor=0C1217" alt="MIT License"/>
  <img src="https://img.shields.io/badge/version-v1_2-14B8A6?style=for-the-badge&labelColor=0C1217" alt="version v1.2"/>
</p>

---

## What this is

Rasputin Mantle is a self-hosted, MIT-licensed agent platform. The orchestration runs on your machine. The model spend lives in your account. No SaaS dependency, no billing layer, no opaque backend.

v1.2 ships a complete product surface: documented design system, 24 Radix-backed component primitives, three-pane resizable shell, real-time agent trace, Neko WebRTC live browser, scrubbable replay, share links, mobile layouts, onboarding, and full WCAG AA accessibility.

Underneath, the engine remains:

- **FastAPI gateway** with server-enforced cost ceiling (HTTP 429 on budget exceed)
- **CodeAct executor** (Wang et al. 2024) — Python action loop, open tool dialect
- **Hardened Docker sandbox** — `python:3.12-slim`, non-root, 512 MB RAM, `no-new-privileges`
- **Playwright + Chromium** — OS sandbox always on, enforced by pre-commit hook
- **SKILL.md registry** — frontmatter + body, loadable from any repo
- **Neko WebRTC live view** — real virtual browser stream, not screenshot polling
- **rasputin-memory** — Qdrant + FalkorDB, 72.40% LoCoMo
- **Wide research** — up to 10 parallel sandboxed subagents via `asyncio.gather`
- **Voice loop** — Faster-Whisper STT + Kokoro TTS, p50 365 ms
- **MCP host** — JSON-RPC 2.0, stdio + WebSocket
- **Tauri 2 desktop** — Mac DMG, Linux DEB/RPM, Windows MSI

---

## Architecture

<p align="center">
  <svg width="100%" viewBox="0 0 800 420" fill="none" xmlns="http://www.w3.org/2000/svg" style="max-width:800px;">
    <style>
      .mantle-box { fill: #111820; stroke: #1E2833; stroke-width: 1; rx: 6; }
      .mantle-label { fill: #E8EDF2; font-family: IBM Plex Mono, monospace; font-size: 11px; }
      .mantle-sublabel { fill: #8B95A2; font-family: IBM Plex Mono, monospace; font-size: 9px; }
      .mantle-accent { stroke: #14B8A6; stroke-width: 1.5; }
      .mantle-line { stroke: #2A3644; stroke-width: 1; }
      .mantle-arrow { fill: #2A3644; }
    </style>

    <!-- Interface Layer -->
    <rect x="200" y="20" width="400" height="60" class="mantle-box"/>
    <text x="400" y="42" class="mantle-label" text-anchor="middle">Interface</text>
    <text x="400" y="58" class="mantle-sublabel" text-anchor="middle">Next.js 15 · React 19 · Tauri 2 · Tailwind v4</text>

    <!-- Gateway Layer -->
    <rect x="200" y="110" width="400" height="60" class="mantle-box mantle-accent"/>
    <text x="400" y="132" class="mantle-label" text-anchor="middle">Gateway</text>
    <text x="400" y="148" class="mantle-sublabel" text-anchor="middle">FastAPI · sessions · cost wall · SSE · routes</text>

    <!-- Agent Layer -->
    <rect x="40" y="200" width="160" height="50" class="mantle-box"/>
    <text x="120" y="222" class="mantle-label" text-anchor="middle">Browser</text>
    <text x="120" y="236" class="mantle-sublabel" text-anchor="middle">Playwright + Chromium</text>

    <rect x="220" y="200" width="160" height="50" class="mantle-box"/>
    <text x="300" y="222" class="mantle-label" text-anchor="middle">CodeAct</text>
    <text x="300" y="236" class="mantle-sublabel" text-anchor="middle">Python action loop</text>

    <rect x="400" y="200" width="160" height="50" class="mantle-box"/>
    <text x="480" y="222" class="mantle-label" text-anchor="middle">Wide Research</text>
    <text x="480" y="236" class="mantle-sublabel" text-anchor="middle">10-way parallel dispatch</text>

    <rect x="580" y="200" width="160" height="50" class="mantle-box"/>
    <text x="660" y="222" class="mantle-label" text-anchor="middle">Skills</text>
    <text x="660" y="236" class="mantle-sublabel" text-anchor="middle">SKILL.md registry</text>

    <!-- Runtime Layer -->
    <rect x="100" y="290" width="180" height="50" class="mantle-box"/>
    <text x="190" y="312" class="mantle-label" text-anchor="middle">Sandbox</text>
    <text x="190" y="326" class="mantle-sublabel" text-anchor="middle">Docker · non-root · 512 MB</text>

    <rect x="310" y="290" width="180" height="50" class="mantle-box"/>
    <text x="400" y="312" class="mantle-label" text-anchor="middle">Voice</text>
    <text x="400" y="326" class="mantle-sublabel" text-anchor="middle">Whisper + Kokoro</text>

    <rect x="520" y="290" width="180" height="50" class="mantle-box"/>
    <text x="610" y="312" class="mantle-label" text-anchor="middle">MCP Host</text>
    <text x="610" y="326" class="mantle-sublabel" text-anchor="middle">JSON-RPC 2.0</text>

    <!-- Foundation Layer -->
    <rect x="200" y="370" width="400" height="40" class="mantle-box"/>
    <text x="400" y="395" class="mantle-label" text-anchor="middle">postgres · redis · qdrant · falkordb · rasputin-memory</text>

    <!-- Arrows -->
    <line x1="400" y1="80" x2="400" y2="110" class="mantle-line"/>
    <polygon points="396,108 404,108 400,116" class="mantle-arrow"/>

    <line x1="400" y1="170" x2="120" y2="200" class="mantle-line"/>
    <polygon points="117,197 120,205 123,197" class="mantle-arrow"/>

    <line x1="400" y1="170" x2="300" y2="200" class="mantle-line"/>
    <polygon points="297,197 300,205 303,197" class="mantle-arrow"/>

    <line x1="400" y1="170" x2="480" y2="200" class="mantle-line"/>
    <polygon points="477,197 480,205 483,197" class="mantle-arrow"/>

    <line x1="400" y1="170" x2="660" y2="200" class="mantle-line"/>
    <polygon points="657,197 660,205 663,197" class="mantle-arrow"/>

    <line x1="120" y1="250" x2="190" y2="290" class="mantle-line"/>
    <polygon points="187,287 190,295 193,287" class="mantle-arrow"/>

    <line x1="300" y1="250" x2="190" y2="290" class="mantle-line"/>
    <polygon points="187,287 190,295 193,287" class="mantle-arrow"/>

    <line x1="400" y1="340" x2="400" y2="370" class="mantle-line"/>
    <polygon points="396,367 400,373 404,367" class="mantle-arrow"/>
  </svg>
</p>

Five layers. Interface → Gateway → Agent Loop → Sandboxes → Foundation. Every layer is self-hostable. Cloud APIs are swappable backends, not requirements.

---

## Performance

### WebVoyager-300 — measured, reproducible

<p align="center">
  <svg width="100%" viewBox="0 0 600 200" fill="none" xmlns="http://www.w3.org/2000/svg" style="max-width:600px;">
    <style>
      .bar-bg { fill: #111820; rx: 4; }
      .bar-fill { fill: #14B8A6; rx: 4; transition: width 0.6s cubic-bezier(0.16, 1, 0.3, 1); }
      .bar-label { fill: #8B95A2; font-family: IBM Plex Mono, monospace; font-size: 10px; }
      .bar-value { fill: #E8EDF2; font-family: IBM Plex Mono, monospace; font-size: 11px; font-weight: 600; }
      .bar-line { stroke: #2A3644; stroke-width: 0.5; stroke-dasharray: 2 2; }
    </style>

    <!-- Grid lines -->
    <line x1="180" y1="20" x2="180" y2="180" class="bar-line"/>
    <text x="175" y="15" class="bar-label" text-anchor="end">25%</text>

    <line x1="260" y1="20" x2="260" y2="180" class="bar-line"/>
    <text x="255" y="15" class="bar-label" text-anchor="end">50%</text>

    <line x1="340" y1="20" x2="340" y2="180" class="bar-line"/>
    <text x="335" y="15" class="bar-label" text-anchor="end">75%</text>

    <line x1="420" y1="20" x2="420" y2="180" class="bar-line"/>
    <text x="415" y="15" class="bar-label" text-anchor="end">100%</text>

    <!-- Opus 4.6: 78% -->
    <text x="170" y="48" class="bar-label" text-anchor="end">Opus 4.6</text>
    <rect x="180" y="36" width="273" height="20" class="bar-fill"/>
    <text x="460" y="51" class="bar-value">78.00%</text>

    <!-- Sonnet 4.6: 74.33% -->
    <text x="170" y="83" class="bar-label" text-anchor="end">Sonnet 4.6</text>
    <rect x="180" y="71" width="260" height="20" class="bar-fill" style="fill: #0D9488;"/>
    <text x="446" y="86" class="bar-value">74.33%</text>

    <!-- GPT-5.5: 70% -->
    <text x="170" y="118" class="bar-label" text-anchor="end">GPT-5.5</text>
    <rect x="180" y="106" width="246" height="20" class="bar-fill" style="fill: #0F766E;"/>
    <text x="432" y="121" class="bar-value">70.00%</text>

    <!-- Kimi K2.6: 69.33% -->
    <text x="170" y="153" class="bar-label" text-anchor="end">Kimi K2.6</text>
    <rect x="180" y="141" width="243" height="20" class="bar-fill" style="fill: #115E59;"/>
    <text x="429" y="156" class="bar-value">69.33%</text>
  </svg>
</p>

Same agent loop, same browser, same sandbox. The only variable is the planning model.

| Eval | Result | Target |
|---|---|---|
| **WebVoyager-300** (Opus 4.6) | **78.00%** | — |
| **CodeAct contract** | 6/6 = **100%** | 6/6 |
| **Voice round-trip (p50)** | **365 ms** | <1500 ms |
| **Memory (LoCoMo)** | **72.40%** | — |
| **Lighthouse (landing)** | **97** | 95 |

Full eval artifacts in [`MANTLE_V1_1_RELEASED.md`](MANTLE_V1_1_RELEASED.md) and [`MANTLE_V1_2_RELEASED.md`](MANTLE_V1_2_RELEASED.md).

---

## What ships in v1.2

v1.0 proved the platform. v1.1 proved the agent. v1.2 makes both feel like a product.

### Design system

A complete, documented design system in `design-system/`. Teal-sage accent. Geist Sans + IBM Plex Mono. Light and dark mode, both first-class.

- **`tokens.css`** — CSS custom properties for color, type, spacing, radius, shadow, motion
- **`SPEC.md`** — component contract. Every primitive, layout rule, interaction state
- **`COPY.md`** — voice and tone. Sentence case. Active voice. Forbidden words list
- **`MOTION.md`** — motion vocabulary. Standard easings, durations, reduced-motion

### 24 component primitives

Built on Radix UI. Styled against design tokens. Storybook stories and unit tests for each.

`Button` · `Input` · `Textarea` · `Select` · `Checkbox` · `Switch` · `Slider` · `Tabs` · `Dialog` · `Sheet` · `Drawer` · `Popover` · `Tooltip` · `Toast` · `Badge` · `Avatar` · `Card` · `Separator` · `Progress` · `Skeleton` · `Spinner` · `EmptyState` · `Code` · `CommandPalette`

### Session view

Three resizable panes: agent trace (left), Neko WebRTC live browser (center), artifact list (right). Structured events streamed over SSE. Collapsible. Keyboard navigable.

### Replay mode

Completed sessions as a scrubbable timeline. Drag the playhead. Jump to any tool call. Watch screenshots and DOM diffs side-by-side.

### Share links

Signed share tokens. Read-only replay. No cost data, no internal IDs. Expiry and optional passphrase enforced.

### Onboarding

Multi-step flow: API key entry → permission consent → first task suggestions. Writes to `localStorage` and `~/.mantle/config.json`. Idempotent.

### Mobile layouts

All screens ship dedicated mobile breakpoints. Three-pane desktop becomes tabbed single-pane below 768px. Touch-aware Neko wrapper.

### Accessibility

Full WCAG AA. Keyboard navigation for the complete task flow. Reduced-motion respected. Color contrast verified by Lighthouse across both themes.

---

## Live Computer View

Most agent frameworks hide their browser. Mantle streams it back.

A real [Neko](https://neko.m1k1o.net/) WebRTC virtual browser lives inside the sandbox. When the agent navigates, clicks, types, or evaluates — you see it happen in real time. No screenshot polling. No fake animation. No SSE-throttled image strip.

- **Trust by inspection.** See what the agent sees. Intervene before destructive actions.
- **Debugging by witness.** Watch a task fail at step 7 of 10. No log archaeology.
- **Portable proof.** A `SKILL.md` author demos their skill; the WebRTC stream is the evidence.

---

## Wide Research

```python
from wide_research.dispatcher import dispatch_research

results = await dispatch_research(
    query="latest self-hosted LLM agent frameworks",
    n_agents=10,
    backends=["brave", "exa"],
)
```

Ten sandboxed subagents fan out in parallel via `asyncio.gather`. A merger collates, deduplicates, and produces a unified summary. Wall-clock time is roughly that of a single sequential search.

---

## Engineering invariants

These rules the codebase will not violate. Enforced by pre-commit hooks, the auditor, or both.

1. **Everything is self-hostable.** No required SaaS.
2. **License-clean.** Every dep passes `license-review` before merge.
3. **CodeAct sandboxing is non-negotiable.** Agent never executes on the host.
4. **Chromium sandbox is on. Always.**
5. **Cost ceiling is server-trusted.** Middleware reads `usage` from upstream, writes to `gateway_costs`.
6. **Reversible by default.** State-mutating tools require `confirm: true`.
7. **Gateway binds `127.0.0.1`** unless `MANTLE_PUBLIC=true`.
8. **Atomic state.** Orchestrator survives `kill -9`. State persists via `fsync` + `rename`.

**Sandbox hardening:**

```python
image        = "python:3.12-slim"
user         = "1000:1000"
mem_limit    = "512m"
cpu_quota    = 100_000  # ~1.0 CPU
security_opt = ["no-new-privileges:true"]
exec_timeout = 120
```

---

## Honest gaps

- **WebVoyager-300** — Best result is 78% with Opus 4.6. The benchmark is hard. Cheaper planners fall short (Qwen3-235B at 12% is the floor).
- **Voice latency p95** — 2153 ms, elevated by Kokoro's first-iteration cold start. p50 of 365 ms is the steady-state number.
- **STT on CPU** — Faster-Whisper at `int8` runs roughly real-time. Sub-100 ms STT requires a GPU.
- **Tauri AppImage** — DEB and RPM compile. AppImage bundling fails on icon manifest and is skipped.

Full audit log in [`AUDIT_2026_05_16.md`](AUDIT_2026_05_16.md). Every claim is reproducible.

---

## Documentation

| Document | Contents |
|---|---|
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Component graph, data flow, request lifecycle |
| [`docs/SECURITY.md`](docs/SECURITY.md) | Threat model, sandboxing, key handling, SSRF policy |
| [`docs/SKILL_AUTHORING.md`](docs/SKILL_AUTHORING.md) | Writing a `SKILL.md`, frontmatter schema, validation |
| [`MANTLE_V1_2_RELEASED.md`](MANTLE_V1_2_RELEASED.md) | v1.2 release notes, Lighthouse scores, cost summary |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Dev setup, coding style, commit format, PR flow |

---

## Reproduce locally

```bash
# 1. Clone with submodules
git clone --recursive https://github.com/jcartu/rasputin-mantle && cd rasputin-mantle

# 2. Configure
cp .env.example .env
$EDITOR .env   # ANTHROPIC_API_KEY, VLLM_BASE_URL, VLLM_API_KEY

# 3. Install
uv sync
pnpm install

# 4. Bring up full stack
docker compose -f infra/compose.dev.yml up -d

# 5. Verify
make verify

# 6. Run the web UI
pnpm --filter web dev   # http://127.0.0.1:3000
```

---

## Citations

- **CodeAct** — Wang et al., *Executable Code Actions Elicit Better LLM Agents*, ICML 2024. [arXiv:2402.01030](https://arxiv.org/abs/2402.01030)
- **WebVoyager** — He et al., *WebVoyager: Building an End-to-End Web Agent with Large Multimodal Models*, ACL 2024. [arXiv:2401.13919](https://arxiv.org/abs/2401.13919)
- **LoCoMo** — Maharana et al., *Evaluating Very Long-Term Conversational Memory of LLM Agents*, ACL 2024. [arXiv:2402.17753](https://arxiv.org/abs/2402.17753)
- **Neko** — [m1k1o/neko](https://github.com/m1k1o/neko) — WebRTC virtual browser
- **MCP** — [Model Context Protocol](https://modelcontextprotocol.io/) — JSON-RPC 2.0

---

## License

[MIT](LICENSE). Every dependency is OSI-approved. The `license-review` CI gate refuses non-compatible licenses.

---

<br/>

<p align="center">
  <sub>Hand it a goal. Watch it work. Keep the keys.</sub>
</p>
