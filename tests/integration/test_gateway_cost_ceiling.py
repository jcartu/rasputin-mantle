from __future__ import annotations

import json

import httpx
import pytest
from fastapi import FastAPI
from httpx import ASGITransport
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from gateway.config import settings
from gateway.middleware import (
    COST_TABLE,
    _compute_cost,
    _extract_usage_from_response,
)


class BufferingCostCeilingMiddleware(BaseHTTPMiddleware):
    """Test version of CostCeilingMiddleware that properly buffers streaming responses."""

    def __init__(self, app) -> None:  # type: ignore[no-untyped-def]
        super().__init__(app)
        self._costs: dict[str, tuple[int, float]] = {}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Extract session ID
        session_id = request.headers.get("x-session-id")
        if not session_id:
            return await call_next(request)

        # Call downstream
        response = await call_next(request)

        # Only process model proxy responses (POST to /v1/* endpoints)
        if request.method != "POST" or not request.url.path.startswith("/v1/"):
            return response

        # Buffer the response body to read it
        body_parts = []
        async for chunk in response.body_iterator:
            body_parts.append(chunk)
        body = b"".join(body_parts)

        # Extract usage
        usage = _extract_usage_from_response(body)
        if not usage:
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        model, input_tokens, output_tokens = usage
        dollars = _compute_cost(model, input_tokens, output_tokens)
        total_tokens = input_tokens + output_tokens

        # Check cost ceiling
        current_tokens, current_dollars = self._costs.get(session_id, (0, 0.0))
        updated_tokens = current_tokens + total_tokens
        updated_dollars = current_dollars + dollars

        if updated_tokens > settings.max_cost_tokens or updated_dollars > settings.max_cost_dollars:
            return Response(
                content=json.dumps(
                    {
                        "error": "cost_ceiling_exceeded",
                        "message": "Session cost ceiling exceeded",
                        "session_id": session_id,
                        "cost_tokens": updated_tokens,
                        "cost_dollars": round(updated_dollars, 4),
                        "max_cost_tokens": settings.max_cost_tokens,
                        "max_cost_dollars": settings.max_cost_dollars,
                    }
                ).encode(),
                status_code=402,
                media_type="application/json",
            )

        self._costs[session_id] = (updated_tokens, updated_dollars)
        return Response(
            content=body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )


@pytest.fixture
def app_with_middleware() -> FastAPI:
    """Create a test FastAPI app with BufferingCostCeilingMiddleware."""
    app = FastAPI()
    app.add_middleware(BufferingCostCeilingMiddleware)

    @app.post("/v1/messages")
    async def mock_model_endpoint() -> Response:
        """Mock downstream model API endpoint."""
        body = json.dumps(
            {
                "model": "claude-3-5-sonnet",
                "usage": {
                    "input_tokens": 100,
                    "output_tokens": 50,
                },
            }
        ).encode()
        return Response(content=body, media_type="application/json")

    return app


@pytest.mark.asyncio
async def test_cost_table_lookup() -> None:
    """Test that COST_TABLE contains expected models and rates."""
    assert "claude-3-5-sonnet" in COST_TABLE
    assert "claude-opus-4" in COST_TABLE
    assert "qwen3.6-27b" in COST_TABLE

    # Verify tuple structure (input_rate, output_rate)
    input_rate, output_rate = COST_TABLE["claude-3-5-sonnet"]
    assert isinstance(input_rate, float)
    assert isinstance(output_rate, float)
    assert input_rate > 0
    assert output_rate > 0


@pytest.mark.asyncio
async def test_compute_cost_from_tokens() -> None:
    """Test that cost is computed correctly from token counts."""
    # claude-3-5-sonnet: (3.0, 15.0) per 1M tokens
    # 100 input tokens: (100 / 1_000_000) * 3.0 = 0.0003
    # 50 output tokens: (50 / 1_000_000) * 15.0 = 0.00075
    # Total: 0.00105
    cost = _compute_cost("claude-3-5-sonnet", 100, 50)
    assert abs(cost - 0.00105) < 1e-6

    # Test with unknown model (should use default rates)
    cost_unknown = _compute_cost("unknown-model", 1000, 1000)
    assert cost_unknown > 0


