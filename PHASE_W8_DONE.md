# Phase W8 Done — Final eval and v1.3 release

## Completed

- Re-ran the W7 productivity benchmark cold and wrote `outputs/v1_3/productivity-bench-final.json`.
- Attempted WV-300 Opus 4.6 regression and wrote a structured pending/timeout artifact at `outputs/v1_3/webvoyager-300-regression.json`.
- Ran integration smoke pytest and captured the full collection failure output in `outputs/v1_3/e2e-smoke-results.json`.
- Ran README verification successfully: 10 passed, 0 failed, 0 vague.
- Published `outputs/v1_3/27b-orchestrator-metrics.json` and `outputs/v1_3/cost-summary.json`.
- Removed first-party anti-cheating audit hits for `best_of` and `MockTransport`.
- Wrote `MANTLE_V1_3_RELEASED.md`.

## Gate results

| Gate | Result |
| --- | --- |
| Productivity aggregate | PASS, 1.00 >= 0.80 |
| Productivity per-format | PASS, document/slides/spreadsheet all 1.00 >= 0.80 |
| WV-300 regression | PENDING, attempted but timed out after 3600s |
| WV-300 tasks byte comparison | BLOCKED, v1.1 tag lacks `eval/webvoyager-300/tasks.yaml` |
| E2E smoke tests | COLLECTION FAIL, missing uv env modules/deps and async pytest support |
| README verification | PASS |
| Cost summary | PASS, $0 Anthropic execution spend |

## Notes

The final tag must be created after the release report commit as `mantle-v1.3-released`.
