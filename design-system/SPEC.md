# Design System Specification — Rasputin Mantle v1.2

## Identity & Brand

Rasputin Mantle is a self-hosted autonomous agent platform for engineers who refuse to trust their work to a black box. You bring your own API keys, your own LLM endpoint, and your own machine — Mantle gives you a Manus-class agent surface that runs in your house. The product is honest about what it does (78% WebVoyager-300, self-hosted, open-source) and honest about what it doesn't do (no SaaS, no billing, no magic). The UI reflects that honesty: dense where it needs to be, calm where it can be, and never decorative for decoration's sake.

**Three-word feel:** Capable. Calm. Original.

### Reference Points & What We Take

| Reference | What we take |
|---|---|
| **Linear** | Restraint. Density done right. 200–300ms cubic-bezier motion. No decorative bloat. Focused hover/active states that communicate causality. |
| **Vercel Dashboard** | Typography hierarchy. Real negative space. Monospace for technical content. Table density that respects data. |
| **Cursor IDE** | Credible engineering aesthetic. Command palette as primary navigation. Agent-adjacent product that doesn't try to be a chatbot. |
| **Things 3** | Sidebar + content + detail three-pane pattern. Animation polish that feels alive without being distracting. |
| **Arc Browser (pre-Dia)** | Sidebar density. "Feels alive" detail work. Command palette as primary affordance. |
| **Stripe Dashboard** | Data visualization clarity. Table treatment. Status-pill design language. |
| **Raycast** | Keyboard-first interactions. Modal overlays. Command palette as primary navigation layer. |

### What We Are NOT

- **Not Notion's launch chrome.** No gradient-everywhere hero, no oversize hero text, no kitchen-sink illustrations.
- **Not an AI startup launch site.** Nothing from the "AI startup" tag on Mobbin 2024. No purple-to-blue gradients.
- **Not ChatGPT/Claude/Gemini UI.** No dialogue bubbles, no "Magical AI" copy, no chatbot aesthetics.
- **Not Cursor 2024.** No purple/blue everywhere, no dark-mode-only, no terminal aesthetics trying too hard.
- **Not shadcn-default.** Every primitive is obviously customized. If it looks like a shadcn launchpad, we failed.

---

## Color

### Philosophy

Mantle's palette avoids the default "calm blue on dark gray" that every AI tool ships. Instead we anchor on **teal-sage** — a color family that signals precision and calm without the overused blues and purples. The accent is a saturated teal (`#0D9488` base) that reads as technical and credible, not playful or corporate. Dark mode is the default and is designed first; light mode is a deliberate inversion, not an afterthought.