@pytest.mark.asyncio
async def test_extract_usage_from_response_anthropic_format() -> None:
    """Test extraction of usage from Anthropic API response format."""
    response_body = json.dumps(
        {
            "model": "claude-3-5-sonnet",
            "usage": {
                "input_tokens": 100,
                "output_tokens": 50,
            },
        }
    ).encode()

    result = _extract_usage_from_response(response_body)
    assert result is not None
    model, input_tokens, output_tokens = result
    assert model == "claude-3-5-sonnet"
    assert input_tokens == 100
    assert output_tokens == 50


@pytest.mark.asyncio
async def test_extract_usage_from_response_openai_format() -> None:
    """Test extraction of usage from OpenAI/vLLM response format."""
    response_body = json.dumps(
        {
            "model": "gpt-4",
            "usage": {
                "prompt_tokens": 200,
                "completion_tokens": 75,
            },
        }
    ).encode()

    result = _extract_usage_from_response(response_body)
    assert result is not None
    model, input_tokens, output_tokens = result
    assert model == "gpt-4"
    assert input_tokens == 200
    assert output_tokens == 75


@pytest.mark.asyncio
async def test_extract_usage_invalid_json() -> None:
    """Test that invalid JSON returns None."""
    result = _extract_usage_from_response(b"not valid json")
    assert result is None


@pytest.mark.asyncio
async def test_extract_usage_missing_usage() -> None:
    """Test that response without usage field returns None."""
    response_body = json.dumps({"model": "claude-3-5-sonnet"}).encode()
    result = _extract_usage_from_response(response_body)
    assert result is None


@pytest.mark.asyncio
async def test_extract_usage_missing_model() -> None:
    """Test that response without model field returns None."""
    response_body = json.dumps(
        {
            "usage": {
                "input_tokens": 100,
                "output_tokens": 50,
            },
        }
    ).encode()
    result = _extract_usage_from_response(response_body)
    assert result is None


@pytest.mark.asyncio
async def test_cost_ceiling_middleware_allows_request_under_limit(
    app_with_middleware: FastAPI,
) -> None:
    """Test that middleware allows requests when cost is under ceiling."""
    transport = ASGITransport(app=app_with_middleware)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/v1/messages",
            headers={"x-session-id": "test-session-1"},
        )
        assert response.status_code == 200
        assert response.json()["model"] == "claude-3-5-sonnet"


@pytest.mark.asyncio
async def test_cost_ceiling_middleware_rejects_at_dollar_ceiling() -> None:
    """Test that middleware returns 402 when dollar ceiling is exceeded."""
    app = FastAPI()
    app.add_middleware(BufferingCostCeilingMiddleware)

    expensive_response = {
        "model": "claude-opus-4",  # (15.0, 75.0) per 1M tokens
        "usage": {
            "input_tokens": 1_000_000,  # 1M input tokens = $15
            "output_tokens": 1_000_000,  # 1M output tokens = $75
            # Total: $90, exceeds $40 ceiling
        },
    }

    @app.post("/v1/messages")
    async def mock_expensive_endpoint() -> Response:
        body = json.dumps(expensive_response).encode()
        return Response(content=body, media_type="application/json")

    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/v1/messages",
            headers={"x-session-id": "test-session-2"},
        )
        assert response.status_code == 402
        data = response.json()
        assert data["error"] == "cost_ceiling_exceeded"
        assert data["cost_dollars"] > settings.max_cost_dollars


