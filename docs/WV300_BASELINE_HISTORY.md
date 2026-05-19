# WV-300 Baseline History

Generated for the v1.3.2 diagnostic pass.

## Baseline provenance

- **Published v1.1 WV-300 baseline:** 234/300 = **78.0%**.
- **File containing the published 78%:** `outputs/v1_1/webvoyager-300-opus46.json`.
- **Canonical v1.3.1 regression run:** `outputs/v1_3_1/webvoyager-300-regression.json`, 203/300 = **67.67%**.
- **Drop:** -31 passes, -10.33 percentage points.

## v1.1 result files scanned

| File | Total | Passed | Failed | Pass rate | Contains published 78% |
|---|---:|---:|---:|---:|---|
| `outputs/v1_1/failure-taxonomy-gpt55.json` | None | None | None | None% | no |
| `outputs/v1_1/failure-taxonomy.json` | None | None | None | None% | no |
| `outputs/v1_1/webvoyager-100-baseline.json` | 100 | 63 | 37 | 63.0% | no |
| `outputs/v1_1/webvoyager-300-gpt55.json` | 300 | 210 | 90 | 70.0% | no |
| `outputs/v1_1/webvoyager-300-kimi26.json` | 300 | 208 | 92 | 69.33% | no |
| `outputs/v1_1/webvoyager-300-opus46.json` | 300 | 234 | 66 | 78.0% | yes |
| `outputs/v1_1/webvoyager-300-sonnet46.json` | 300 | 223 | 77 | 74.33% | no |
| `outputs/v1_1/webvoyager-gpt55-direct.json` | 100 | 66 | 34 | 66.0% | no |
| `outputs/v1_1/webvoyager-gpt55.json` | 100 | 0 | 100 | 0.0% | no |

## Task-set identity

- v1.1 result IDs: 300
- v1.3.1 result IDs: 300
- Intersection: 300
- Only v1.1: 0
- Only v1.3.1: 0
- Identity score (Jaccard over task IDs): **1.0**
- Same IDs: **True**

Task-content identity is **unknown** from available artifacts. `eval/webvoyager-300/TASKS_LOCK.json` locks the v1.3.1/current tasks hash (`fa0648b4842d8f427c37b5acc6fde86253df334fefa2233dec3acf6efb2bad26`) and notes: “v1.3.1 canonical baseline — v1.1-released tag did not contain tasks.yaml”. Therefore, the diagnostic can prove ID-set identity, but not byte-for-byte task-content identity for v1.1.

## Outcome transition on matched IDs

- v1.1 pass → v1.3.1 pass: 196
- v1.1 pass → v1.3.1 fail: 38
- v1.1 fail → v1.3.1 pass: 7
- v1.1 fail → v1.3.1 fail: 59

## Failure distribution

### v1.1 Opus 4.6

```json
{
  "timeout": 0,
  "wrong_answer": 39,
  "browser_crash": 26,
  "planner_error": 1,
  "other": 0
}
```

### v1.3.1 regression

```json
{
  "timeout": 0,
  "wrong_answer": 44,
  "browser_crash": 51,
  "planner_error": 2,
  "other": 0
}
```

Failure types are mechanically classified from recorded `error`, `final_answer`, step action, and step observation fields. Judge failures with no runtime/planner error are classified as `wrong_answer`.

## Duration comparison

| Run | Avg seconds/task | Median seconds/task | Count with duration |
|---|---:|---:|---:|
| v1.1 Opus 4.6 | 40.017 | 27.565 | 300 |
| v1.3.1 regression | 40.43 | 26.745 | 300 |

## Planner context analysis

The result JSON does **not** record provider token usage or explicit planner token fields, so exact planner input tokens are `unknown`. The diagnostic JSON includes estimated planner input tokens reconstructed from `runner.py` (`SYSTEM_PROMPT` + compact JSON `{task,state,previous_steps[-5:]}`) with a chars/4 token approximation.

- v1.3.1 passed-task median estimated planner input tokens: 3813
- v1.3.1 failed-task median estimated planner input tokens: 3261.0
- Failed/passed median ratio: 0.8552
- Difference: -552.0 estimated tokens

## Hypothesis ranking

1. **runtime regression** — evidence_strength=1.0. Same 300 task IDs; 38 v1.1 passes became v1.3.1 failures while 7 prior failures became passes (net -31 on matched IDs). Pass rate moved -10.33 percentage points.
2. **planner context bloat** — evidence_strength=0.0. Explicit token usage is not recorded. Estimated median v1.3.1 planner input tokens: failed=3261.0, passed=3813, ratio=0.8552; this is an association only, not causal proof.
3. **different task set** — evidence_strength=0.0. Result IDs are identical by set comparison (identity_score=1.0; only_v1_1=0, only_v1_3_1=0). Task content identity cannot be proven from v1.1 because TASKS_LOCK notes the v1.1-released tag did not contain tasks.yaml.

## Diagnostic artifact

Full machine-readable analysis: `outputs/v1_3_2/wv300-diagnostic.json`.
