# Manus Feature Delta — May 19, 2026 Deep Dive

Complete survey of what Manus ships as of today vs what Rasputin Mantle ships
post-v1.2. Sources cited inline; primary references are manus.im/blog,
en.wikipedia.org/wiki/Manus_(AI_agent), and independent reviews from Q1-Q2 2026.

## Manus's release timeline (post-launch)

- **March 6, 2025** — Initial Manus invitation-only beta launch
- **June 2025** — Video generation, OneDrive integration
- **October 16, 2025** — Manus 1.5: 4× faster, unlimited context, full-stack web app deployment
- **December 1, 2025** — Manus Projects launched
- **December 15, 2025** — Manus 1.6: Max agent, Mobile Dev, Design View
- **December 17, 2025** — Manus crosses $100M ARR (fastest in startup history)
- **December 29, 2025** — Meta acquires Manus for ~$2B
- **January 19, 2026** — Manus Cloud Computer (24/7 user-owned cloud VM)
- **January 27, 2026** — Manus Skills (adopting Anthropic Agent Skills open standard)
- **February 17, 2026** — Manus rolled into Meta Ads Manager
- **March-May 2026** — Iterative product improvements; >20% MoM growth; weekly blog cadence

Current stable: **Manus 1.6** with **1.6 Lite** (free tier) and **1.6 Max** (Pro tier).
Mobile app version 26.5.1 (May 13, 2026).

## Complete current feature inventory

### Engine & reasoning
- Manus 1.6 Max (planning + reasoning flagship; 19.2% satisfaction lift)
- Manus 1.6 Lite (free-tier agent; lighter resource use)
- Smarter Wide Research (all sub-agents on Max architecture)
- Unlimited context per task (since 1.5)
- 4× faster vs April 2025 baseline (since 1.5)

### Application surfaces
- Web app (manus.im)
- macOS desktop app
- Windows desktop app
- iOS native app
- Android native app (v26.5.1 as of May 13, 2026)
- Manus Browser Operator (Chrome + Edge extension)
- "My Computer" (control PC from phone)
- API access (Team plan)
- SSO (Team plan)

### Productivity & content
- AI Slides (.pptx generation)
- Enhanced Spreadsheets (financial modeling, multi-dim matrices) — headline 1.6 feature
- Document generation (.docx, .pdf)
- Refined Web Development (internal tools with polished UI)
- Mobile Development (end-to-end mobile app builds; new in 1.6)
- AI Image generation
- Design View (interactive image-editing canvas with mask tool; new in 1.6)
- Video generation (since June 2025)
- AI Music generation
- Multimedia processing (audio/video)
- Full-stack web app deployment (since 1.5 — backend, db, auth, AI, notifications, analytics)

### Communication & integration
- Mail Manus (dedicated inbox; reads/writes emails)
- Slack integration (slash command + channel posts + @mention)
- Scheduled Tasks (cron-style recurring jobs)
- Meeting minutes (Zoom/Meet transcription + summarization)
- Manus Collab (multi-user session sharing)
- OneDrive integration (since June 2025)

### Workflow & organization
- Manus Projects (persistent workspaces with KB + config inheritance + team sharing; Dec 2025)
- Manus Skills (Anthropic Agent Skills open standard; Jan 2026)
  - Skills marketplace
  - One-click "save successful workflow as Skill"
  - "Team Skill Library" — shared across team members
- Manus Playbooks (curated task templates)
- Cloud Computer (always-on cloud VM per user; Jan 2026)
- Replay any session
- Public share links (no-auth replay)

### Enterprise
- Team plan ($20/seat/mo, SSO, analytics, access controls, shared slide templates)
- Pro tiers ($20/mo, $40/mo)
- Manus Academy (gamified learning platform with certifications; partnered with Build Club)
- 24/7 Cloud Computer (Jan 2026)

### Scale claims (Manus disclosed)
- 147 trillion tokens processed since launch
- 80 million virtual computers created
- $100M ARR in 8 months (Dec 2025)
- $125M revenue run rate (incl. usage-based)
- >20% MoM growth since 1.5 release

## What we have as of v1.2 (May 18, 2026)

### Engine & reasoning
- WebVoyager-300: **78% with Opus 4.6** (verified, audited, anti-cheating-clean)
- Multi-planner support (GPT-5.5, Opus 4.6, Sonnet 4.6, Kimi K2.6) — runtime choice
- VLM screenshot fallback for opaque DOMs (S4)
- LoginWallDetector + self-correction (S5)
- Wide Research with real Brave/Exa dispatch (R1)

### Application surfaces
- Web app with three-pane session view, multi-tab agent browser, take-control,
  cost gutter, mobile responsive (P0-P3)
- Tauri config from v1.0 — **but binaries never produced** → W1
- No browser extension → W1
- No mobile native app
- No SSO
- No API

### Productivity & content
- Sandbox can run pandas/openpyxl/python-pptx but no first-class skill → W7
- No image generation
- No video generation
- No music generation
- No design canvas

### Communication & integration
- Voice (Faster-Whisper + Kokoro, live verified in v1.1)
- Memory client → rasputin-memory HTTP API
- No Slack → W6
- No mail → W6
- APScheduler infra from R5 but no UI → W6

### Workflow & organization
- Empty home page ("Select a session or create a new one") → W2
- No projects → W4 (NEW priority)
- Own skill loader but not Anthropic Agent Skills standard → W5 (NEW priority)
- No playbooks → W2
- No replay → W3
- No share links → W3

## Gap matrix → v1.3 plan

