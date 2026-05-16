#!/usr/bin/env bash
# protocol/scripts/verify-phase.sh
#
# Run the mechanical floor checks for a phase. Exit 0 iff every check passes.
# This is the CHEAP gate. The full audit (Opus) runs after this passes.
#
# Usage: bash protocol/scripts/verify-phase.sh R3

set -uo pipefail

PHASE="${1:?usage: $0 <phase> (e.g. R3)}"
PHASE_FILE="protocol/phases/phase-${PHASE}.yaml"

if [ ! -f "$PHASE_FILE" ]; then
  echo "✗ phase file not found: $PHASE_FILE"
  exit 2
fi

if [ -t 1 ]; then GREEN="$(tput setaf 2)"; RED="$(tput setaf 1)"; YELLOW="$(tput setaf 3)"; BOLD="$(tput bold)"; RESET="$(tput sgr0)"; else GREEN=""; RED=""; YELLOW=""; BOLD=""; RESET=""; fi
ok()      { printf "  ${GREEN}✓${RESET} %s\n" "$*"; }
fail()    { printf "  ${RED}✗${RESET} %s\n" "$*"; failed=1; }
warn()    { printf "  ${YELLOW}!${RESET} %s\n" "$*"; }
section() { printf "\n${BOLD}▶ %s${RESET}\n" "$*"; }

PHASE_JSON=$(uv run python -c "import yaml, json; print(json.dumps(yaml.safe_load(open('$PHASE_FILE'))))")

NAME=$(echo "$PHASE_JSON" | jq -r '.name // ""')
printf "${BOLD}Phase ${PHASE}: ${NAME}${RESET}\n"

failed=0

# packages_required
section "packages_required (each must pass its own verify)"
PKGS=$(echo "$PHASE_JSON" | jq -r '.packages_required[]? // empty')
if [ -z "$PKGS" ]; then
  warn "no packages_required declared"
else
  while IFS= read -r pkg; do
    [ -z "$pkg" ] && continue
    if [ ! -d "$pkg" ]; then
      fail "package missing: $pkg"; continue
    fi
    if [ -f "$pkg/Makefile" ]; then
      if (cd "$pkg" && make verify >/dev/null 2>&1); then
        ok "$pkg make verify"
      else
        fail "$pkg make verify"
      fi
    elif [ -d "$pkg/tests" ]; then
      if PYTHONPATH=".:apps/gateway/src:packages/shared:packages/skills:packages/codeact:packages/sandbox:packages/browser:packages/voice:packages/mcp-host" \
         uv run pytest "$pkg/tests" -q --no-header >/dev/null 2>&1; then
        ok "$pkg pytest"
      else
        fail "$pkg pytest"
      fi
    else
      warn "$pkg has no Makefile or tests/ — listed but unverified"
    fi
  done <<< "$PKGS"
fi

# artifacts
section "artifacts (files must exist and be non-empty)"
ARTIFACTS=$(echo "$PHASE_JSON" | jq -r '.artifacts[]? // empty')
if [ -z "$ARTIFACTS" ]; then
  warn "no artifacts declared"
else
  while IFS= read -r a; do
    [ -z "$a" ] && continue
    if [ -f "$a" ] && [ -s "$a" ]; then ok "$a"
    elif [ -f "$a" ]; then fail "$a exists but empty"
    else fail "$a missing"; fi
  done <<< "$ARTIFACTS"
fi

# integration_tests
section "integration_tests"
ITESTS=$(echo "$PHASE_JSON" | jq -r '.integration_tests[]? // empty')
if [ -z "$ITESTS" ]; then
  warn "no integration_tests declared"
else
  while IFS= read -r t; do
    [ -z "$t" ] && continue
    if [ ! -f "$t" ]; then fail "integration test missing: $t"; continue; fi
    if PYTHONPATH=".:apps/gateway/src:packages/shared:packages/skills:packages/codeact:packages/sandbox:packages/browser:packages/voice:packages/mcp-host" \
       uv run pytest "$t" -q --no-header >/dev/null 2>&1; then
      ok "$t"
    else
      fail "$t"
    fi
  done <<< "$ITESTS"
fi

# eval_suites
section "eval_suites (each must hit minimum_pass_rate)"
N=$(echo "$PHASE_JSON" | jq -r '.eval_suites | length')
if [ "$N" = "0" ] || [ "$N" = "null" ]; then
  warn "no eval_suites declared"
else
  for i in $(seq 0 $((N - 1))); do
    SNAME=$(echo "$PHASE_JSON" | jq -r ".eval_suites[$i].name")
    SMIN=$(echo "$PHASE_JSON" | jq -r ".eval_suites[$i].minimum_pass_rate")
    SCMD=$(echo "$PHASE_JSON" | jq -r ".eval_suites[$i].command // empty")
    SOUT=$(echo "$PHASE_JSON" | jq -r ".eval_suites[$i].output_file // empty")
    [ -z "$SCMD" ] && { warn "$SNAME no command — skipping"; continue; }
    if eval "$SCMD" >/dev/null 2>&1; then :; else fail "$SNAME command failed"; continue; fi
    if [ -n "$SOUT" ] && [ -f "$SOUT" ]; then
      RATE=$(jq -r '.pass_rate // 0' < "$SOUT")
      if awk "BEGIN{ exit !($RATE >= $SMIN) }"; then
        ok "$SNAME pass_rate=$RATE ≥ $SMIN"
      else
        fail "$SNAME pass_rate=$RATE < $SMIN"
      fi
    else
      warn "$SNAME ran but produced no $SOUT — cannot verify pass rate"
    fi
  done
fi

# forbidden_patterns
section "forbidden_patterns (no Potemkin smells)"
FPATTERNS=$(echo "$PHASE_JSON" | jq -r '.forbidden_patterns[]? // empty')
if [ -z "$FPATTERNS" ]; then
  warn "no forbidden_patterns declared"
else
  while IFS= read -r p; do
    [ -z "$p" ] && continue
    HITS=$(grep -rE --include='*.py' --include='*.ts' --include='*.tsx' \
        --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=.next \
        --exclude-dir=dist --exclude-dir=__pycache__ --exclude-dir=audit-log \
        --exclude-dir=planning \
        "$p" . 2>/dev/null || true)
    if [ -n "$HITS" ]; then
      fail "forbidden pattern '$p' found:"
      echo "$HITS" | head -5 | sed 's/^/      /'
    else
      ok "no '$p'"
    fi
  done <<< "$FPATTERNS"
fi

echo ""
if [ $failed -eq 0 ]; then
  printf "${GREEN}${BOLD}✓ phase ${PHASE} mechanical floor GREEN${RESET}\n"
  echo "  (audit (Opus) still required before phase ships)"
  exit 0
else
  printf "${RED}${BOLD}✗ phase ${PHASE} mechanical floor RED${RESET}\n"
  echo "  Do NOT modify the verifier to fix this. Open tickets to fix the underlying capability."
  exit 1
fi
