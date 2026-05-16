#!/usr/bin/env bash
set -euo pipefail

# R0 Ship Verification Script
# Mechanically verifies every R0 ship criterion

echo "=== R0 Ship Verification ==="
echo ""

FAILED=0

# Helper function to check file existence and non-empty
check_file_exists() {
    local file="$1"
    if [[ ! -f "$file" ]]; then
        echo "[FAIL] File does not exist: $file"
        return 1
    fi
    if [[ ! -s "$file" ]]; then
        echo "[FAIL] File is empty: $file"
        return 1
    fi
    return 0
}

# Check 1: All required artifacts exist and are non-empty
echo "[CHECK] All required artifacts exist and are non-empty"
REQUIRED_FILES=(
    "protocol/orchestrator.py"
    "protocol/state.py"
    "protocol/agents/auditor.py"
    "protocol/agents/planner.py"
    "protocol/agents/executor.py"
    "protocol/prompts/auditor-strict.md"
    "protocol/prompts/planner.md"
    "protocol/prompts/executor.md"
    "protocol/phases/phase-R0.yaml"
    "protocol/phases/phase-R1.yaml"
    "protocol/phases/phase-R2.yaml"
    "protocol/phases/phase-R3.yaml"
    "protocol/phases/phase-R4.yaml"
    "protocol/phases/phase-R5.yaml"
    "protocol/phases/phase-R6.yaml"
    "protocol/scripts/verify-phase.sh"
    "protocol/scripts/banned-phrases.txt"
    "protocol/scripts/banned-phrases.sh"
    "protocol/scripts/health-check.sh"
    "protocol/scripts/hooks/pre-commit"
    "Makefile"
    "docs/RASPUTIN_MANTLE_BUILD_PLAN.md"
    "docs/AUDIT_2026_05_16.md"
    "docs/AUDIT_LOOP.md"
    "docs/ORCHESTRATOR.md"
    ".github/workflows/phase-verify.yml"
    ".github/workflows/license-gate.yml"
    ".github/workflows/eval-nightly.yml"
    ".github/workflows/absorb-nightly.yml"
)

for file in "${REQUIRED_FILES[@]}"; do
    if ! check_file_exists "$file"; then
        FAILED=1
    fi
done

if [[ $FAILED -eq 0 ]]; then
    echo "[PASS]"
else
    echo "[FAIL] Some required artifacts are missing or empty"
    exit 1
fi

# Check 2: Python import succeeds
echo "[CHECK] Python import: protocol.orchestrator"
if python -c 'import protocol.orchestrator' 2>/dev/null; then
    echo "[PASS]"
else
    echo "[FAIL] Cannot import protocol.orchestrator"
    exit 1
fi

# Check 3: All 7 phase YAMLs parse via verify-phase.sh
echo "[CHECK] All 7 phase YAMLs parse via verify-phase.sh"
PHASES=("R0" "R1" "R2" "R3" "R4" "R5" "R6")
for phase in "${PHASES[@]}"; do
    if ! bash protocol/scripts/verify-phase.sh "$phase" >/dev/null 2>&1; then
        echo "[FAIL] Phase $phase verification failed"
        exit 1
    fi
done
echo "[PASS]"

# Check 4: banned-phrases.sh exits 0
echo "[CHECK] protocol/scripts/banned-phrases.sh exits 0"
if bash protocol/scripts/banned-phrases.sh >/dev/null 2>&1; then
    echo "[PASS]"
else
    echo "[FAIL] banned-phrases.sh did not exit 0"
    exit 1
fi

# Check 5: docs/AUDIT_LOOP.md does NOT contain 'Sisyphus' (case-insensitive)
echo "[CHECK] docs/AUDIT_LOOP.md does NOT contain 'Sisyphus' (case-insensitive)"
if grep -qi "sisyphus" docs/AUDIT_LOOP.md; then
    echo "[FAIL] docs/AUDIT_LOOP.md contains 'Sisyphus'"
    exit 1
else
    echo "[PASS]"
fi

# Check 6: docs/ORCHESTRATOR.md does NOT contain 'Sisyphus'
echo "[CHECK] docs/ORCHESTRATOR.md does NOT contain 'Sisyphus' (case-insensitive)"
if grep -qi "sisyphus" docs/ORCHESTRATOR.md; then
    echo "[FAIL] docs/ORCHESTRATOR.md contains 'Sisyphus'"
    exit 1
else
    echo "[PASS]"
fi

# Check 7: Forbidden patterns absent
echo "[CHECK] Forbidden patterns absent"
FORBIDDEN_PATTERNS=(
    "drift-check\.py.*sleep"
    "TODO: real drift check"
    "litellm.*master.*key"
)

PATTERN_FAILED=0
for pattern in "${FORBIDDEN_PATTERNS[@]}"; do
    if grep -r "$pattern" protocol/ docs/ .github/ 2>/dev/null | grep -v ".git" | grep -v "verify-r0-ship.sh" | grep -v "\.yaml" >/dev/null; then
        echo "[FAIL] Found forbidden pattern: $pattern"
        PATTERN_FAILED=1
    fi
done

if [[ $PATTERN_FAILED -eq 0 ]]; then
    echo "[PASS]"
else
    exit 1
fi

# Check 8: .git/hooks/pre-commit exists and is executable (warn if missing, don't fail)
echo "[CHECK] .git/hooks/pre-commit exists and is executable"
if [[ -f ".git/hooks/pre-commit" ]] && [[ -x ".git/hooks/pre-commit" ]]; then
    echo "[PASS]"
elif [[ -f ".git/hooks/pre-commit" ]]; then
    echo "[WARN] .git/hooks/pre-commit exists but is not executable"
else
    echo "[WARN] .git/hooks/pre-commit does not exist (not a git repo or not installed)"
fi

echo ""
echo "=== R0 Ship Verification: ALL CHECKS PASSED ==="