| Priority | Manus feature | We have | v1.3 phase | Estimated impact |
|---|---|---|---|---|
| 🔴 Must | Tauri desktop builds | config only | W1 | Closes credibility gap (we promised it) |
| 🔴 Must | Browser extension | none | W1 | "Send to Mantle" daily-use surface |
| 🔴 Must | Onboarding + Playbooks | empty | W2 | First-task time-to-value |
| 🔴 Must | Replay scrubber | none | W3 | UX feature people screenshot |
| 🔴 Must | Public share links | none | W3 | Manus's viral growth mechanic |
| 🔴 Must | **Manus Projects equivalent** | none | **W4 (NEW priority)** | Enterprise wedge; persistent context |
| 🔴 Must | **Agent Skills standard** | own loader | **W5 (NEW priority)** | Cross-platform compatibility |
| 🟡 Should | Slack integration | none | W6 | Common enterprise integration |
| 🟡 Should | Email integration | none | W6 | Asynchronous task triggering |
| 🟡 Should | Scheduled tasks UI | APScheduler | W6 | Cron UX |
| 🟡 Should | Slides generator | sandbox | W7 | "Make me a deck" use case |
| 🟡 Should | Spreadsheet skill | sandbox | W7 | "Financial modeling" use case |
| 🟡 Should | Document drafter | sandbox | W7 | "Write me a report" use case |
| 🟢 Defer | Mobile app development | none | v1.4+ | Massive scope (RN/Flutter agents) |
| 🟢 Defer | Design View canvas | none | v1.4+ | Cool but expensive; users have Figma |
| 🟢 Defer | AI Music gen | none | indefinite | Gimmick |
| 🟢 Defer | Video generation | none | indefinite | Huge model dependency |
| 🟢 Defer | Meeting minutes | none | v1.4+ | Integration brittleness |
| 🟢 Defer | Manus Collab (multi-user) | none | v1.4+ | Single-user is fine for v1.3 |
| 🟢 Defer | Cloud Computer 24/7 | sandbox per-session | v1.4+ | Big infra commitment |
| 🟢 Defer | SSO | none | v1.4+ | Worth it but separate sprint |
| 🟢 Defer | OneDrive / Google Drive | memory only | v1.4+ | Worth it but separate sprint |
| 🟢 Defer | Manus 1.5 unlimited context | bounded | v1.4+ | Wait for users to hit the limit |
| 🟢 Defer | Full-stack web app deploy | partial | v1.4+ | Separate vertical |

## Our wedges (don't lose these in v1.3)

These remain unique to us post-v1.3:

1. **Multi-tab agent browser** — Manus does one browser per session
2. **Take-control toggle** — user can grab cursor from agent mid-task
3. **Real-time cost gutter** — Manus's pricing is opaque; we make it visible
4. **Self-hosted, open-source, no data egress** — primary wedge post-Meta acquisition
5. **Multi-planner choice at runtime** — GPT-5.5, Opus, Sonnet, Kimi
6. **Audited, reproducible WebVoyager-300 benchmark** — every result inspectable in repo
7. **27B-orchestrated mode** — runs without Anthropic dependency for the orchestrator role
8. **Anti-cheating policy + programmatic README audit** — credibility infrastructure

## Why we're skipping the "AI generators"

Music, video, image generation are real Manus features. We skip them because:

- **Music gen**: 99% of users won't use it; the demos are cute but nobody pays $20/mo for AI music.
- **Video gen**: requires massive model dependencies (Veo, Sora-class models we can't self-host).
- **Image gen**: Design View is the interesting bit, not the generation. Image generation alone
  is commoditized (FLUX, SDXL, etc.); the canvas is the moat.

If users tell us they want these, we revisit. Right now: skip.

## Why we're skipping Manus Cloud Computer (24/7 VM)

Genuinely cool feature. But it's a fundamentally different infrastructure commitment:

- Per-session VMs spin up and tear down — current model
- 24/7 user VMs need persistent storage, persistent network identity, monitoring,
  billing-per-hour, snapshot/restore, OS update management
- That's a v1.4 vertical, not a v1.3 feature

For now: users who want this self-host on their own infrastructure (which is
the whole point of being self-hostable).

## Why we're skipping mobile app development

Building an agent that generates React Native / Flutter apps is a separate
competence from web automation. Different planners, sandboxes, testing.
v1.4+ standalone vertical, if at all. The market for self-hosted mobile-app
agents is also unclear — devs who can self-host probably also have iOS devs.

## What about the Meta acquisition impact

Meta acquired Manus for ~$2B in late December 2025. Per Meta's public roadmap:

- Manus continues operating standalone product (manus.im)
- Manus gets integrated into Meta Ads Manager (rolled out February 17, 2026)
- Long-term: integration into Facebook, Instagram, WhatsApp, Meta AI
- New Manus signups paused at acquisition time; some pricing tiers reopened later

What this means for us:

1. **Window of opportunity.** Big-company integrations slow product velocity.
   Manus 1.6 (Dec 15, 2025) is the last fully-independent release. Manus 2.0
   probably won't ship as fast as Manus 1.6 did.

2. **Enterprise concern.** Companies that won't send work to Meta's
   infrastructure now have a strong reason to look at self-hosted alternatives.
   Our positioning gets stronger.

3. **Trust shift.** Meta-owned Manus has different data handling than independent
   Manus. We don't change anything; that's the point.

Our v1.3 goal is to close the user-visible feature gap. The infrastructure
ownership gap closes itself the moment people read "owned by Meta."