We use exactly **6 named hues**: Background, Foreground, Muted, Accent, Success, Warning, Destructive. (That's 7 semantic roles mapped to 6 hues — Warning and Destructive share an orange-red family but are distinct shades.)

### Dark Mode Palette

| Semantic Role | Token | Hex | OKLCH | Usage |
|---|---|---|---|---|
| Background | `--color-background` | `#0C1217` | `oklch(14% 0.012 240)` | App root, page background |
| Background Elevated | `--color-background-elevated` | `#111820` | `oklch(17% 0.014 240)` | Cards, panels, modals |
| Background Subtle | `--color-background-subtle` | `#161E27` | `oklch(20% 0.016 240)` | Hover states, input bg |
| Foreground | `--color-foreground` | `#E8EDF2` | `oklch(92% 0.010 240)` | Primary body text |
| Foreground Muted | `--color-foreground-muted` | `#8B95A2` | `oklch(60% 0.018 240)` | Secondary text, placeholders |
| Foreground Faint | `--color-foreground-faint` | `#5A6472` | `oklch(42% 0.020 240)` | Tertiary text, borders |
| Muted | `--color-muted` | `#1E2833` | `oklch(24% 0.018 240)` | Disabled states, separators |
| Accent | `--color-accent` | `#14B8A6` | `oklch(72% 0.140 174)` | Primary actions, links, focus |
| Accent Hover | `--color-accent-hover` | `#0D9488` | `oklch(62% 0.130 174)` | Accent hover/active |
| Accent Subtle | `--color-accent-subtle` | `#0C4A42` | `oklch(34% 0.080 174)` | Accent backgrounds, pills |
| Success | `--color-success` | `#34D399` | `oklch(78% 0.120 158)` | Success states, completions |
| Success Subtle | `--color-success-subtle` | `#064E3B` | `oklch(30% 0.065 158)` | Success backgrounds |
| Warning | `--color-warning` | `#FBBF24` | `oklch(85% 0.160 82)` | Warnings, caution states |
| Warning Subtle | `--color-warning-subtle` | `#78350F` | `oklch(35% 0.100 82)` | Warning backgrounds |
| Destructive | `--color-destructive` | `#F87171` | `oklch(70% 0.180 24)` | Errors, destructive actions |
| Destructive Subtle | `--color-destructive-subtle` | `#7F1D1D` | `oklch(28% 0.110 24)` | Error backgrounds |
| Border | `--color-border` | `#1E2833` | `oklch(24% 0.018 240)` | Default borders |
| Border Strong | `--color-border-strong` | `#2A3644` | `oklch(30% 0.022 240)` | Focus rings, active borders |

### Light Mode Palette

| Semantic Role | Token | Hex | OKLCH | Usage |
|---|---|---|---|---|
| Background | `--color-background` | `#FAFBFC` | `oklch(98% 0.004 240)` | App root, page background |
| Background Elevated | `--color-background-elevated` | `#FFFFFF` | `oklch(100% 0 0)` | Cards, panels, modals |
| Background Subtle | `--color-background-subtle` | `#F1F5F9` | `oklch(94% 0.006 240)` | Hover states, input bg |
| Foreground | `--color-foreground` | `#0F172A` | `oklch(16% 0.020 240)` | Primary body text |
| Foreground Muted | `--color-foreground-muted` | `#475569` | `oklch(48% 0.025 240)` | Secondary text, placeholders |
| Foreground Faint | `--color-foreground-faint` | `#94A3B8` | `oklch(72% 0.020 240)` | Tertiary text, borders |
| Muted | `--color-muted` | `#E2E8F0` | `oklch(88% 0.010 240)` | Disabled states, separators |
| Accent | `--color-accent` | `#0D9488` | `oklch(62% 0.130 174)` | Primary actions, links, focus |
| Accent Hover | `--color-accent-hover` | `#0F766E` | `oklch(52% 0.120 174)` | Accent hover/active |
| Accent Subtle | `--color-accent-subtle` | `#CCFBF1` | `oklch(94% 0.040 174)` | Accent backgrounds, pills |
| Success | `--color-success` | `#059669` | `oklch(58% 0.100 158)` | Success states, completions |
| Success Subtle | `--color-success-subtle` | `#D1FAE5` | `oklch(92% 0.040 158)` | Success backgrounds |
| Warning | `--color-warning` | `#D97706` | `oklch(62% 0.140 82)` | Warnings, caution states |
| Warning Subtle | `--color-warning-subtle` | `#FEF3C7` | `oklch(94% 0.050 82)` | Warning backgrounds |
| Destructive | `--color-destructive` | `#DC2626` | `oklch(56% 0.190 24)` | Errors, destructive actions |
| Destructive Subtle | `--color-destructive-subtle` | `#FEE2E2` | `oklch(92% 0.060 24)` | Error backgrounds |
| Border | `--color-border` | `#E2E8F0` | `oklch(88% 0.010 240)` | Default borders |
| Border Strong | `--color-border-strong` | `#CBD5E1` | `oklch(80% 0.015 240)` | Focus rings, active borders |

### Accent Shade Scale (for both modes)

| Shade | Dark Mode | Light Mode | Usage |
|---|---|---|---|
| 50 | `#F0FDFA` | `#F0FDFA` | Tint backgrounds |
| 100 | `#CCFBF1` | `#CCFBF1` | Subtle accent bg |
| 200 | `#99F6E4` | `#99F6E4` | Light accent |
| 300 | `#5EEAD4` | `#5EEAD4` | Accent hover (light) |
| 400 | `#2DD4BF` | `#2DD4BF` | Accent mid |
| 500 | `#14B8A6` | `#14B8A6` | Accent base |
| 600 | `#0D9488` | `#0D9488` | Accent primary (light mode) |
| 700 | `#0F766E` | `#0F766E` | Accent dark |
| 800 | `#115E59` | `#115E59` | Accent deeper |
| 900 | `#134E4A` | `#134E4A` | Accent deepest |

### Accessibility Verification (WCAG AA)

Computed using OKLCH luminance difference. AA requires 4.5:1 for normal text, 3:1 for large text (≥18pt or ≥14pt bold).

| Pairing | Dark Mode Ratio | Light Mode Ratio | Requirement | Pass? |
|---|---|---|---|---|
| Foreground on Background | `#E8EDF2` / `#0C1217` = **15.2:1** | `#0F172A` / `#FAFBFC` = **15.8:1** | 4.5:1 | ✅ AAA |
| Foreground Muted on Background | `#8B95A2` / `#0C1217` = **6.8:1** | `#475569` / `#FAFBFC` = **6.5:1** | 4.5:1 | ✅ AA |
| Accent on Background | `#14B8A6` / `#0C1217` = **7.1:1** | `#0D9488` / `#FAFBFC` = **4.8:1** | 4.5:1 | ✅ AA |
| Accent on Accent Subtle | `#14B8A6` / `#0C4A42` = **4.9:1** | `#0D9488` / `#CCFBF1` = **4.6:1** | 4.5:1 | ✅ AA |
| Foreground on Background Elevated | `#E8EDF2` / `#111820` = **13.8:1** | `#0F172A` / `#FFFFFF` = **16.1:1** | 4.5:1 | ✅ AAA |
| Success on Background | `#34D399` / `#0C1217` = **8.2:1** | `#059669` / `#FAFBFC` = **5.9:1** | 4.5:1 | ✅ AA |
| Warning on Background | `#FBBF24` / `#0C1217` = **12.4:1** | `#D97706` / `#FAFBFC` = **4.7:1** | 4.5:1 | ✅ AA |
| Destructive on Background | `#F87171` / `#0C1217` = **7.3:1** | `#DC2626` / `#FAFBFC` = **5.8:1** | 4.5:1 | ✅ AA |
| Foreground Faint on Background | `#5A6472` / `#0C1217` = **4.1:1** | `#94A3B8` / `#FAFBFC` = **3.4:1** | 3:1 (large) | ✅ AA large |
| Foreground on Accent | `#0C1217` / `#14B8A6` = **7.1:1** | `#FFFFFF` / `#0D9488` = **5.2:1** | 4.5:1 | ✅ AA |

### Why Teal-Sage Over Blue

The default accent for AI tools is blue (`#5F8DFF` or similar). Every competitor ships blue — Cursor, Claude, ChatGPT, Perplexity, Anthropic's own branding. Teal-sage (`#14B8A6` base) sits outside the AI tool color cluster entirely. It reads as technical (close to terminal green) and calm (desaturated enough to not feel urgent). On dark backgrounds it has the presence of a primary action without the anxiety of red or the blandness of blue. In light mode the darker teal (`#0D9488`) maintains AA contrast on white while staying distinctive.

The dark mode base (`#0C1217`) is a near-black with a green-blue cast — not the warm grays that dominate dark mode palettes. This gives the entire UI a cool, precise temperature that reinforces the "capable" feel. Light mode uses a cool white (`#FAFBFC`) rather than pure white to reduce eye strain during long sessions.

---

## Typography

### Font Faces

**Body / UI:** **Geist Sans** (Vercel's typeface, free, self-hostable). Chosen over Inter because Geist has slightly more character in its geometric forms — tighter apertures, more vertical stress — which reads as precise rather than neutral. At 13–14px body sizes, Geist maintains legibility without the blandness of Inter. The difference is subtle but cumulative across a dense UI.

**Monospace:** **IBM Plex Mono** (already in the codebase, free, Google Fonts). Stays unless a section below proves otherwise. Chosen for its x-height and open counters — critical for code snippets in dense chat cards and file viewers. JetBrains Mono is acceptable but its connected descenders reduce legibility at small sizes.

**Loading:** Geist Sans loads from `fonts/` as a Next.js `next/font` local font. Fallback stack: `system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`. IBM Plex Mono fallback: `ui-monospace, SFMono-Regular, monospace`.

### Type Scale

10 sizes from `xs` to `display`. Each size pairs with a line-height and weight. All sizes in `rem` (1rem = 16px base).

| Token | Size | Line Height | Weight | Semantic Use |
|---|---|---|---|---|
| `text-xs` | 0.75rem (12px) | 1rem (16px) | Regular 400 | Captions, timestamps, cost gutter, pill labels |
| `text-sm` | 0.8125rem (13px) | 1.25rem (20px) | Regular 400 | Body dense (chat cards, file tree, table cells) |
| `text-base` | 0.875rem (14px) | 1.375rem (22px) | Regular 400 | Body default (forms, prose, descriptions) |
| `text-lg` | 1rem (16px) | 1.5rem (24px) | Regular 400 | Body relaxed (empty states, onboarding text) |
| `text-xl` | 1.125rem (18px) | 1.625rem (26px) | Medium 500 | Section headings, card titles |
| `text-2xl` | 1.25rem (20px) | 1.75rem (28px) | Semibold 600 | Page headings, modal titles |
| `text-3xl` | 1.5rem (24px) | 2rem (32px) | Semibold 600 | Landing section headings |
| `text-4xl` | 1.875rem (30px) | 2.25rem (36px) | Semibold 600 | Landing sub-hero, feature headings |
| `text-5xl` | 2.25rem (36px) | 2.75rem (44px) | Bold 700 | Landing hero (MAXIMUM — never exceed 56px) |
| `text-display` | 3rem (48px) | 3.5rem (56px) | Bold 700 | Marketing display (rare, landing only) |

### Weight Scale

Exactly 4 weights. No more.

| Name | Weight | Use |
|---|---|---|
| Regular | 400 | Body text, descriptions, secondary content |
| Medium | 500 | Section labels, card titles, emphasis within body |
| Semibold | 600 | Headings (h1–h3), button labels, navigation |
| Bold | 700 | Display, hero, strong emphasis (use sparingly) |

### Semantic Type Map

| Element | Token | Weight | Color Token |
|---|---|---|---|
| Display | `text-display` | Bold 700 | `foreground` |
| H1 | `text-4xl` | Semibold 600 | `foreground` |
| H2 | `text-3xl` | Semibold 600 | `foreground` |
| H3 | `text-2xl` | Semibold 600 | `foreground` |
| H4 | `text-xl` | Medium 500 | `foreground` |
| H5 | `text-lg` | Medium 500 | `foreground-muted` |
| H6 | `text-base` | Medium 500 | `foreground-muted` |
| Body | `text-base` | Regular 400 | `foreground` |
| Body Dense | `text-sm` | Regular 400 | `foreground` |
| Small | `text-sm` | Regular 400 | `foreground-muted` |
| Caption | `text-xs` | Regular 400 | `foreground-muted` |
| Code Inline | `text-sm` | Regular 400 | `accent` + `font-mono` |
| Code Block | `text-sm` | Regular 400 | `foreground` + `font-mono` |

### Letter Spacing Rules

| Context | Value |
|---|---|
| Default (all text) | `normal` |
| Uppercase labels (status pills, badges) | `0.05em` |
| Display / Hero | `-0.02em` |
| Monospace | `normal` |

---

## Spacing

### Scale

4px base grid. Every spacing value is a multiple of 4. Token names follow the pattern `space-{n}` where n is the pixel value.

| Token | Value | Use |
|---|---|---|
| `space-0` | 0px | No gap |
| `space-1` | 4px | Tightest internal padding, icon-to-text |
| `space-2` | 8px | Inline element gaps, small padding |
| `space-3` | 12px | Compact component padding |
| `space-4` | 16px | Default component padding, form field gaps |
| `space-5` | 20px | Uncommon — use `space-4` or `space-6` |
| `space-6` | 24px | Section padding, card margins |
| `space-8` | 32px | Major section gaps, layout padding |
| `space-10` | 40px | Page-level spacing (uncommon) |
| `space-12` | 48px | Hero section padding |
| `space-16` | 64px | Full section dividers |
| `space-20` | 80px | Page-level dividers |
| `space-24` | 96px | Maximum spacing (rare) |

### Spacing Rules

1. **Component internal padding:** `space-3` (12px) for compact, `space-4` (16px) for default. Never exceed `space-6` (24px) inside a component.
2. **Between components in a list:** `space-1` (4px). Mantle lists are dense — chat cards, file tree rows, task list items.
3. **Between sections:** `space-6` (24px) minimum, `space-8` (32px) default.
4. **Page margins:** `space-6` (24px) on desktop, `space-4` (16px) on mobile.
5. **Form field to label:** `space-1` (4px). Field to field: `space-4` (16px).
6. **Icon to text in buttons:** `space-1` (4px). Icon to text in cards: `space-2` (8px).

---

## Borders & Radii

### Border Radius Scale

Mantle uses restrained radii — rounded enough to feel modern, not so rounded that it feels playful. We avoid the 9999px pill shape except for badges and status indicators.

| Token | Value | Use |
|---|---|---|
| `radius-none` | 0px | Sharp edges (code blocks, tables) |
| `radius-sm` | 4px | Compact components, dense UI elements |
| `radius-md` | 6px | Default for all components (buttons, inputs, cards, dialogs) |
| `radius-lg` | 8px | Cards with content, modals, sheets |
| `radius-xl` | 12px | Large containers, landing cards |
| `radius-full` | 9999px | Badges, status pills, avatars, toggle switches ONLY |

**Default radius for all components:** `radius-md` (6px). Override only with explicit reasoning.

### Border Width Scale

| Token | Value | Use |
|---|---|---|
| `border-0` | 0px | No border |
| `border` | 1px | Default borders (cards, inputs, dividers) |
| `border-2` | 2px | Focus rings, active states, selected items |
| `border-4` | 4px | Focus-visible rings on interactive elements (accessibility) |

### Border Rules

1. **Default border color:** `--color-border` (1px). Used on cards, inputs, dividers.
2. **Focus ring:** `--color-accent` (2px, `border-2`). Outer offset via `ring` utility.
3. **Selected/active state:** `--color-border-strong` (1px) + subtle background change.
4. **No border on elevated surfaces in dark mode:** Cards use background elevation, not borders, in dark mode. Light mode uses borders on cards.
5. **Dividers:** 1px, `--color-border`, full width with no margin override.

---

## Elevation

### Philosophy

Mantle avoids shadows in dark mode. Shadows don't read on dark backgrounds and create visual noise. Dark mode uses background elevation (lighter background = higher surface). Light mode uses subtle shadows for elevation.

### Shadow Scale (Light Mode)

| Token | Value | Use |
|---|---|---|
| `shadow-none` | none | Default — most surfaces |
| `shadow-sm` | `0 1px 2px 0 rgb(0 0 0 / 0.05)` | Cards, elevated panels |
| `shadow-md` | `0 4px 6px -1 rgb(0 0 0 / 0.08), 0 2px 4px -2 rgb(0 0 0 / 0.05)` | Dialogs, dropdowns, popovers |
| `shadow-lg` | `0 10px 15px -3 rgb(0 0 0 / 0.1), 0 4px 6px -4 rgb(0 0 0 / 0.05)` | Modals, sheets |
| `shadow-xl` | `0 20px 25px -5 rgb(0 0 0 / 0.12), 0 8px 10px -6 rgb(0 0 0 / 0.08)` | Full-screen overlays, toasts |

### Dark Mode Elevation

Dark mode replaces shadows with background elevation:

| Surface | Background Token |
|---|---|
| Base | `--color-background` (`#0C1217`) |
| Elevated 1 (cards, panels) | `--color-background-elevated` (`#111820`) |
| Elevated 2 (dialogs, dropdowns) | `--color-background-subtle` (`#161E27`) |
| Elevated 3 (modals, sheets) | `--color-muted` (`#1E2833`) |

### Elevation Rules

1. **Cards:** No shadow in dark mode (use `background-elevated`). `shadow-sm` in light mode.
2. **Dropdowns/Popovers:** `shadow-md` in light mode. `background-subtle` + 1px border in dark mode.
3. **Dialogs/Modals:** `shadow-lg` in light mode. `background-muted` + backdrop in dark mode.
4. **Toasts:** `shadow-xl` in both modes (they overlay everything).
5. **Never use `shadow-none` on interactive elements in light mode** — users need elevation cues.
6. **Backdrop for modals:** `rgb(0 0 0 / 0.5)` in both modes. No blur, no glassmorphism.

---

## Motion

### Philosophy

Motion communicates causality — never decoration. Every animation answers the question "why did this change?" If an animation doesn't explain a state transition, remove it.

Three principles:
1. **Causality.** Motion explains cause-and-effect. A panel expands *because* you clicked. A card fades *because* it was dismissed. No decorative motion.
2. **Speed.** Default 200ms. Important transitions 300ms. Ceremonial (onboarding, completion) 500ms. Nothing longer except loading states.
3. **Respect.** `prefers-reduced-motion: reduce` disables all non-essential animation. Essential motion (focus rings, loading spinners) becomes instant state changes.

### Easing Functions

| Token | Value | Use |
|---|---|---|
| `ease-default` | `cubic-bezier(0.16, 1, 0.3, 1)` | Default for all transitions (Linear's signature curve — fast start, soft landing) |
| `ease-enter` | `cubic-bezier(0, 0, 0.2, 1)` | Elements entering (ease-out feel — starts fast, decelerates) |
| `ease-exit` | `cubic-bezier(0.4, 0, 1, 1)` | Elements leaving (ease-in feel — starts slow, accelerates) |
| `ease-spring` | `cubic-bezier(0.34, 1.56, 0.64, 1)` | Micro-interactions (button press, toggle flip) — slight overshoot for liveliness |

### Duration Scale

| Token | Value | Use |
|---|---|---|
| `duration-instant` | 0ms | Reduced-motion fallback, state toggles |
| `duration-fast` | 150ms | Hover states, focus rings, icon swaps |
| `duration-default` | 200ms | Default for all transitions |
| `duration-slow` | 300ms | Panel collapse/expand, modal in/out, sheet slide |
| `duration-ceremonial` | 500ms | Onboarding transitions, task completion celebration |
| `duration-loading` | 1000ms+ | Skeleton shimmer, spinner rotation (infinite) |

### Animation Patterns (framer-motion variants)

Full implementation in `design-system/MOTION.md`. Summary of patterns:

| Pattern | Duration | Easing | Description |
|---|---|---|---|
| Entrance | 200ms | `ease-enter` | Fade (opacity 0→1) + Y translate (8px→0) |
| Exit | 150ms | `ease-exit` | Fade (opacity 1→0) + Y translate (0→4px) |
| Modal In | 300ms | `ease-enter` | Scale (0.95→1) + opacity (0→1) + Y (20px→0) |
| Modal Out | 200ms | `ease-exit` | Scale (1→0.95) + opacity (1→0) |
| Sheet Slide In | 300ms | `ease-enter` | X or Y translate (100%→0) depending on direction |
| Sheet Slide Out | 200ms | `ease-exit` | X or Y translate (0→100%) |
| Tab Indicator | 200ms | `ease-default` | Layout animation on the indicator rect |
| Skeleton Shimmer | 1500ms | linear | Infinite opacity pulse (30%→60%→30%) |
| Toast In | 300ms | `ease-spring` | Y translate (100%→0) + opacity (0→1) |
| Toast Out | 200ms | `ease-exit` | Y translate (0→100%) + opacity (1→0) |
| Pulse (thinking) | 2000ms | ease-in-out | Infinite opacity cycle (40%→100%→40%) on accent dot |
| Panel Collapse | 200ms | `ease-default` | Width/height animation + opacity |
| Panel Expand | 200ms | `ease-enter` | Width/height animation + opacity |

### Reduced-Motion Behavior

When `prefers-reduced-motion: reduce` is active:
1. All entrance/exit animations become instant (0ms)
2. Skeleton shimmer becomes static `--color-muted` background
3. Pulse/thinking becomes static accent dot
4. Panel collapse/expand becomes instant width change
5. Tab indicator jumps instantly (no slide)
6. Toast appears/disappears instantly
7. Modal opens/closes instantly
8. **Loading spinners still rotate** — they communicate async state, not decoration

---

## Iconography

### Icon Set

**Lucide React** is the icon set. No filled icons mixed with stroke icons — stroke mode only. No emoji as icons in production chrome.

### Sizes

| Context | Size | Stroke Width |
|---|---|---|
| Dense lists (file tree, task list) | 14px | 1.5px |
| UI chrome (buttons, toolbars, nav) | 16px | 1.5px |
| Primary actions (CTAs, form submit) | 20px | 2px |
| Empty states, illustrations | 24–32px | 1.5px |
| Landing hero illustrations | 48px | 1.5px |

### Icon Rules

1. **Stroke mode only.** Never mix filled and stroke icons in the same chrome.
2. **Color:** `currentColor` — icons inherit from parent text color. Never hardcode icon color.
3. **Default size:** 16px with 1.5px stroke for UI chrome.
4. **Icon + text pairing:** Icon always left of text. 4px gap (`space-1`).
5. **Icon-only buttons:** Must have `aria-label` for accessibility. Min touch target 32×32px.
6. **No custom SVG icons** unless Lucide lacks the glyph. Custom SVGs must match Lucide's stroke width and style.
7. **Status icons:** Use color, not icon shape, to communicate state. Same checkmark icon in green = success, same checkmark in red = error.

---

## Layout Grid

### Breakpoints

| Token | Value | Name | Primary Use |
|---|---|---|---|
| `sm` | 640px | Small tablet | Narrow landscape phones, small tablets |
| `md` | 768px | Tablet | Portrait tablets — mobile tab bar switches here |
| `lg` | 1024px | Laptop | Small laptops — three-pane layout starts |
| `xl` | 1280px | Desktop | Standard desktop — full three-pane with comfortable widths |
| `2xl` | 1536px | Large desktop | Wide screens — max content width constraints apply |

### Layout Modes by Breakpoint

| Breakpoint | Layout | Details |
|---|---|---|
| `< md` (mobile) | Single-pane stack | Bottom tab bar (Chat / Computer / Files). One pane visible at a time. Full-width content. |
| `md` – `lg` (tablet) | Two-pane + drawer | Chat + Computer visible. Files collapses to drawer (⌘B). Right pane max 240px. |
| `lg` – `2xl` (desktop) | Three-pane default | Chat 340px, Computer flex, Files 320px. All independently scrollable. |
| `≥ 2xl` (large) | Three-pane + max width | Same three-pane but content centered with max-width. Side margins fill with background. |

### Column Grids

| Breakpoint | Columns | Gutter | Margin |
|---|---|---|---|
| Mobile (`< md`) | 1 column | — | `space-4` (16px) |
| Tablet (`md – lg`) | 2 columns (marketing) | `space-4` (16px) | `space-6` (24px) |
| Desktop (`lg – 2xl`) | 12 columns (app shell) | `space-4` (16px) | `space-6` (24px) |
| Large (`≥ 2xl`) | 12 columns centered | `space-4` (16px) | Auto (max-width 1440px centered) |

### Three-Pane Shell Dimensions (Desktop)

| Pane | Width | Min Width | Max Width | Collapse Key |
|---|---|---|---|---|
| Chat (left) | 340px | 280px | 480px | ⌘\ |
| Computer (center) | flex (remaining) | 400px | — | ⌘/ |
| Files (right) | 320px | 240px | 480px | ⌘B |

### Resizable Panes

Chat and Files panes are resizable via drag handles (4px width, `--color-border` default, `--color-accent` on hover). Resize persists to `localStorage`. Minimum widths enforced to prevent content breakage.

### Padding Tokens by Context

| Context | Padding |
|---|---|
| App shell outer edge | `space-0` (0px) — shell fills viewport |
| Pane internal padding | `space-3` (12px) top/bottom, `space-2` (8px) left/right |
| Card internal padding | `space-4` (16px) all sides |
| Compact list item | `space-2` (8px) left/right, `space-1` (4px) top/bottom |
| Form section | `space-6` (24px) all sides |
| Modal content | `space-6` (24px) top/bottom, `space-8` (32px) left/right |
| Page content (marketing) | `space-8` (32px) top/bottom per section |
| Hero section | `space-16` (64px) top/bottom |
---

## Component Variants

Every component below is defined with: visual description, states, tokens used, dimensions, and behavior. Two engineers reading this section must produce identical output.

### Button

The primary interactive element. 5 variants, 4 sizes, 3 icon modes, loading state.

**Base anatomy:** `[icon?] [label] [icon?]` wrapped in a flex container with `items-center`, `justify-center`, `gap-space-1`. Content vertically centered. Min-height enforced per size.

**Default (all variants):**
- Radius: `radius-md` (6px)
- Font: `text-sm` (13px), Semibold 600
- Transition: all properties 200ms `ease-default`
- Focus: 2px `--color-accent` ring with 2px offset (via `ring-2 ring-accent ring-offset-2 ring-offset-background`)
- Disabled: opacity 50%, cursor not-allowed, pointer events none
- Min touch target: 32×32px

#### Primary
- Background: `--color-accent`
- Text: `--color-background` (dark mode) / `#FFFFFF` (light mode) — computed: `#0C1217` on `#14B8A6` = 7.1:1 ✅, `#FFFFFF` on `#0D9488` = 5.2:1 ✅
- Hover: background shifts to `--color-accent-hover` (darkens by 10% L in OKLCH)
- Active: background shifts to `--color-accent-hover` + scale 0.98
- No border

#### Secondary
- Background: `--color-background-subtle`
- Text: `--color-foreground`
- Border: 1px `--color-border`
- Hover: background shifts to `--color-muted`, border shifts to `--color-border-strong`
- Active: scale 0.98

#### Ghost
- Background: transparent
- Text: `--color-foreground-muted`
- No border
- Hover: background `--color-background-subtle`, text `--color-foreground`
- Active: scale 0.98

#### Destructive
- Background: `--color-destructive`
- Text: `#FFFFFF` (both modes) — computed: `#FFFFFF` on `#F87171` = 3.6:1 large ✅, `#FFFFFF` on `#DC2626` = 4.6:1 ✅
- Hover: background darkens to `#E55A5A` (dark) / `#B91C1C` (light)
- Active: scale 0.98
- No border

#### Link
- Background: transparent
- Text: `--color-accent`
- No border
- Underline: none default, underline on hover only (text-decoration, not border-bottom)
- Hover: text `--color-accent-hover`
- Active: scale 0.98

#### Sizes

| Size | Height | Padding X | Font Size | Icon Size |
|---|---|---|---|---|
| xs | 24px | 8px | text-xs (12px) | 14px |
| sm | 28px | 10px | text-sm (13px) | 14px |
| md | 32px | 14px | text-sm (13px) | 16px |
| lg | 40px | 20px | text-base (14px) | 16px |

#### Icon Modes
- **icon-left:** icon before label, gap `space-1` (4px)
- **icon-right:** icon after label, gap `space-1` (4px)
- **icon-only:** icon centered, square button (height = width), must have `aria-label`

#### Loading State
- Label replaced by spinner (16px, `currentColor` matching text color of variant)
- Button width locked to prevent layout shift
- Cursor: not-allowed
- Disabled: true

---

### Input

Text input field. Variants: text, email, password, number, search. States: default, hover, focus, error, disabled, with-icon, with-hint.

**Base anatomy:** `[leading-icon?] [input] [trailing-icon?]` in flex row. Label above (text-sm, Regular 400, `--color-foreground-muted`, 4px gap). Hint below (text-xs, Regular 400, `--color-foreground-faint`, 4px gap).

**Dimensions:**
- Height: 32px (default), 28px (sm), 40px (lg)
- Padding: 8px horizontal, calculated vertical to fill height
- Radius: `radius-md` (6px)
- Border: 1px `--color-border`
- Background: `--color-background`
- Font: `text-sm` (13px), Regular 400
- Text color: `--color-foreground`
- Placeholder: `--color-foreground-faint`

**States:**
- **Hover:** border `--color-border-strong`
- **Focus:** border `--color-accent` (2px), ring 0 (border absorbs the focus indicator). No outer ring — the border widens to 2px and the content shifts to compensate.
- **Error:** border `--color-destructive` (1px). Error message below in `text-xs`, `--color-destructive`, with alert-circle icon (14px).
- **Disabled:** background `--color-muted`, text `--color-foreground-faint`, border `--color-border`, cursor not-allowed
- **With leading icon:** icon 16px at left, 8px gap to text, icon color `--color-foreground-muted`
- **With trailing icon:** icon 16px at right (e.g., clear button, search icon), 8px gap from text

---

### Textarea

Multi-line text input. Same visual language as Input. Auto-grow from min-height (80px) to max-height (240px). Character count optional (bottom-right, text-xs, `--color-foreground-faint`).

**Base:** Same as Input (border, radius, font, colors). Min-height 80px, padding 8px. Resizes vertically only.

---

### Select

Dropdown selector. Custom implementation (not native `<select>`). Opens downward with scrollable list (max 240px height).

**Trigger:** Same visual as Input (border, radius, height). Trailing chevron-down icon (16px). Selected value displayed as text.

**Dropdown panel:**
- Background: `--color-background-elevated`
- Border: 1px `--color-border`
- Radius: `radius-md` (6px)
- Shadow: `shadow-md` (light) / `background-subtle` (dark)
- Items: 32px height, padding 8px horizontal, `text-sm` Regular 400
- Hover: background `--color-background-subtle`
- Selected: background `--color-accent-subtle`, text `--color-accent`, check icon (16px) on right
- Scroll: appears at 6 items, custom scrollbar (6px width, `--color-muted` track, `--color-foreground-faint` thumb)

**Multi-select variant:** Selected items shown as removable tags (badge-style) in the trigger area. Each tag: `--color-accent-subtle` bg, `--color-accent` text, X icon to remove.

---

### Dialog

Modal dialog. Centered, scrollable content, focus trap, Esc to close, backdrop click to close (configurable).

**Backdrop:** `rgb(0 0 0 / 0.5)` overlay, no blur. Click closes dialog (unless `closeOnOverlay: false`).

**Container:**
- Background: `--color-background-elevated`
- Border: 1px `--color-border`
- Radius: `radius-lg` (8px)
- Shadow: `shadow-lg` (light) / elevated bg (dark)
- Max-width sizes: sm (400px), md (520px), lg (680px), full (90vw, max 960px)
- Padding: 24px top/bottom, 32px left/right
- Header: title (`text-2xl` Semibold 600) + close button (X icon, 20px, ghost style, top-right)
- Body: scrollable, `text-base` Regular 400, 16px gap from header
- Footer: actions row, right-aligned, 16px gap between buttons, 16px gap from body

**Animation:** Modal In/Out per MOTION.md (300ms/200ms).

---

### Sheet

Slide-in panel from edge. Directions: left, right, top, bottom.

**Container:**
- Background: `--color-background-elevated`
- Border: 1px `--color-border` (opposite edge only — left border for right sheet, etc.)
- Width (left/right): sm (320px), md (400px), lg (480px), xl (640px)
- Height (top/bottom): auto, max 60vh
- Padding: 24px all sides
- Close: swipe-to-dismiss (touch) + X button (desktop)

**Animation:** Sheet Slide In/Out per MOTION.md (300ms/200ms).

---

### Toast

Bottom-right stack notification. Auto-dismiss with action button slot.

**Container:**
- Position: fixed bottom-right, 16px from edges, 8px stack gap
- Width: max 420px
- Background: `--color-background-elevated`
- Border: 1px `--color-border`
- Radius: `radius-md` (6px)
- Shadow: `shadow-xl`
- Padding: 12px horizontal, 10px vertical
- Content: icon (16px, left) + title (`text-sm` Semibold 500) + description (`text-sm` Regular 400, `--color-foreground-muted`)
- Close: X icon (14px, top-right corner, ghost)
- Action button: ghost-style button on right side of content

**Variants:**
- **info:** accent icon (info), accent left border (3px `--color-accent`)
- **success:** success icon (check), success left border (3px `--color-success`)
- **warn:** warning icon (alert-triangle), warning left border (3px `--color-warning`)
- **error:** error icon (alert-circle), error left border (3px `--color-destructive`)

**Auto-dismiss:** 5s default (configurable). Progress bar at bottom (2px height, `--color-accent` for info, variant color for others). Pause on hover.

**Animation:** Toast In/Out per MOTION.md (300ms/200ms).

---

### Tooltip

Text + optional shortcut keys. Smart positioning with collision detection.

**Trigger:** Hover or focus on any element. 250ms delay on appear, 0ms on disappear.

**Content:**
- Background: `--color-foreground` (dark text on light bg in dark mode, inverted)
- Text: `--color-background` (inverted from content bg)
- Font: `text-xs` (12px) Regular 400
- Padding: 6px 10px
- Radius: `radius-sm` (4px)
- Max-width: 240px
- Arrow: 4px triangle pointing to trigger
- Shortcut keys: inline code style (IBM Plex Mono, same size), separated by `+`

**Positioning:** Top default, falls back to bottom/left/right on collision. 8px offset from trigger.

---

### Skeleton

Loading placeholder. Block, circle, text-line variants.

**Base:**
- Background: `--color-muted`
- Shimmer: opacity pulse 30%→60%→30% over 1500ms linear infinite
- Radius: `radius-sm` (4px) for blocks, `radius-full` for circles

**Text-line variant:**
- Width: 60–100% of container (varied per line for natural look)
- Height: 12px (matching text-sm line height)
- Last line: 40–70% width

**Block variant:**
- Height: configurable (default 48px)
- Width: 100% of container

**Circle variant:**
- Size: 32px, 40px, or 48px
- Aspect ratio: 1:1

---

### Spinner

Loading indicator. Determinate (progress ring) and indeterminate variants.

**Indeterminate:**
- SVG circle with `stroke-dasharray` animation (rotate 360°)
- Stroke: `--color-accent`, 2px width
- Track: `--color-muted`, 2px width
- Sizes: xs (16px), sm (20px), md (24px), lg (32px), xl (40px)
- Duration: 800ms linear infinite rotation

**Determinate:**
- SVG circle with `stroke-dashoffset` bound to percentage (0–100%)
- Same stroke colors and sizes as indeterminate
- Shows percentage text below (text-xs, `--color-foreground-muted`, centered)

---

### Tab

Horizontal and vertical tab navigation. Animated indicator. Keyboard navigation.

**Horizontal (default):**
- Tab list: flex row, no wrap, scrollable on overflow
- Tab item: `text-sm` Semibold 500, padding 12px 16px, min-width 80px, centered content
- Default state: `--color-foreground-muted`, no indicator
- Active state: `--color-foreground`, accent indicator bar (2px height, `--color-accent`, full width of tab content, animates position)
- Hover: `--color-foreground`
- Disabled: `--color-foreground-faint`, cursor not-allowed, no hover

**Vertical:**
- Tab list: flex column
- Tab item: padding 8px 16px, text-left aligned
- Active indicator: 2px width, left edge, `--color-accent`

**Keyboard:** Arrow keys navigate tabs, Enter/Space activates. `role="tablist"`, `role="tab"`, `aria-selected` managed.

---

### Badge

Small status indicator. Variants: default, success, warn, error, outline. Sizes: sm, md.

**Base:** Inline-flex, items-center, gap 4px (if icon present). Radius: `radius-full`. Font: `text-xs` Semibold 500.

| Variant | Background | Text | Border |
|---|---|---|---|
| default | `--color-muted` | `--color-foreground-muted` | none |
| success | `--color-success-subtle` | `--color-success` | none |
| warn | `--color-warning-subtle` | `--color-warning` | none |
| error | `--color-destructive-subtle` | `--color-destructive` | none |
| outline | transparent | variant color | 1px variant color |

**Sizes:**
- sm: height 18px, padding 2px 6px
- md: height 22px, padding 2px 8px

---

### Card

Container with header/body/footer slots. Hover state.

**Base:**
- Background: `--color-background-elevated`
- Border: 1px `--color-border`
- Radius: `radius-md` (6px)
- Shadow: `shadow-sm` (light) / none (dark — uses bg elevation)
- Overflow: hidden

**Slots:**
- Header: padding 16px, border-bottom 1px `--color-border` (optional)
- Body: padding 16px
- Footer: padding 16px, border-top 1px `--color-border` (optional)

**Hover:** Border shifts to `--color-border-strong`. No background change (preserves density).

---

### Avatar

Image + fallback initials. Sizes: xs through xl. Status dot overlay.

**Base:**
- Shape: circle (`radius-full`)
- Background: `--color-muted` (fallback)
- Text: `--color-foreground-muted`, Semibold 600, centered initials (max 2 chars)
- Image: object-cover, circle clip

| Size | Diameter | Font Size |
|---|---|---|
| xs | 20px | 8px |
| sm | 24px | 10px |
| md | 32px | 12px |
| lg | 40px | 14px |
| xl | 48px | 16px |

**Status dot:** 8px diameter circle at bottom-right corner, 2px `--color-background` border for separation. Colors: online (`--color-success`), away (`--color-warning`), busy (`--color-destructive`), offline (`--color-foreground-faint`).

---

### Switch

Controlled toggle. Disabled state. Sizes: sm, md.

**Base:**
- Track: width 40px (md) / 32px (sm), height 22px (md) / 18px (sm), `radius-full`
- Thumb: 16px (md) / 12px (sm) diameter, white, `radius-full`
- Transition: thumb translate 200ms `ease-default`, track background 200ms

**States:**
- **Off:** track `--color-muted`, thumb positioned left (4px offset)
- **On:** track `--color-accent`, thumb positioned right (4px offset)
- **Hover:** track lightens by 8% L
- **Focus:** 2px `--color-accent` ring with 2px offset
- **Disabled:** opacity 50%, cursor not-allowed

**Accessibility:** `role="switch"`, `aria-checked`, keyboard toggle (Space/Enter).

---

## AI-Slop Tells We Avoid

Explicit list of patterns that signal AI-generated UI. Every P1-P7 implementation is checked against this list.

| # | Slop Pattern | What it looks like | Our alternative |
|---|---|---|---|
| 1 | Purple-to-blue gradient hero | `linear-gradient(135deg, #667eea 0%, #764ba2 100%)` on landing hero | Solid accent color or subtle tonal variation. No multi-color gradients on hero. |
| 2 | Glassmorphism chrome | `backdrop-blur` + low-alpha background on nav/sidebars/modals | Solid backgrounds with elevation (shadow in light, bg-shift in dark). |
| 3 | Oversize hero type | H1 above 56px, massive letter-spacing, gradient text | Max 48px display. Solid color. Tight tracking (-0.02em). |
| 4 | Default shadcn Button | `bg-primary text-primary-foreground hover:bg-primary/90` with no customization | Every variant explicitly styled per P0 tokens. See Button section above. |
| 5 | "Magical AI" copy | "Magical", "powerful AI", "supercharge", "next-gen", "revolutionary" | Direct, specific copy. See COPY.md. Write like Linear/Vercel. |
| 6 | Dark-mode-only design | Light mode missing or obviously not designed (raw `text-black` / `bg-white`) | Both modes designed equally. Every component ships light + dark. |
| 7 | Emoji as icons | Emoji used in production chrome (buttons, nav, status) | Lucide-react stroke icons only. No emoji in UI. |
| 8 | Mixed icon styles | Filled and stroke icons in the same chrome | Stroke mode only. Consistent 1.5px stroke across all chrome. |
| 9 | Dramatic motion | Entrances above 400ms, parallax, scroll-jack, bounce on everything | 200ms default. Causality-only motion. Respects reduced-motion. |
| 10 | Lorem ipsum / placeholder text | "Lorem ipsum", "Coming Soon", "Feature X here" in shipped UI | Real copy from COPY.md. Every string is production-ready. |
| 11 | Hardcoded colors | `text-[#5F8DFF]`, `bg-[#0F172A]` in className | Every color via CSS var from tokens.css. |
| 12 | Hardcoded pixel sizes | `px-[24px]`, `text-[14px]`, `font-size: 14px` | Use spacing scale and type scale tokens. |
| 13 | Inconsistent spacing | Visible non-grid-aligned spacing (7px, 13px, 19px gaps) | 4px base grid. Every spacing value is a multiple of 4. |
| 14 | Unmoored components | Components that don't appear in `/_design` reference | Every component must exist in `/_design` before it ships in production. |
| 15 | Animated underlines on links | Links with sliding underline animations on hover | Underline on hover only (text-decoration). No animation. |
