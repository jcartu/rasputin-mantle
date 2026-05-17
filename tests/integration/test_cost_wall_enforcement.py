from __future__ import annotations

import json
import uuid

import httpx
import pytest
from fastapi import FastAPI
from gateway.cost_wall import DEFAULT_POSTGRES_DSN, CostWall
from gateway.middleware import CostCeilingMiddleware
from httpx import ASGITransport
from starlette.responses import Response


@pytest.mark.asyncio
async def test_postgres_cost_wall_returns_429_when_budget_exceeded() -> None:
    workspace_id = f"integration-cost-{uuid.uuid4()}"
    wall = CostWall(dsn=DEFAULT_POSTGRES_DSN, max_cost_dollars=0.001)
    try:
        await wall.open()
    except Exception as exc:
        pytest.skip(f"Postgres is not reachable: {exc}")

    app = FastAPI()
    app.add_middleware(CostCeilingMiddleware, cost_wall=wall)

    @app.post("/v1/messages")
    async def expensive_model_response() -> Response:
        return Response(
            content=json.dumps(
                {
                    "model": "claude-3-5-sonnet",
                    "usage": {"input_tokens": 1000, "output_tokens": 1000},
                }
            ),
            media_type="application/json",
        )

    try:
        transport = ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/v1/messages", headers={"x-session-id": workspace_id})
    finally:
        await wall.close()

    assert response.status_code == 429
    body = response.json()
    assert body["error"] == "cost_ceiling_exceeded"
    assert body["session_id"] == workspace_id
    assert body["cost_dollars"] > body["max_cost_dollars"]
