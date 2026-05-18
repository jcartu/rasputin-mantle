# Design Brief — Rasputin Mantle

This brief is the single most important document in v1.2. The visual design system you (mantle-designer, Opus 4.7) produce from this brief is what every subsequent phase implements against. Take 4-8 hours. Iterate. Push back if anything below is contradictory or vague.

## Who we are

Rasputin Mantle is a self-hosted open-source autonomous agent platform. Users bring their own Anthropic API key and their own vLLM endpoint and get a Manus-equivalent that runs in their house. The product is the surface; the agent underneath is competitive with Manus on benchmarks (78% WebVoyager-300, beating Manus's likely territory).

The audience is technical: hackers, indie engineers, security-conscious developers, small ML teams. They have opinions about CSS. They notice the difference between Linear's UI and a shadcn launchpad. They will not pay for slop. They will fork the repo if the README screenshot doesn't sell them in 5 seconds.

## What we want them to feel

Three words, in priority order:

1. **Capable.** Like the product was made by someone who knows what they're doing. Density done right. Real typography hierarchy. No "we ran out of time on this screen" energy.
2. **Calm.** Agent platforms are anxious products by default (something is happening that you didn't explicitly authorize). The UI should counter that — clear state, no jumping layouts, no notification spam, no "Magical AI" language.
3. **Original.** Not a Manus clone. Not a Cursor clone. Not a Linear clone. Inspired-by, not derived-from. The brand has its own opinion about typography, color, motion.

## What we want them to NOT feel

- "This is another wrapper around Claude" — sloppy ChatGPT-clone aesthetics, dialogue bubbles, "Magical AI" copy
- "This is Notion's launch page" — gradient-everywhere, oversize hero, kitchen-sink hero illustration
- "This is shadcn-default" — every primitive should be obviously customized
- "This is Cursor 2024" — purple/blue everywhere, dark-mode-only, terminal aesthetics that try too hard
- "I have to fight this UI" — friction at any obvious place

## Reference points to study before designing

Study what each does *right*:

- **Linear** — restraint, density, no decorative bloat, perfect motion timings (200-300ms cubic-bezier easing throughout), focused hover/active states
- **Vercel dashboard** — typography hierarchy, monospace for technical content, real use of negative space, table density
- **Cursor IDE** — agent product with credible engineering aesthetic, command palette as primary nav
- **Things 3** — for the sidebar + content + detail pattern, animation polish
- **Arc Browser (pre-Dia)** — sidebar density, "feels alive" detail work, command palette
- **Stripe Dashboard** — data visualization, table treatment, payment-status-pill design language
- **Raycast** — keyboard-first interactions, modal overlays, command palette as primary affordance

What we are NOT:

- Notion's launch chrome, Coda, Airtable launch pages
- Anything from a "AI startup launch site" tag on Mobbin from 2024
- ChatGPT's UI (anywhere), Claude's web UI, Gemini's web UI

## Constraints

### Tech stack constraint

The front-end already uses:
- Next.js 15 (app router, React 19)
- Tailwind 4 (we use CSS vars via `@theme`)
- shadcn/ui as the *underlying primitive set* but heavily restyled
- lucide-react for icons (we keep this — no emoji UI)
- framer-motion for animations
- IBM Plex Mono for code/monospace; you choose the body/UI face

So the design system you produce must be implementable in Tailwind 4 with CSS variables. Avoid SVG-heavy custom components when CSS can do it. Avoid anything that fights the framework.

### Constraint on density

Mantle is a tool, not a marketing site. We need to display:
- Chat narration with up to ~50 step cards in one session
- Live video feed of a browser (Neko WebRTC)
- File tree with up to ~100 files
- All three simultaneously on a desktop screen

This means dense UI by default with breathing room earned, not given. Reference Linear's task list density, not Notion's blog post layout.

### Constraint on color

You have a free hand to choose the palette. But:
- Default mode is dark. Light mode also ships. Both must look intentional, not "dark-mode + invert."
- Accent color is currently `#5F8DFF` (a calm blue) — you can change it but explain why.
- No more than 6 named hues in the palette (background, foreground, muted, accent, success, warning, destructive). Anything beyond is bloat.
- Each hue needs at least 8 shades for both modes.
- WCAG AA contrast minimum, AAA where text is small/dense.

### Constraint on type

You choose the body face. Suggestions:
- Inter (default, predictable, free)
- Geist (Vercel's, slightly more character, free)
- Söhne (paid, classier — only if we license)
- Mona Sans (GitHub's, free, neutral)

For monospace: IBM Plex Mono stays unless you have a strong reason. JetBrains Mono is acceptable.

Type scale: define at least 10 sizes (from xs to display) with line-height pairings. Define exactly 4 weights (regular, medium, semibold, bold).

### Constraint on motion

Reference Linear and Things 3. Three principles:
- Motion communicates causality (this expanded *because* you clicked) — never decorative
- Default duration 200ms, important transitions 300ms, ceremonial 500ms — nothing longer except loading
- Easing: `cubic-bezier(0.16, 1, 0.3, 1)` (Linear's signature) as default; `ease-out` for entrances, `ease-in` for exits
- Reduced-motion fallback for every animation

### Constraint on iconography

Lucide-react is the icon set. Define:
- Default icon size (probably 16px in UI chrome, 20px in primary actions, 14px in dense lists)
- Stroke weight (1.5px default, 2px for primary actions)
- Color: inherit from text color (currentColor in stroke)
- No filled icons mixed with stroke icons — pick one mode

## Deliverables for P0

Sisyphus will judge your P0 ticket "done" only when all of the following exist:

### 1. `design-system/SPEC.md` — the canonical design specification

Sections (you can reorder, but must contain):

- **Identity & Brand** — one-paragraph brand statement, three-word feel summary, named reference points and what we take from each
- **Color** — full palette with hex values for both modes, semantic role table (background, foreground, muted, accent, success, warning, destructive), accessibility check passing
- **Typography** — chosen face + monospace, full scale table with size/line-height/weight pairings, semantic use table (display, h1-h6, body, small, caption, code)
- **Spacing** — chosen scale (probably 4px or 8px base), table from 0 to 96px, semantic use rules
- **Borders + Radii** — radius scale, border width scale, semantic use
- **Elevation** — shadow scale (0-5 or 0-7), use rules (no shadow on dark mode chrome, etc.)
- **Motion** — easing functions, duration scale, semantic timing table, reduced-motion behavior
- **Iconography** — Lucide variant rules, sizes, stroke
- **Layout Grid** — desktop / tablet / mobile breakpoints, column grids per breakpoint, gutter sizes
- **Component Variants** — at minimum: Button (5 variants), Input, Select, Dialog, Sheet, Toast, Tooltip, Skeleton, Spinner, Tab. For each: visual description, states (default/hover/focus/active/disabled), tokens used
- **AI-Slop Tells We Avoid** — explicit list, with the slop pattern and our deliberate alternative

### 2. `design-system/tokens.css` — the implementable token file

CSS custom properties for everything in the SPEC. Both `:root` (light) and `.dark` blocks. Tailwind 4 `@theme` directive at the top with the semantic mappings.

### 3. `apps/web/app/_design/page.tsx` — the design system reference page

A page at `/_design` that renders every primitive in every state, in both modes (with a toggle). This is the canonical reference subsequent phases compare implementations against. It's also the test artifact: if a phase ships a Button that doesn't match the `/_design` Button, the audit fails.

The page should be navigable — sticky sidebar with sections, anchor links, easy to inspect any component in context.

### 4. `design-system/MOTION.md` — animation cookbook

Reusable framer-motion variants and Tailwind animation classes for the common patterns:
- Entrance (fade + slight Y translate)
- Exit (fade + slight Y translate, faster)
- Modal in/out
- Sheet slide-in
- Tab indicator slide
- Skeleton shimmer
- Toast in/out
- Pulse for "thinking" states
- Each with reduced-motion fallback

### 5. `design-system/COPY.md` — voice + tone guide

How we write text in the product. With Do/Don't examples.

- Sentence case for headings (not Title Case)
- Active voice
- No "Magical AI" language
- Error messages name the cause and the next step
- Empty states are useful, not coy
- Loading messages should describe what's happening if it takes >2s
- Numerics: thousand separators, decimal precision rules
- Time: relative ("3 minutes ago") for recent, absolute for older

### 6. `design-system/AI_SLOP_CHECKLIST.md` — the audit checklist

A specific list of patterns the mantle-designer (you, on subsequent phases) checks for when auditing P1-P7 implementations. At minimum the 10 hard-rules from KICKOFF_PRODUCT.txt expanded with rationale and an example image description of what each looks like in the wild.

## How to iterate

You'll do this through multiple Sisyphus delegations. Sisyphus will call you, give you the brief, you produce v0.1 of SPEC.md. Sisyphus reviews — does it cover all the deliverables? Is it specific enough? Is the color palette actually chosen, not "vibe TBD"? — and if not, calls you again with the gaps.

Target: 3-5 iterations of mantle-designer to land a v1.0 of all six deliverables. Each iteration is one Opus call costing ~$1-2.

## What "good enough to ship P0" looks like

Specific enough that two independent front-end engineers, handed only `design-system/SPEC.md` and `tokens.css`, would build the same Button. Same colors, same dimensions, same hover state, same motion timing. If there's ambiguity that requires "use your taste," P0 isn't done.

## What "too far" looks like for P0

P0 is the design system, not the implementation. Do NOT spend P0 writing components. Do NOT spend P0 building the landing page. Those are P4. P0 produces the documents that P1-P7 implement against. The single piece of `.tsx` you write in P0 is the `/_design` reference page, and only because we need a visual canonical for future audits.

## Final note

This is the most important phase. Every subsequent phase's output quality is bounded by how good P0 is. A mediocre P0 produces a beautiful-on-paper spec that 27B can't faithfully implement, that Sonnet has to interpret, and that ships as inconsistent UI. A great P0 makes the rest of v1.2 mechanical: take ticket → read spec → implement → match canonical → ship.

Don't rush. Push back. Ask Sisyphus for clarification on any constraint above that feels contradictory. Take the 4-8 hours.
