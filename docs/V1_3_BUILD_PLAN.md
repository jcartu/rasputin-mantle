# Rasputin Mantle v1.3 — Build Plan (May 19, 2026)

v1.0 shipped the engine. v1.1 shipped the agent at 78% WebVoyager-300. v1.2
shipped the product surface. v1.3 ships **the features that close real Manus
gaps** + runs the build on local 27B for the first time (Opus reserved for
auditor only).

## What v1.3 is

```
                       │ Phase   │ Goal                              │ Cost  │
                       │ ──────  │ ────────────────────────────────  │ ───── │
   Wave 0 (sequential) │  W0     │ v1.2 audit cleanup                │ $0-1  │
                       │ ─────── │ ───────────────────────────────── │ ────  │
   Wave 1 (parallel)   │  W1     │ Tauri + Browser extension         │ $1-3  │
                       │  W2     │ Onboarding + Playbooks            │ $1-2  │
                       │  W3     │ Replay + Share + OG previews      │ $5-10 │
                       │ ─────── │ ───────────────────────────────── │ ────  │
   Wave 2 (parallel)   │  W4     │ Manus Projects equivalent  (NEW)  │ $2-5  │
                       │  W5     │ Agent Skills standard      (NEW)  │ $2-5  │
                       │  W6     │ Slack + Email + Scheduled         │ $3-6  │
                       │ ─────── │ ───────────────────────────────── │ ────  │
   Wave 3 (sequential) │  W7     │ Slides + Sheets + Docs            │ $15-30│
                       │ ─────── │ ───────────────────────────────── │ ────  │
   Wave 4 (final)      │  W8     │ Eval regression + release         │ $30-50│
```

Total Anthropic spend target: **$59-112** (vs $600 on v1.1 — 27B-heavy budget).

## What v1.3 is NOT

- **Not another benchmark sprint.** WV-300 = 78% remains the headline. W8
  re-runs only to confirm no regressions from v1.3 changes.
