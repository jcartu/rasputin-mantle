# AI Slop Checklist — Rasputin Mantle

Used by mantle-designer (MODE B) to audit P1-P7 implementations. Also used by mantle-auditor (patterns 24-30).

**Rule:** Even one flagged signal → FAIL. No exceptions.

---

## Signal Checklist

### 1. `gradient_on_hero`
**What:** Any multi-color gradient on the main hero section or marketing pages.
**Look for:** `linear-gradient(135deg, ...)` with more than two color stops. Especially purple-to-blue or pink-to-orange combinations.
**Check:** `grep -r "linear-gradient" apps/web/` — if any result has 3+ color stops on a hero/marketing component, flag it.

### 2. `glassmorphism`
**What:** `backdrop-blur` + low-alpha background combo on any chrome (nav, sidebar, modal backdrop).
**Look for:** `backdrop-blur`, `bg-white/xx`, `bg-black/xx` combined with blur.
**Check:** `grep -r "backdrop-blur" apps/web/` — should return zero results in production chrome.

### 3. `oversize_hero_type`
**What:** H1 above 56px on landing page.
**Look for:** `text-6xl` (48px) is the max. `text-7xl` (60px) or larger = flag. Custom `text-[64px]` or larger = flag.
**Check:** `apps/web/app/page.tsx` — verify hero heading ≤ `text-5xl` (36px) or `text-display` (48px).

### 4. `shadcn_default_button`
**What:** Button.tsx that's the default shadcn variant with `bg-primary text-primary-foreground hover:bg-primary/90`.
**Look for:** `bg-primary text-primary-foreground` in Button.tsx without further customization.
**Check:** `grep -r "bg-primary" apps/web/components/ui/Button.tsx` — if found without custom token overrides, flag it.

### 5. `magical_ai_copy`
**What:** Words like "magical", "powerful AI", "supercharge", "next-gen", "revolutionary", "unlock the power of", "AI-powered", "intelligent", "smart" (as marketing adjective).
**Look for:** These words in any user-facing string, landing page, onboarding, or marketing copy.
**Check:** `grep -riE "magical|supercharge|next-gen|revolutionary|unlock the power|ai-powered" apps/web/` — zero results expected.

### 6. `dark_mode_only`
**What:** Light mode either missing or obviously not designed.
**Look for:** Components that use raw `text-black` or `bg-white` (should use `text-foreground` / `bg-background`). Components that only look right in dark mode.
**Check:** Toggle to light mode on `/_design` page — every component must render correctly.

### 7. `emoji_ui`
**What:** Emoji used as icons in production chrome.
**Look for:** Unicode emoji characters in component JSX (not in user-generated content).
**Check:** `grep -rP "[\x{1F600}-\x{1F64F}\x{1F300}-\x{1F5FF}\x{1F680}-\x{1F6FF}\x{1F1E0}-\x{1F1FF}\x{2600}-\x{26FF}\x{2700}-\x{27BF}]" apps/web/components/` — zero results.

### 8. `mixed_icon_styles`
**What:** Filled and stroke icons mixed in the same chrome.
**Look for:** `lucide-react` imports of both `Circle` and `CircleDot` in the same component. Or any filled icon variant alongside stroke variants.
**Check:** `grep -r "import.*from 'lucide-react'" apps/web/` — verify only stroke-style icons are used.

### 9. `dramatic_motion`
**What:** Entrances above 400ms, parallax, scroll-jack.
**Look for:** `duration` > 400 in framer-motion variants (except loading states). `useScroll`, `useTransform` for parallax effects.
**Check:** `grep -rE "duration.*[4-9][0-9]{2}|duration.*[1-9][0-9]{3}" apps/web/` — should only appear in loading/skeleton contexts.

### 10. `lorem_ipsum`
**What:** Any placeholder text anywhere.
**Look for:** "Lorem ipsum", "Coming Soon", "Feature X here", "Your description here", "TODO", "PLACEHOLDER".
**Check:** `grep -riE "lorem ipsum|coming soon|feature . here|your description|placeholder|todo.*design" apps/web/` — zero results.

### 11. `inconsistent_spacing`
**What:** Visible non-grid-aligned spacing (7px, 13px, 19px gaps).
**Look for:** `p-[7px]`, `m-[13px]`, `gap-[19px]`, `padding: 7px` — any non-multiple-of-4 value.
**Check:** `grep -rE "\[(7|11|13|14|15|17|18|19|21|22|23|25|26|27|29|30|31|33|34|35|37|38|39|41|42|43|45|46|47|49|50|51|53|54|55|57|58|59|61|62|63)px\]" apps/web/` — zero results.

### 12. `unmoored_components`
**What:** Components that don't appear in `/_design` reference page.
**Look for:** Any component in `apps/web/components/` that doesn't have a corresponding preview block in `apps/web/app/_design/page.tsx`.
**Check:** Compare component list against `/_design` page sections.

### 13. `hardcoded_colors`
**What:** `text-[#5F8DFF]`, `bg-[#0F172A]` — hex colors in className.
**Look for:** `#[0-9A-Fa-f]{3,6}` in Tailwind classes or inline styles.
**Check:** `grep -rE "#[0-9A-Fa-f]{3,6}" apps/web/` — should only appear in tokens.css and design-system files.

### 14. `hardcoded_sizes`
**What:** `px-[24px]`, `text-[14px]`, `font-size: 14px` — hardcoded pixel values.
**Look for:** Arbitrary pixel values in Tailwind classes or CSS that don't map to the spacing/type scale.
**Check:** `grep -rE "\[\d+px\]" apps/web/` — verify all values are multiples of 4 (spacing) or match type scale.

### 15. `animated_underlines`
**What:** Links with sliding underline animations on hover.
**Look for:** `::after` pseudo-element with width animation on link hover.
**Check:** `grep -rE "underline.*after|after.*underline|link.*underline.*anim" apps/web/` — should use `underline` on hover only.

---

## Audit Process

1. Run each grep check above against the shipped code.
2. Manually inspect `/_design` page in both light and dark modes.
3. Score fidelity (0-10) and originality (0-10) per the mantle-designer rubric.
4. Return PASS only if fidelity ≥ 7 AND originality ≥ 7 AND zero slop signals flagged.
