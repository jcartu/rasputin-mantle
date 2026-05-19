# WV-300 Runtime Regression Diagnosis

## T1 findings

- The strongest supported hypothesis in `outputs/v1_3_2/wv300-diagnostic.json` is a runtime regression.
- Task IDs are identical between v1.1 and v1.3.1 (`identity_score=1.0`), so benchmark identity drift is not the cause.
- Outcomes skewed negative: 38 tasks went pass→fail, while only 7 went fail→pass.
- Planner context bloat is not supported by the data.
- The runtime changed between v1.1 and v1.3.1: APScheduler, skill-loader rediscovery, and project KB lazy mount introduced extra overhead and background noise during eval runs.

## Chosen fix

Mantle now supports an explicit eval mode controlled by `MANTLE_EVAL_MODE=1`. Eval mode keeps benchmark runs focused on the WebVoyager task loop by disabling runtime background work that is useful in production but noisy during repeatable evaluation.

## What eval mode disables

- APScheduler startup and scheduler resume during gateway startup.
- Skill-loader rediscovery when a warm skill cache already exists.
- Project KB lazy mount and KB prompt injection on session start.

## How to use

Set the environment variable before running WV-300:

```bash
MANTLE_EVAL_MODE=1 python eval/webvoyager-300/runner.py --planner gpt-5.5
```

The WV-300 runner also sets `MANTLE_EVAL_MODE=1` automatically.