- **Not a context-engineering rewrite.** CodeAct, file-based memory, todo.md
  recitation remain v1.4+ until real users hit limits the current agent can't
  handle. (Manus 1.5 already has unlimited context — but we won't beat them by
  copying; we'll beat them by being self-hosted and audited.)
- **Not a Manus clone.** We pick features that close user-visible gaps in our
  product specifically.

## The May 19, 2026 Manus survey (full version in MANUS_FEATURE_DELTA.md)

After re-surveying Manus's product since the December 15, 2025 Manus 1.6 release
and the late-December Meta acquisition, here's the current state:

| What Manus has now | We have | v1.3 plan |
|---|---|---|
| Tauri desktop apps (Mac/Win/Linux) | config only | **W1 ships them** |
| Chrome/Edge "Browser Operator" extension | none | **W1 ships them** |
| Manus Projects (persistent workspaces + KB) | none | **W4 ships them** (NEW priority) |
| Manus Skills (Anthropic Agent Skills standard) | own skill loader | **W5 adopts standard** (NEW priority) |
| Playbooks / task templates | none | **W2 ships them** |
| Replay any session | none | **W3 ships scrubber** |
| Public share links | none | **W3 ships them** |
| Slack integration | none | **W6 ships /mantle command** |
| Mail Manus (email integration) | none | **W6 ships inbox+reply** |
| Scheduled Tasks (with UI) | APScheduler only | **W6 ships UI** |
| Slides .pptx | sandbox can run pptx | **W7 ships first-class** |
| Enhanced Spreadsheets | sandbox | **W7 ships first-class** |
| Documents .docx/.pdf | sandbox | **W7 ships first-class** |
| Manus 1.5 unlimited context | bounded | **Defer to v1.4** |
| Manus 1.6 Max planner | Opus 4.6 at 78% WV-300 | **Defer — our number is fine** |
| Full-stack web app deploy | partial | **Defer to v1.4** |
| Mobile app development | none | **Out of scope** |
| Design View image canvas | none | **Out of scope** |
| Music generation | none | **Out of scope (gimmick)** |
| Video generation | none | **Out of scope** |
| Meeting minutes (Zoom/Meet) | none | **Out of scope (brittleness)** |
| Manus Collab (multi-user) | none | **Out of scope (complexity)** |
| Cloud Computer (24/7 user VM) | sandbox per-session | **Defer to v1.4** |
| SSO (Team plan) | none | **Defer to v1.4** |
| OneDrive integration | none | **Defer to v1.4** |

## Why these specific picks

**Must-have (W1-W6):** every one corresponds to a user-visible UI surface that
people screenshot, share, and use daily. Tauri/extension/replay/share are also
already named in our public README's roadmap — credibility cost to defer further.

**Big new picks from May 19 survey:**

- **W4 — Manus Projects equivalent.** This is Manus's enterprise wedge. A
  "Project" is a persistent workspace with:
    - Knowledge base (uploaded docs, brand guidelines, code libraries)
    - Default configuration (system prompt addendum, allowed tools, default
      planner model)
    - Team sharing (visibility + edit permissions)
    - Session inheritance (every new session in the project gets the KB +
      config automatically)
  Without this, every Mantle session starts from zero. With it, a marketing
  team's "Campaign Development" project has the brand book pre-loaded, and
  every new session is on-brand from the first token. This is the single
  highest-leverage UX feature we can add.

- **W5 — Agent Skills standard adoption.** Manus integrated Anthropic's
  Agent Skills open standard in January 2026. By adopting the same format,
  we get cross-platform compatibility: any skill written for Manus also works
  on Mantle, and vice versa. Plus a marketplace (we host our own; users can
  share skills publicly or within their team). One-click "save successful
  workflow as Skill" is the user-facing magic.

**Productivity skills (W7) cost more** because the benchmark requires real
file generation + Sonnet judging across 30 tasks. Other phases stay cheap
because they're mostly 27B + Opus auditor (one call per phase).

## 27B as orchestrator — the big change

This is the first sprint where Sisyphus runs on local-vllm/qwen3.5-27b instead
of Opus. The cost saving is real (Sisyphus orchestration is ~$30 of v1.1's
$600). The risk is real too (27B drifts on long state).

Mitigations baked into v1.3:

1. **Phase scope shrunk.** Each W phase has 4-6 tickets max. v1.1 had 8-12.
2. **MAX_AUDIT_ITERATIONS = 3** (down from 5). Drift compounds; fail fast.
3. **`scripts/sisyphus-state-check.py` every 5 tickets.** Programmatic drift
   detection: compares boulder.json claims to git tag / commit / file reality.
4. **Default executor concurrency = 4** (down from 5). One less thing to track.
5. **Opus fallback on 27B errors.** OMO config: `sisyphus.fallback_models:
   ["anthropic/claude-opus-4-7"]`. If 27B errors or stalls, the specific turn
   bounces to Opus automatically. Build continues.
6. **Auditor stays Opus 4.7.** The safety net is unaffected by 27B-as-Sisyphus.

See `docs/27B_ORCHESTRATOR_GUIDE.md` for the full operating manual.

## Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| 27B-Sisyphus drifts over 9 phases | Medium | High | Smaller phases + state-check every 5 tickets + Opus fallback |
| Tauri build complexity on 3 OSes | Medium | Medium | W1 produces per-platform binaries; failing one OS doesn't block phase |
| Manus Projects schema gets messy | Medium | Medium | W4 has explicit YAML schema in artifacts; auditor verifies migrations |
| Skills standard moves while we're building | Low | Medium | Pin to Anthropic Agent Skills spec as of 2026-05-19 in docs/AGENT_SKILLS_SPEC.md |
| WV-300 regresses below 75% from v1.3 changes | Low | High | W8 gates explicitly; no sandbox changes in W4/W5/W6 affect agent |
| Productivity benchmark too easy → inflated rate | Medium | Medium | Per-format rubric; judge runs ablation on holdout |
| README claim drift returns | Low | Critical | scripts/verify-readme-claims.py enforces; auditor pattern #24 |

## Definition of done for v1.3

- W0-W8 all tagged `phase-W*-shipped` on origin/main
- `mantle-v1.3-released` tag exists AND `MANTLE_V1_3_RELEASED.md` exists
- WV-300 ≥ 75% with Opus 4.6 (regression check; v1.1 baseline 78%, ≤ 3-point drop allowed)
- Productivity benchmark ≥ 0.80 aggregate AND per format
- `scripts/verify-readme-claims.py README.md` exits 0
- README "## On the roadmap" section explicitly lists deferred features (mobile dev, Design View, music, video, meeting minutes, Collab, Cloud Computer 24/7, SSO, OneDrive, full-stack deploy, CodeAct/unlimited context) with rationale
- Anti-cheating audit clean on W8 (carried forward from v1.1)
- `scripts/sisyphus-state-check.py` returns drift=0 at every phase ship
- Every audit-log/phase-W*-iter-N.json exists for each iteration

When all that's true, v1.3 ships and we promote.
