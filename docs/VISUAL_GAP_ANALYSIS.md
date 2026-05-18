# Visual Gap Analysis — Manus vs Mantle (May 19, 2026)

Component-by-component UI deep dive comparing Manus's product surface to what
we shipped in v1.2, with concrete v1.3 fix tickets.

The point isn't to clone Manus pixel-for-pixel. It's to identify which UI
elements are doing real work for them (and missing for us), vs which are
visual noise we can ignore.

## Manus's overall layout (the reference we're measuring against)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [≡ Projects ▾]  Mantle               [search ⌘K]  [credits 4,000] [user]  │   ← top bar
├──────────────────┬──────────────────────────────────────┬──────────────────┤
│                  │                                       │                  │
│  Project sidebar │  Manus's Computer                    │  File tree       │
│  ───────────────│  ──────────────────────────────────  │  ───────────────│
│  📁 Personal    │  [tab1] [tab2] [+]   [⛶][📷][↻]    │  /workspace/    │
│    > Today      │  ┌────────────────────────────────┐  │    ├ research/  │
│    > Yesterday  │  │                                 │  │    │  └ raw.json│
│    > Last week  │  │  <iframe Neko>                  │  │    ├ outputs/  │
│                  │  │                                 │  │    │  ├ deck.pptx│
│  📁 Marketing   │  │                                 │  │    │  └ sheet.xlsx│
│  📁 Engineering │  │                                 │  │    └ notes.md  │
│                  │  └────────────────────────────────┘  │                  │
│  [+ New project]│                                       │                  │
│                  │  Chat                                 │                  │
│                  │  ──────────────────────────────────  │                  │
│                  │  Step 1 [click] Sign up button [▾]  │                  │
│                  │       ⏱ 1.2s · 💰 $0.003            │                  │
│                  │  Step 2 [extract] Email field [▾]   │                  │
│                  │  ...                                  │                  │
│                  │                                       │                  │
│                  │  [____ message ____] [voice 🎤] [▶]  │                  │
└──────────────────┴──────────────────────────────────────┴──────────────────┘
```

Key elements (left to right):

1. **Project sidebar** (collapsible) — current project + recent sessions grouped
   by date
2. **Top bar** — search, credit counter, user menu
3. **Manus's Computer** — center pane, multi-tab browser, fullscreen/screenshot/refresh
4. **Chat with structured tool-call cards** — bottom of center pane, scrolling
5. **File tree** — right pane, workspace files with previews
6. **Message input** — bottom of center pane with voice + send

## Component-by-component gap

### ✅ Components we have and ship correctly in v1.2

| Manus has | We have | Quality |
|---|---|---|
| Three-pane layout | ✓ chat-pane, computer-pane, files-pane | A — better than Manus (we have take-control toggle + multi-tab) |
| Live computer view (Neko/RDP-style) | ✓ ComputerView with Neko iframe | A |
| Browser tabs in computer view | ✓ multi-tab built into ComputerView | **A+ (we have this, Manus does single-browser per session)** |
| Take-control toggle | ✓ ComputerView's onTakeControl | **A+ (Manus doesn't expose this)** |
| Cost transparency | ✓ cost-gutter.tsx | A — Manus credit count is opaque |
| Mobile responsive layout | ✓ mobile-tabs.tsx | A |
| Keyboard shortcuts | ✓ ⌘\ chat, ⌘B files, Esc artifact | A |
| Persistent pane state | ✓ localStorage per session | A |
| Design system tokens | ✓ 174-token tokens.css | A |

### 🟡 Components we have but ship at lower quality

| Manus has | We have | Quality | v1.3 fix |
|---|---|---|---|
| Structured tool-call cards in chat | ✓ tool-call-card.tsx | B — needs polish (expander, inline screenshot thumbnail, action icon) | W7 indirectly via productivity-skill cards |
| File tree with thumbnails | ✓ file-tree.tsx | B — no thumbnails, no syntax-highlighted preview | W3 (artifact viewer upgrade) |
| Recent sessions list | ✓ basic list in (app)/page.tsx | C — flat list, no date grouping | W2 (home page rebuild) |
| Artifact viewer | ✓ artifact-viewer.tsx | B — opens text only, no .pptx/.xlsx/.docx preview | W7 |

### 🔴 Components we don't have (real gaps)

| Manus has | We have | v1.3 fix |
|---|---|---|
| **Project sidebar with switcher** | nothing | **W4** — leftmost pane with current project, project list, recent sessions per project |
| **Knowledge base UI** (upload docs to project) | nothing | **W4** — drag-drop file uploader scoped to a project |
| **Project settings page** | nothing | **W4** — system prompt addendum, default planner, allowed tools |
| **Skill marketplace UI** | nothing | **W5** — grid of skills, install/uninstall, "save as skill" button |
| **Skill detail page** | nothing | **W5** — markdown spec, usage examples, "use in this session" button |
| **Onboarding flow** | empty home page | **W2** — three-step welcome with template picker |
| **Playbook gallery** | nothing | **W2** — categorized templates with previews |
| **Replay timeline scrubber** | nothing | **W3** — horizontal track below chat, drag handle, play button |
| **Public share badge** | nothing | **W3** — "This session is shared" banner on shared sessions |
| **Share button + URL copy UI** | nothing | **W3** — modal with copy-to-clipboard, public/private toggle, expiration |
| **OG image preview card** | nothing | **W3** — for /replay/<id>, shown when shared on Slack/Twitter |
| **Integration status badges** | nothing | **W6** — "Slack connected ✓", "Mail connected ✓" in user menu |
| **Scheduled task list page** | nothing | **W6** — list with next-run time, last-run status, run history |
| **Slash command palette** | ✓ command-palette.tsx exists but bare | **W5** — populate with skills + templates + scheduled tasks |
| **Voice input button** | none | (defer to v1.4 — we have STT backend but no UI) |
| **Credit/cost meter in top bar** | only in chat gutter | minor — could add to top-bar.tsx in W2 |

### 🟢 Components we don't have AND aren't planning to add

| Manus has | Why we skip |
|---|---|
| Design View image canvas | Out of scope — Photoshop/Figma exist |
| Music generation UI | Gimmick |
| Video preview player | Defer to v1.4 |
| Mobile app native UI | Defer to v1.4 |
| Multi-user collab cursors | Defer to v1.4 |
| Cloud Computer console | Defer to v1.4 (different infra) |

## Typography + density

Manus is **denser** than we are. Their chat messages are smaller, the tool-call
cards are tighter, and the file tree uses smaller fonts than ours. We've leaned
toward generous whitespace (good for marketing screenshots, less good for
power-user density).

Recommendation for v1.3: **don't change density yet**. We're not at the point
where users are saying "this feels sparse." First make sure the missing
components ship; then iterate on density in v1.4 if needed.

## Motion & feel

What Manus does well that we should match:

1. **Pane collapse animation** — smooth slide, not instant snap. Our v1.2 uses
   instant collapse via grid-template-columns transition. Acceptable, but a
   spring animation would feel better.

2. **Tool-call card reveal** — Manus's chat cards fade-in and slide-up by 8px
   when they first appear. Our v1.2 cards just appear. Easy upgrade in W7.

3. **Live computer view loading states** — Manus shows a skeleton of the
   browser chrome before the iframe finishes loading. We show a generic
   spinner. Small but adds polish.

4. **Confirmation modals** — Manus uses subtle slide-down sheets from the top
   for "Are you sure?". We have shadcn dialogs. Both fine.

What Manus does that we should NOT match:

1. **Gradient backgrounds** — Manus uses subtle purple-blue gradients in some
   onboarding screens. Looks AI-generated. We keep flat charcoal.

2. **Animated typing indicators** — Manus has the "Mantle is thinking..." dots
   bouncing. Trendy but distracting in real use. Our v1.2 just shows a static
   spinner; keep it.

3. **Confetti on task completion** — Manus has a confetti burst when a task
   finishes. Gimmicky for power-users.

## Empty states

Manus's empty states are uniformly: short heading + one-line description +
single CTA button. We have a mix. v1.3 should standardize on the Manus pattern
in `apps/web/components/ui/empty-state.tsx` (new component in W2).

Locations needing empty states:

- /(app)/page.tsx — "No recent sessions" (currently bare)
- /(app)/playbooks → "No saved playbooks yet" (after W2)
- /(app)/scheduled → "No scheduled tasks yet" (after W6)
- /(app)/projects/<id> → "This project has no sessions yet" (after W4)
- /(app)/skills → "No installed skills" (after W5)

## Color use

Manus uses their teal/cyan brand color (similar to our #14B8A6) for:

- Primary buttons
- Active nav items
- Progress indicators
- Hyperlinks

And uses semantic colors for:

- Green for "Connected" / "Online" / "Success"
- Amber for "Pending" / "Running" / "Warning"
- Red for "Error" / "Disconnected"
- Gray for inactive / disabled

Our v1.2 design system already has all of these. **No changes needed.**

## Information architecture / navigation

Manus's nav model:

```
Top-level:
├── Projects (sidebar)
│   ├── <Project>
│   │   ├── Sessions
│   │   ├── Knowledge base
│   │   ├── Settings
│   │   └── Members (Team plan)
├── Skills (top-bar)
├── Playbooks (top-bar)
├── Scheduled (top-bar)
└── Settings (user menu)
```

Our v1.2 nav model:

```
Top-level:
├── Sessions (sidebar — flat list)
└── Settings (user menu)
```

v1.3 target after W2+W4+W5+W6:

```
Top-level:
├── Projects (sidebar)              ← W4
│   ├── <Project>
│   │   ├── Sessions
│   │   ├── Knowledge base
│   │   └── Settings
├── Playbooks (top-bar)             ← W2
├── Skills (top-bar)                ← W5
├── Scheduled (top-bar)             ← W6
└── Settings (user menu)
    ├── Integrations (Slack/Mail)   ← W6
    └── Account
```

## Final v1.3 visual checklist

Components to ship (in W2+W3+W4+W5+W6+W7):

- [ ] Empty-state component
- [ ] Project sidebar
- [ ] Project switcher dropdown
- [ ] Knowledge base uploader
- [ ] Project settings page
- [ ] Onboarding three-step flow
- [ ] Playbook gallery
- [ ] Replay timeline scrubber
- [ ] Share modal
- [ ] Public share badge banner
- [ ] OG image preview card
- [ ] Skill marketplace grid
- [ ] Skill detail page
- [ ] "Save as skill" button
- [ ] Integration settings page
- [ ] Scheduled tasks list page
- [ ] Tool-call card polish (expander + thumbnail)
- [ ] File tree thumbnails + syntax preview
- [ ] Slash command palette populated with skills/templates
- [ ] Slide preview in artifact viewer
- [ ] Spreadsheet preview in artifact viewer
- [ ] Document preview in artifact viewer

Each component has acceptance criteria in its corresponding phase YAML.
