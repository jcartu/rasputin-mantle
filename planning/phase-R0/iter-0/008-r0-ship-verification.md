slug: 008-r0-ship-verification
package: protocol
goal: Add an R0 ship-verification script that proves all ship criteria
files_in_scope:
  - protocol/scripts/verify-r0-ship.sh
verify: "bash protocol/scripts/verify-r0-ship.sh"
wall_clock_minutes: 15
body: |
  Create `protocol/scripts/verify-r0-ship.sh` — a single bash script that mechanically verifies every R0 ship criterion from the rubric.

  The script must:
  1. Be `#!/usr/bin/env bash` with `set -euo pipefail`.
  2. Print a banner: `=== R0 Ship Verification ===`.
  3. For each check, print `[CHECK] <name>` then `[PASS]` or `[FAIL]` with details.
  4. Exit 0 only if ALL checks pass. Exit 1 on first failure.

  Checks to perform (in order):
  1. All required artifacts exist and are non-empty. Iterate over: `protocol/orchestrator.py`, `protocol/state.py`, `protocol/agents/auditor.py`, `protocol/agents/planner.py`, `protocol/agents/executor.py`, `protocol/prompts/auditor-strict.md`, `protocol/prompts/planner.md`, `protocol/prompts/executor.md`, all 7 phase YAMLs (`protocol/phases/phase-R{0..6}.yaml`), `protocol/scripts/verify-phase.sh`, `protocol/scripts/banned-phrases.txt`, `protocol/scripts/banned-phrases.sh`, `protocol/scripts/health-check.sh`, `protocol/scripts/hooks/pre-commit`, `Makefile`, `docs/RASPUTIN_MANTLE_BUILD_PLAN.md`, `docs/AUDIT_2026_05_16.md`, `docs/AUDIT_LOOP.md`, `docs/ORCHESTRATOR.md`, `.github/workflows/phase-verify.yml`, `.github/workflows/license-gate.yml`, `.github/workflows/eval-nightly.yml`, `.github/workflows/absorb-nightly.yml`.
  2. `protocol/orchestrator.py` imports cleanly: `python -c 'import protocol.orchestrator'`.
  3. All 7 phase YAMLs parse: loop and call `protocol/scripts/verify-phase.sh` on each.
  4. `protocol/scripts/banned-phrases.sh` exits 0 on the repo.
  5. `docs/AUDIT_LOOP.md` does NOT contain the word `Sisyphus` (case-insensitive grep, must NOT match).
  6. `docs/ORCHESTRATOR.md` does NOT contain `Sisyphus` (same).
  7. Forbidden patterns from rubric are absent: grep repo for `drift-check\.py.*sleep`, `TODO: real drift check`, `litellm.*master.*key` — all must be absent.
  8. `.git/hooks/pre-commit` exists and is executable (skip with warning if not installed — don't fail, just warn).

  Final line: `=== R0 Ship Verification: ALL CHECKS PASSED ===` on success.
