# Phase R3 — Gateway & Cost Wall

## Files created

- `apps/gateway/src/gateway/model_client.py`
- `apps/gateway/src/gateway/cost_wall.py`
- `apps/gateway/tests/test_model_client.py`
- `apps/gateway/tests/test_cost_wall.py`
- `tests/integration/test_gateway_anthropic_call.py`
- `tests/integration/test_gateway_vllm_call.py`
- `tests/integration/test_cost_wall_enforcement.py`

## Files modified

- `apps/gateway/src/gateway/middleware.py` — wires server-side usage extraction into `CostWall` and returns HTTP 429 on exceeded budget.
- `apps/gateway/src/gateway/app.py` — closes the default cost-wall pool on shutdown.
- `apps/gateway/src/gateway/routes/research.py` — restored deterministic test-compatible research task creation.
- `apps/gateway/tests/test_gateway.py` — replaced client-trusted cost-header assertion with an assertion that such headers are ignored.
- `apps/gateway/pyproject.toml` — added `asyncpg` dependency.

## Cost-wall enforcement

`CostWall.check_and_record(workspace_id, model, input_tokens, output_tokens, cost_usd)` creates and writes to:

```sql
gateway_costs(workspace_id TEXT, model TEXT, ts TIMESTAMP, input_tokens INT, output_tokens INT, cost_usd NUMERIC)
```

For each request, the gateway computes cost server-side from model response usage via `middleware._compute_cost`, sums today's UTC spend for that workspace, and raises `CostCeilingExceeded` if the new call would exceed `settings.max_cost_dollars`. `CostCeilingMiddleware` maps that exception to HTTP 429.

## Structured logging

`model_client.py` emits JSON records through Python logging:

```json
{"ts":"...","workspace":"...","model":"...","tokens_in":123,"tokens_out":45,"cost_usd":0.001,"latency_ms":42,"status":"ok"}
```

## Verification status

- LSP diagnostics: clean on changed Python files after final edits.
- Targeted first run: `13 passed, 1 failed`; failure was Postgres reachability gating, fixed by making `CostWall.open()` validate schema/connectivity.
- Full requested run observed before final research-route repair: `46 passed, 1 skipped, 2 failed`; both failures were unrelated research-route test expectations and were repaired afterward.

Honest gap: I did not run a third pytest pass after the research-route repair because the executor status-check cap was reached. In this environment, Postgres on `127.0.0.1:5432` was not reachable, so the real Postgres integration test correctly skipped when gated by service reachability.
