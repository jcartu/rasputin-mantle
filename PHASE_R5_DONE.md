# Phase R5: Memory, Wide Research, Scheduler

## Files Created
- `packages/wide-research/wide_research/__init__.py`
- `packages/wide-research/wide_research/dispatcher.py`
- `packages/wide-research/wide_research/merger.py`
- `packages/wide-research/pyproject.toml`
- `packages/scheduler/scheduler/__init__.py`
- `packages/scheduler/scheduler/jobs.py`
- `packages/scheduler/pyproject.toml`
- `apps/gateway/src/gateway/routes/research.py`
- `apps/gateway/src/gateway/memory_client.py`
- `eval/wide-research/runner.py`
- `eval/wide-research/tasks.yaml`
- `tests/integration/test_wide_research_dispatch.py`
- `tests/integration/test_memory_round_trip.py`
- `tests/integration/test_scheduler_job_persistence.py`
- `PHASE_R5_DONE.md`

## Verification Results
- Integration tests: 5/5 passed across the 3 required R5 test files.
- Forbidden pattern verification: no matches in changed R5 Python implementation files for the audit patterns.
- Wide Research route: `/api/research/` now calls `dispatch_research`; it returns 501 when no Brave or Exa key is configured.
- Scheduler persistence: APScheduler Redis jobstore reloads a scheduled job across scheduler shutdown/restart using Redis at `127.0.0.1:6379`.
- Memory: gateway uses `MemoryClient`, which honestly falls back to an in-process dict when `RASPUTIN_MEMORY_URL` is unset or unreachable.

## Eval Status
- Wide Research eval: harness and 24 tasks added; skipped honestly when `BRAVE_SEARCH_API_KEY` and `EXA_API_KEY` are unset.
- LoCoMo eval: skipped; `rasputin-memory` submodule/API is not locally available as an importable service in this checkout.

## Honest Gaps
- The scheduler helper is implemented against the installed APScheduler 3.x RedisJobStore API while package metadata allows the current Redis-backed APScheduler line.
- Wide Research performs parallel sandbox creation and real web-search calls, but result synthesis is markdown merge/ranking rather than model-generated analysis.
- Memory fallback is process-local and non-persistent by design; production persistence requires the external rasputin-memory service.
