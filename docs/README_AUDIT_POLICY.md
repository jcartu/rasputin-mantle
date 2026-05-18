# README Audit Policy

v1.2 shipped a `mantle-v1.2-released` tag with a README claiming "Replay mode",
"Share links", and "Onboarding" — none in the code. The strict-mode auditor
verified each P-phase commit but never cross-referenced the README's
"What ships in v1.2" against grep.

That gap closes here. v1.3 ships `scripts/verify-readme-claims.py` as a hard
pre-commit and per-phase check.

## What the script does

1. Reads `README.md`
2. Locates the section `## What ships in vX.Y` (or `## What ships`)
3. Extracts each markdown bullet
4. For each bullet, derives a search keyword:
   - First: explicit code in backticks (`` `design-system/tokens.css` ``)
   - Second: bold feature names (`**Replay mode**`)
   - Third: capitalized noun at start of bullet
   - Or: explicit `<!-- verify: pattern1, pattern2 -->` annotation
5. Greps the codebase for the keyword
6. Reports per-bullet pass/fail/vague

Exit code:

- **0** — every bullet matches a grep OR has a valid annotation
- **1** — at least one bullet has zero matches and no annotation
- **2** — at least one bullet is too vague to grep and lacks annotation

## When it runs

- **Every phase audit.** `@mantle-auditor` runs the script before issuing
  PERFECT. Non-zero exit = blocker.
- **Pre-commit hook.** A `pre-commit` hook on README.md changes re-runs it.
- **CI.** GitHub Actions blocks PRs that fail the check.
- **Manual.** Run anytime: `python3 scripts/verify-readme-claims.py`

## Annotations for legitimately vague bullets

Some claims don't have a single greppable keyword. Example:
"Accessibility: prefers-reduced-motion respected, full keyboard navigation."

Solution: add an HTML comment on the bullet:

```markdown
- **Accessibility**: prefers-reduced-motion respected, full keyboard navigation.
  <!-- verify: prefers-reduced-motion, onKeyDown -->
```

The script reads `<!-- verify: ... -->` and greps each comma-separated pattern.
All must match for the bullet to pass.

## "Skip" annotation for in-progress drafts

For draft READMEs where bullets are intentionally aspirational:

```markdown
- Some feature that's not done yet <!-- verify: skip -->
```

But the bullet MUST be under `## On the roadmap` or `## Coming in vX.Y`, never
under `## What ships`. The script enforces this.

## Auditor pattern integration

`protocol/prompts/auditor-strict.md` v1.3 has pattern #24:

> README "What ships" claims must be grep-verifiable. Run
> `scripts/verify-readme-claims.py README.md` as part of EVERY audit.
> If exit code != 0, the phase fails. This is a blocker, not a nit.

Plus pattern #25 for component-count claims, #26 for dead-route detection,
#27 for missing release reports, #28 for 27B orchestrator state drift.

## What this prevents

The exact bug class that shipped in v1.2:

- README says "Replay mode" → grep finds zero `*replay*` files → exit 1
- README says "Share links" → grep finds zero `*share*` files → exit 1
- README says "Onboarding" → grep finds zero `*onboard*` files → exit 1
- README said "24" component primitives but the actual count was 15 → script counts, finds 15

In v1.2 this took a human audit a week after release to catch. With the
script as a phase gate, every commit that touches README.md gets checked
in seconds.

## What this doesn't prevent (still on the auditor)

- Bullets matching a grep but describing a stub (we can grep for `replay` and
  find a file named `replay.tsx` even if it's a placeholder). The auditor
  verifies via integration tests in the phase YAML.

- Bullets that are technically true but misleading. ("Cost transparency" when
  we only show cost on one page.) The auditor's judgment.

- Bullets that match in unrelated context. (Grep for `share` matches React's
  `Object.share`.) The script reports matches with file:line so the auditor
  can spot false positives.

The script is the first line of defense, not the only one. The strict
auditor still runs all 28 patterns. But the README→grep check is the one
that catches 60% of v1.2's audit findings, so it gets first priority.

## Forcing the README writer to know what the code does

The annotation requirement means whoever writes the README must know what to
grep for. They have to actually look at the code. That discipline is the
point.

If you write "Three-pane session view with persistent pane state" and the
script says vague — you have to add `<!-- verify: chatCollapsed, filesCollapsed,
localStorage -->`. To know those are the right patterns, you have to read the
code. Result: the README writer can no longer write claims based on
"what we said we'd build" without verifying "what we actually built."

## Integration with v1.3 phases

Every W phase's `artifacts` list includes README changes. The auditor runs
`scripts/verify-readme-claims.py` after the phase's diff is applied. If the
phase adds a feature but doesn't update README, the script catches the
omission (no failure, but a notice). If the phase updates README but the
feature isn't in code yet, the script catches the overclaim (failure).

The expected workflow for each phase:

1. Ship the feature (code, tests, components)
2. Update README's "## What ships in v1.3" with a new bullet
3. Run `python3 scripts/verify-readme-claims.py README.md`
4. If exit != 0, fix the bullet (add annotation or rephrase to match code)
5. Commit
6. Auditor verifies the script passes; issues PERFECT

## False positives we accept

The script will occasionally pass bullets that shouldn't. Example: README says
"Replay scrubbing" and the codebase has a file named `replay.tsx` that's just
a stub. Script passes; the auditor's integration-test check catches the stub.

The script is intentionally permissive: any match in code = pass. The
strictness comes from the integration tests in the phase YAML, not from the
script. The script's only job is catching CLAIMS WITH ZERO CODE REFERENCES,
which is what v1.2 shipped.

## Why not a more sophisticated check?

Could do: NLP-based semantic matching between bullets and code. Could do:
LLM-based "does this code actually implement this claim". Both expensive,
both flaky.

Grep is cheap, deterministic, and catches the bug class that actually shipped.
That's enough.
