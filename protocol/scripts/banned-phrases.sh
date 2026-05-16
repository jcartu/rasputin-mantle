#!/usr/bin/env bash
# protocol/scripts/banned-phrases.sh
# Reads stdin, exits 1 if any line in banned-phrases.txt matches.
set -euo pipefail
LIST="$(dirname "${BASH_SOURCE[0]}")/banned-phrases.txt"
[ -f "$LIST" ] || { echo "missing $LIST" >&2; exit 2; }
TMP=$(mktemp); trap 'rm -f "$TMP"' EXIT
cat > "$TMP"
PATTERN=$(grep -v '^#' "$LIST" | grep -v '^$' | tr '\n' '|' | sed 's/|$//')
[ -z "$PATTERN" ] && exit 0
if grep -iE -- "$PATTERN" "$TMP" >/dev/null; then
  echo "BANNED PHRASE DETECTED:" >&2
  grep -iEn -- "$PATTERN" "$TMP" | head -5 >&2
  exit 1
fi
exit 0
