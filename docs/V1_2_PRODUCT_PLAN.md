# Rasputin Mantle v1.2 — Product Sprint

v1.0 shipped the engine. v1.1 shipped the agent. v1.2 ships **the product**.

## What this sprint is not

- Not another benchmark push. We're at 78% WebVoyager-300 with Opus 4.6. That number is publication-ready. Re-running it isn't worth $300.
- Not a context-engineering rewrite. CodeAct, file-based memory, todo.md recitation — those are real techniques but they only matter when users hit a workload the current agent can't handle. Build the surface first; users will tell us where the agent breaks; *then* we know what to architect for.
- Not a new framework. Browser Use, OpenHands, etc. are mentioned in the analysis doc — ignore. We have a working 78% agent. Throwing it away to rebuild on someone else's framework is the wrong direction.

## What this sprint is

A gorgeous product surface on top of the existing engine. Same architecture, same agents, dramatically better UX. By the end someone visits our hosted demo, runs an agent in 30 seconds, and posts a screenshot.

The three things that turn an agent demo into a product:

1. **Surface area that feels considered.** Real visual design, not shadcn-default. Real layout, not stacked divs. Real polish on mobile, motion, accessibility, empty states, error states.
2. **An onboarding that respects the user's time.** First-task in under 60 seconds. No API key wall on landing. Templates and starter prompts that get someone to "oh, this is useful" fast.
3. **Sharability.** Replay mode + share links. Someone runs an agent task, replays it, shares the link. The link doesn't require sign-up to view. That's how Manus actually grew — public agent traces are viral.

## What Manus does that we don't (UI-wise)

Stripped from the screenshots that circulate:

- **Three-pane session view.** Chat narration left, live computer center, file tree + artifacts right. Each pane independently scrollable. The center pane is the magic — it's a real video feed of the agent's browser.
- **Structured tool-call cards in chat.** Not "I'm clicking the Sign Up button." Instead a small card: `[Click]` icon, target description, screenshot inline, "show details" expander.
- **Replay scrubbing.** Drag the timeline to any point in a finished session, see the state at that moment (page, chat, files).
- **Public share links.** Send any task's replay to anyone, no auth required. OG image is the agent's final screenshot.
- **Task templates.** Curated starter prompts grouped by intent ("Research", "Build", "Summarize", "Schedule").
- **Sandbox file system visible.** Right pane shows `/workspace/<task>/` as a tree, with thumbnails for images, syntax-highlighted previews for code.
- **Cost transparency.** Per-step credit cost in the chat margin. You see "this turn cost 12 credits" inline.

We can ship every one of those. The hard part is taste — making it look professional, not AI-slop. That's why P0 (design system) gets 4-8 hours of Opus iteration before any front-end code is written.

## What gorgeous looks like for us

