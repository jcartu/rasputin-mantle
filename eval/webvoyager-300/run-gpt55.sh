#!/usr/bin/env bash
set -euo pipefail
cd /home/josh/dev/rasputin-mantle
export PYTHONPATH="packages/browser:packages/sandbox:packages/wide-research:packages/shared:packages/skills:apps/gateway/src"
export ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}"
export OPENAI_API_KEY="${OPENAI_API_KEY}"
exec python3 -u eval/webvoyager-100/direct_runner.py \
  --tasks eval/webvoyager-300/tasks.yaml \
  --output outputs/v1_1/webvoyager-300-gpt55.json \
  --concurrency 2 \
  --traces --traces-dir outputs/v1_1/traces-wv300-gpt55
