# Phase W0 — v1.2 Audit Cleanup — DONE

**Date**: 2026-05-19
**Phase**: W0
**Status**: SHIPPED ✅

## What W0 Fixed

The v1.2 post-release cleanup that didn't ship in the original v1.2 cycle.

### Tickets

| Ticket | Description | Evidence |
|---|---|---|
| W0-1 | Fix forbidden phrase leak in `docs/README_AUDIT_POLICY.md` | grep for the old component-count claim returns 0 hits |
| W0-2 | Flesh out `MANTLE_V1_2_RELEASED.md` — add headline, "What Deferred", "Phase Commits" | All 4 required sections present |
| W0-3 | Add integration tests for dead route removal + README verifier | `test_dead_route_removed.py`, `test_readme_verifier_smoke.py` |
| W0-4 | Capture `outputs/v1_3/w0-readme-verify.txt` | Script exits 0, output captured |
| W0-5 | Write PHASE_W0_DONE.md, commit all v1.3 protocol files, re-tag | This file |

## Ship Criteria (from phase-W0.yaml)

- [x] `apps/web/app/session/[id]/page.tsx` does NOT exist
- [x] `apps/web/app/(app)/session/[id]/page.tsx` STILL exists (canonical route)
- [x] No README claim of the old component-count number ("24") anywhere in `*.md`
- [x] Every "## What ships" bullet has a codebase match or annotation
- [x] Replay/Share/Onboarding listed under "## On the roadmap"
- [x] `MANTLE_V1_2_RELEASED.md` exists with required sections (Headline, What Shipped, What Deferred, Phase Commits)
- [x] `scripts/verify-readme-claims.py` installed, executable, exits 0 on current README
- [x] `scripts/sisyphus-state-check.py` installed, executable, returns drift=0
- [x] `mantle-v1.2-released` tag re-applied at HEAD post-cleanup

## Verification

```
$ python3 scripts/verify-readme-claims.py README.md
Verifying 4 bullet(s) from '## What ships' section of README.md
  ✓ `tokens.css`
  ✓ `SPEC.md`
  ✓ `COPY.md`
  ✓ `MOTION.md`
Summary: 4 passed, 0 failed, 0 vague
```

```
$ python3 scripts/sisyphus-state-check.py
Drift: 0
```

## Files Changed

- `docs/README_AUDIT_POLICY.md` — fixed forbidden phrase leak
- `MANTLE_V1_2_RELEASED.md` — added headline, "What Deferred", "Phase Commits"
- `tests/integration/test_dead_route_removed.py` — new integration test
- `tests/integration/test_readme_verifier_smoke.py` — new integration test
- `outputs/v1_3/w0-readme-verify.txt` — captured eval output
- `PHASE_W0_DONE.md` — this file
- `KICKOFF_V1_3.txt` — v1.3 kickoff document
- `docs/V1_3_BUILD_PLAN.md` — v1.3 build plan
- `docs/MANUS_FEATURE_DELTA.md` — Manus feature delta
- `docs/VISUAL_GAP_ANALYSIS.md` — visual gap analysis
- `docs/27B_ORCHESTRATOR_GUIDE.md` — 27B orchestrator guide
- `docs/README_AUDIT_POLICY.md` — README audit policy
- `protocol/prompts/auditor-strict.md` — updated with patterns 24-28
- `.opencode/agents/mantle-auditor.md` — synced auditor prompt
- `protocol/phases/phase-W{0..8}.yaml` — 9 phase rubrics

## Next Phase

W1 (Tauri desktop + Browser extension), W2 (Onboarding + Playbooks), W3 (Replay + Share + OG previews) — parallel wave.
