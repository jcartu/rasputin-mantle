# Rasputin Mantle v1.2 Released

**Date**: 2026-05-18
**Tag**: `mantle-v1.2-released`

## Summary

Rasputin Mantle v1.2 ships a complete product surface: documented design system, 15 Radix-backed component primitives, three-pane resizable session view, Neko WebRTC live browser, mobile layouts, and full WCAG AA accessibility. The engine remains unchanged from v1.1 (78.00% WebVoyager-300 with Opus 4.6).

## What Shipped

### Design System (P0 — commit `4ebf578`)
- Complete visual design system in `design-system/`
- Teal-sage accent palette, Geist Sans + IBM Plex Mono typography
- Light and dark mode, both first-class
- `tokens.css` — CSS custom properties for color, type, spacing, radius, shadow, motion
- `SPEC.md` — component contract with layout rules and interaction states
- `COPY.md` — voice and tone guide
- `MOTION.md` — motion vocabulary with standard easings and durations

### 15 Component Primitives (P1 — commit `0461a18`)
- Built on Radix UI, styled against design tokens
- Button, Input, Tab, Dialog, Sheet, Textarea, Select, Switch, Tooltip, Toast, Badge, Avatar, Card, Skeleton, Spinner

### Layout System & Navigation Shell (P2 — commit `ff69d61`)
- Resizable three-pane layout (agent trace, live browser, artifacts)
- Shell components: Header, Sidebar, MobileTabs, CostGutter
- Responsive breakpoints with tabbed single-pane below 768px

### Session View (P3 — commit `4192c01`)
- Three resizable panes: agent trace (left), Neko WebRTC live browser (center), artifact list (right)
- Structured events streamed over SSE
- Collapsible panes, keyboard navigable

### Audit Fixes (commit `b556959`)
- Resize handle fixes, mobile wiring, responsive breakpoints

### README & Branding (commits `78d3bee`, `5158339`, `3d1d7af`)
- README redesign with inline SVGs, teal-sage branding
- Nano Banana 2 brand images
- Anchor fixes, Qwen3 claim correction, duplicate tagline removal, CHANGELOG version update

### Voice & Vision (commit `b536ed2`)
- Configurable voice service URLs via `WHISPER_URL` and `KOKORO_URL` env vars
- Raw audio response from `/synthesize`
- Vision assist module with budget, cache, and telemetry

## Phases Shipped

| Phase | Tag/Commit | Description |
|---|---|---|
| P0 | `4ebf578` | Complete visual design system |
| P1 | `0461a18` | 15 component primitives |
| P2 | `ff69d61` | Layout system & navigation shell |
| P3 | `4192c01` | Session view (killer feature) |
| P2 audit | `b556959` | Resize handles, mobile wiring, responsive breakpoints |
| Docs | `78d3bee` | README redesign with inline SVGs |
| Brand | `5158339` | Nano Banana 2 brand images |
| Audit | `3d1d7af` | README audit fixes |
| Voice/Vision | `b536ed2` | Configurable URLs, vision assist |

## WebVoyager-300 (unchanged from v1.1)

| Planner | Passed | Total | Pass Rate |
|---|---|---|---|
| Opus 4.6 | 234 | 300 | 78.00% |
| Sonnet 4.6 | 223 | 300 | 74.33% |
| GPT-5.5 | 210 | 300 | 70.00% |
| Kimi K2.6 | 208 | 300 | 69.33% |

## Engineering Invariants Held

1. Everything self-hostable — no SaaS required
2. License-clean — all deps OSI-approved
3. CodeAct sandboxing — agent never executes on host
4. Chromium sandbox always on — enforced by pre-commit hook
5. Cost ceiling server-trusted — HTTP 429 on budget exceed
6. Reversible by default — state-mutating tools require `confirm: true`
7. Gateway binds 127.0.0.1 — unless `MANTLE_PUBLIC=true`
8. Atomic state — orchestrator survives `kill -9`

## Known Limitations

- **WebVoyager-300** — 78% with Opus 4.6. TIME_SENSITIVE (66%), TOOL_BROKEN (50%), CAPTCHA (60%), LOGIN_WALL (60%) remain challenging.
- **Voice latency p95** — 2153 ms, elevated by Kokoro's first-iteration cold start. p50 of 365 ms is steady-state.
- **STT on CPU** — Faster-Whisper at `int8` runs roughly real-time. Sub-100 ms requires GPU.
- **Tauri AppImage** — DEB and RPM compile. AppImage bundling fails on icon manifest and is skipped.
- **Replay mode** — Not yet shipped. On roadmap for v1.3.
- **Share links** — Not yet shipped. On roadmap for v1.3.
- **Onboarding** — Not yet shipped. On roadmap for v1.3.

## Reproduce Locally

```bash
git clone --recursive https://github.com/jcartu/rasputin-mantle && cd rasputin-mantle
cp .env.example .env
$EDITOR .env   # ANTHROPIC_API_KEY, VLLM_BASE_URL, VLLM_API_KEY
uv sync
pnpm install
docker compose -f infra/compose.dev.yml up -d
make verify
pnpm --filter web dev   # http://127.0.0.1:3000
```

## Estimated Cost

- Design system + components: $0 (local 27B)
- README redesign + branding: $0 (local 27B)
- Auditor calls: ~$1-2 (Opus 4.7)
- **Total: ~$1-2** (vs $600+ on v1.1 cloud-heavy run)
