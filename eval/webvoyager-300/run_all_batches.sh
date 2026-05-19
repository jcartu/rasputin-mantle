#!/usr/bin/env bash
set -u -o pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

OUTPUT="outputs/v1_3_1/webvoyager-300-regression.json"
OUTPUT_DIR="$(dirname "$OUTPUT")"
FAILURE_LOG="$OUTPUT_DIR/webvoyager-300-regression.failures.log"
CONCURRENCY="${CONCURRENCY:-3}"

mkdir -p "$OUTPUT_DIR"
rm -f "$OUTPUT_DIR/webvoyager-300-regression.batch-"*.json "$OUTPUT" "$FAILURE_LOG"

TRACE_ARGS=()
if [[ "${TRACES:-0}" == "1" ]]; then
  TRACE_ARGS=(--traces --traces-dir "$OUTPUT_DIR/traces-wv300-opus46")
fi

for batch in $(seq 0 9); do
  offset=$((batch * 30))
  batch_number=$((batch + 1))
  echo "==> Running WV-300 batch ${batch_number}/10 (offset=${offset}, size=30)"

  if timeout 30m python3 -u eval/webvoyager-300/runner.py \
    --tasks eval/webvoyager-300/tasks.yaml \
    --planner opus-4-6 \
    --output "$OUTPUT" \
    --concurrency "$CONCURRENCY" \
    --batch-size 30 \
    --batch-offset "$offset" \
    --batch-cooldown 0 \
    "${TRACE_ARGS[@]}"; then
    echo "==> Batch ${batch_number}/10 completed"
  else
    status=$?
    message="batch=${batch_number} offset=${offset} status=${status}"
    echo "WARN: ${message}" | tee -a "$FAILURE_LOG"
  fi

  if [[ "$batch" -lt 9 ]]; then
    echo "==> Cooling down for 30s"
    sleep 30
  fi
done

python3 - <<'PY'
from __future__ import annotations

import glob
import json
import time
from pathlib import Path

output = Path("outputs/v1_3_1/webvoyager-300-regression.json")
failure_log = Path("outputs/v1_3_1/webvoyager-300-regression.failures.log")
batch_files = sorted(glob.glob(str(output.with_name(f"{output.stem}.batch-*.json"))))

results: list[dict] = []
for batch_file in batch_files:
    try:
        data = json.loads(Path(batch_file).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"WARN: skipping unreadable batch result {batch_file}: {exc}")
        continue
    results.extend(result for result in data.get("results", []) if isinstance(result, dict))

results.sort(key=lambda result: str(result.get("id", "")))
passed = sum(1 for result in results if result.get("passed"))
total = len(results)
batch_failures = failure_log.read_text().splitlines() if failure_log.exists() else []

aggregate = {
    "benchmark": "webvoyager-300",
    "planner": "opus-4-6",
    "total": total,
    "passed": passed,
    "failed": total - passed,
    "pass_rate": passed / total if total else 0,
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "batch_files": batch_files,
    "batch_failures": batch_failures,
    "results": results,
}
output.write_text(json.dumps(aggregate, indent=2))
print(f"Aggregate: {passed}/{total} = {aggregate['pass_rate']:.2%}")
print(f"Output: {output}")
if batch_failures:
    print("Batch failures:")
    for failure in batch_failures:
        print(f"  {failure}")
PY