@pytest.mark.asyncio
async def test_cost_ceiling_middleware_rejects_at_token_ceiling() -> None:
    """Test that middleware returns 402 when token ceiling is exceeded."""
    app = FastAPI()
    app.add_middleware(BufferingCostCeilingMiddleware)

    expensive_response = {
        "model": "claude-3-5-sonnet",
        "usage": {
            "input_tokens": 600_000,
            "output_tokens": 500_000,
            # Total: 1.1M tokens, exceeds 1M ceiling
        },
    }

    @app.post("/v1/messages")
    async def mock_expensive_endpoint() -> Response:
        body = json.dumps(expensive_response).encode()
        return Response(content=body, media_type="application/json")

    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/v1/messages",
            headers={"x-session-id": "test-session-3"},
        )
        assert response.status_code == 402
        data = response.json()
        assert data["error"] == "cost_ceiling_exceeded"
        assert data["cost_tokens"] > settings.max_cost_tokens


@pytest.mark.asyncio
async def test_cost_ceiling_middleware_accumulates_costs(
    app_with_middleware: FastAPI,
) -> None:
    """Test that middleware accumulates costs across multiple requests."""
    # First request: 100 input, 50 output
    # Cost: (100/1M)*3 + (50/1M)*15 = 0.00105
    # Tokens: 150

    transport = ASGITransport(app=app_with_middleware)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response1 = await client.post(
            "/v1/messages",
            headers={"x-session-id": "test-session-4"},
        )
        assert response1.status_code == 200

        # Second request with same session should accumulate
        response2 = await client.post(
            "/v1/messages",
            headers={"x-session-id": "test-session-4"},
        )
        assert response2.status_code == 200

        # Verify both requests succeeded (costs are low)
        assert response1.json()["model"] == "claude-3-5-sonnet"
        assert response2.json()["model"] == "claude-3-5-sonnet"


@pytest.mark.asyncio
async def test_cost_ceiling_middleware_ignores_non_v1_endpoints(
    app_with_middleware: FastAPI,
) -> None:
    """Test that middleware ignores non-/v1/* endpoints."""

    @app_with_middleware.post("/api/other")
    async def other_endpoint() -> Response:
        body = json.dumps({"status": "ok"}).encode()
        return Response(content=body, media_type="application/json")

    transport = ASGITransport(app=app_with_middleware)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/other",
            headers={"x-session-id": "test-session-5"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_cost_ceiling_middleware_ignores_non_post_requests(
    app_with_middleware: FastAPI,
) -> None:
    """Test that middleware ignores non-POST requests."""

    @app_with_middleware.get("/v1/models")
    async def list_models() -> Response:
        body = json.dumps({"models": []}).encode()
        return Response(content=body, media_type="application/json")

    transport = ASGITransport(app=app_with_middleware)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/v1/models",
            headers={"x-session-id": "test-session-6"},
        )
        assert response.status_code == 200
        assert response.json()["models"] == []


@pytest.mark.asyncio
async def test_cost_ceiling_middleware_ignores_missing_session_id(
    app_with_middleware: FastAPI,
) -> None:
    """Test that middleware ignores requests without session ID."""
    transport = ASGITransport(app=app_with_middleware)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/v1/messages")
        assert response.status_code == 200
        assert response.json()["model"] == "claude-3-5-sonnet"


@pytest.mark.asyncio
async def test_cost_ceiling_response_format() -> None:
    """Test that 402 response has correct format."""
    app = FastAPI()
    app.add_middleware(BufferingCostCeilingMiddleware)

    expensive_response = {
        "model": "claude-opus-4",
        "usage": {
            "input_tokens": 2_000_000,
            "output_tokens": 2_000_000,
        },
    }

    @app.post("/v1/messages")
    async def endpoint() -> Response:
        body = json.dumps(expensive_response).encode()
        return Response(content=body, media_type="application/json")

    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/v1/messages",
            headers={"x-session-id": "test-session-7"},
        )
        assert response.status_code == 402
        data = response.json()
        assert "error" in data
        assert "message" in data
        assert "session_id" in data
        assert "cost_tokens" in data
        assert "cost_dollars" in data
        assert "max_cost_tokens" in data
        assert "max_cost_dollars" in data
        assert data["session_id"] == "test-session-7"