Reference points (paste these into mantle-designer's context if useful):

- **Linear** — restraint, density done right, perfect dark mode, motion that respects attention
- **Vercel dashboard** — typography hierarchy, real use of negative space, monospace for technical content
- **Cursor IDE** — agent-adjacent product with credible engineering aesthetic
- **Arc Browser (pre-Dia)** — sidebar density, command palette as primary nav, the "feels alive" detail work
- **Things 3** — for the file-tree + task list patterns

What we explicitly avoid:

- Notion's chrome-heavy launch aesthetic (gradients everywhere, oversize hero text)
- Anything that screams "I was built by Sonnet 4.6 with shadcn defaults"
- Cursor-clone purple-to-blue gradients on the landing hero
- Glassmorphism. Glassmorphism died in 2024 and we should keep it that way.

## Phases at a glance

```
   P0  Visual Design System         Opus drives, ~4-8h, $50-100
   P1  Component Primitives         Sonnet, ~1 day, $30-60
   P2  Layout System                Sonnet, ~1 day, $30-60
   P3  Session View (★ killer)      Sonnet + 27B backend, ~3 days, $60-120
   P4  Onboarding + Task Creation   Sonnet + landing copy, ~2 days, $30-60
   P5  Artifact Viewer + Replay     Sonnet + 27B file watch, ~2 days, $40-80
   P6  Mobile + Accessibility       Sonnet + 27B grunt, ~2 days, $30-60
   P7  Distribution + Launch        27B builds + Sonnet docs, ~2 days, $30-50
   ─────────────────────────────────────────────────────────────────────────
   TOTAL                            ~2-3 weeks wall clock, $300-590 disciplined
                                                          $600-1000 realistic
                                                          $1500 ceiling
```

## How 27B does maximum heavy lifting

The cost optimization the user asked for:

- **Backend tickets → 27B.** SSE broker wiring, sandbox file watch, MIME detection, Tauri config, install scripts, docker compose tweaks, CI workflow changes, test harness. All 27B. Free.
- **Frontend tickets → Sonnet 4.6.** Component implementation, layout work, animation, accessibility, motion. The cost driver but where taste matters.
- **Design + audits → Opus.** P0 design system (10-40 calls). Per-phase visual audit (1-3 calls per phase). The cost ceiling but the quality gate.
- **27B does the boilerplate, Sonnet does the taste, Opus does the judgment.**

By rough math: 60% of total ticket count goes to 27B (free), 30% to Sonnet (cheap), 10% to Opus (expensive). This is the inverse of cost-naive routing where every ticket touches Sonnet by default.

## What we measure

This is a product sprint, not a benchmark sprint. The metrics are different:

- **Time-to-first-task** (TTFT). Landing page → running task. Target ≤ 60s.
- **Visual review pass rate.** Opus-as-mantle-designer scores each shipped page out of 10 for fidelity-to-spec + originality. Target ≥ 8/10 average across all P3-P7 pages.
- **Lighthouse scores.** Landing page ≥ 95 across all four categories. Session view (heavier app shell) ≥ 90.
- **Mobile flow completion.** Playwright test runs a full task on mobile-Chrome viewport. Must pass.
- **Share-link cold load.** Public replay link, no auth, cold cache. ≤ 2s to interactive.
- **Onboarding completion.** Synthetic Playwright bot completes onboarding → first task. ≥ 95% reliability.

Crucially: we do NOT re-run WebVoyager-300. The v1.1 number is the v1.2 number. The agent is unchanged. We're decorating the engine, not retuning it.

## What v1.2 ships with that v1.1 didn't

- The three-pane session view (with real Neko, real SSE, real artifact tree)
- A landing page worth screenshotting
- An onboarding flow with curated starter prompts and templates
- Replay mode with scrubbable timeline
- Public share links with OG images
- Cost-per-step inline in chat
- Mobile-responsive across all primary screens
- WCAG-AA accessibility minimum
- One-line install (`curl ... | sh`)
- Hosted demo (Fly.io or similar)
- Tauri installers for Mac/Linux/Windows (signed where possible)
- Docs site at the chosen domain
- `MANTLE_V1_2_RELEASED.md` with screenshots, demo video links, the launch story

## What v1.2 does NOT ship

- A new benchmark number (engine unchanged)
- Auth / billing / payments (you bring your own keys)
- A multi-user collaboration mode (single user per session)
- A plugin marketplace (skills as files only — same as v1.0)
- iOS / Android native apps (mobile web is enough for v1.2)
- Voice as a primary modality (voice exists from R6 but isn't featured in v1.2 UX — that's v1.3)

## Risks specifically for this sprint

| Risk | Likelihood | Mitigation |
|---|---|---|
| P0 design system is too generic / shadcn-default | Medium | Mantle-designer prompt explicitly forbids shadcn defaults and lists 10 AI-slop tells (see auditor-strict.md additions) |
| Sonnet 4.6's frontend output looks like AI-slop | Medium-High | Every page passes mantle-designer audit before shipping; spec is detailed enough that Sonnet implements, not invents |
| Mobile experience is added at the end and falls over | High historically | P6 is its own phase with its own gate; Playwright mobile test required at every preceding phase |
| Backend feature scope grows during a "frontend" sprint | Medium | P3 is the only phase allowed to touch backend; all other phases reject backend tickets |
| Cost overruns again | Almost certain | Honest table this time + max parallelism cap of 4 (down from 8) + Sonnet over Opus where possible |
| v1.2 launches and the agent still has the v1.1 bugs that nobody noticed | Medium | P3 gate runs the v1.1 SSE smoke test; if SSE breaks during this sprint, P3 fails |

## Definition of done

- All eight `phase-P*-shipped` tags on origin/main
- `mantle-v1.2-released` tag pushed
- `MANTLE_V1_2_RELEASED.md` exists with screenshots and demo video links
- Hosted demo URL works for at least 5 sample tasks without intervention
- Lighthouse score targets met on landing and session views
- WAVE accessibility check passes on every primary screen
- Tauri DMG / DEB / RPM artifacts attached to GitHub Release
- The README on the repo shows the new screenshots, not the old brand art
- A short demo video (60-90s) embedded in the README

When that's done, we promote. Until then, no promotion.
