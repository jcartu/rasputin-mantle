from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from gateway.config import settings

logger = logging.getLogger(__name__)

# Server-side cost table: per-model token costs (input, output) in USD per 1M tokens.
COST_TABLE: dict[str, tuple[float, float]] = {
    "claude-opus-4-20250514": (15.0, 75.0),
    "claude-opus-4": (15.0, 75.0),
    "claude-sonnet-4-20250514": (3.0, 15.0),
    "claude-sonnet-4": (3.0, 15.0),
    "claude-3-5-sonnet": (3.0, 15.0),
    "claude-3-opus": (15.0, 75.0),
    "qwen3.6-27b": (0.0, 0.0),
    "Qwen3.6-27B": (0.0, 0.0),
}


@dataclass(frozen=True)
class CostIncrement:
    tokens: int = 0
    dollars: float = 0.0


def _compute_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Compute cost from token counts using server-side COST_TABLE."""
    rates = COST_TABLE.get(model, (5.0, 15.0))
    input_cost = (input_tokens / 1_000_000) * rates[0]
    output_cost = (output_tokens / 1_000_000) * rates[1]
    return input_cost + output_cost


def _extract_usage_from_response(response_body: bytes | None) -> tuple[str, int, int] | None:
    """Extract model, input_tokens, output_tokens from a model API response body.

    Handles both Anthropic and OpenAI/vLLM response formats.
    """
    if not response_body:
        return None
    try:
        data = json.loads(response_body)
    except (json.JSONDecodeError, ValueError):
        return None

    usage = data.get("usage")
    if not isinstance(usage, dict):
        return None

    model = data.get("model", "")
    if not model:
        return None

    # Anthropic format
    input_tokens = usage.get("input_tokens") or usage.get("cache_creation_input_tokens", 0) or 0
    output_tokens = usage.get("output_tokens", 0)

    # OpenAI/vLLM format
    if not input_tokens and not output_tokens:
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)

    if input_tokens or output_tokens:
        return (model, int(input_tokens), int(output_tokens))

    return None


class CostCeilingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app) -> None:  # type: ignore[no-untyped-def]
        super().__init__(app)
        self._costs: dict[str, CostIncrement] = {}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        session_id = _session_id_from_request(request)
        if not session_id:
            return await call_next(request)

        # Call downstream first to get the response with usage data
        response = await call_next(request)

        # Only process model proxy responses (POST to /v1/* endpoints)
        if request.method != "POST" or not request.url.path.startswith("/v1/"):
            return response

        # Compute cost server-side from response body
        body = response.body if hasattr(response, "body") else b""
        usage = _extract_usage_from_response(body)
        if not usage:
            return response

        model, input_tokens, output_tokens = usage
        dollars = _compute_cost(model, input_tokens, output_tokens)
        total_tokens = input_tokens + output_tokens

        # Check cost ceiling server-side
        current = self._costs.get(session_id, CostIncrement())
        updated = CostIncrement(
            tokens=current.tokens + total_tokens,
            dollars=current.dollars + dollars,
        )

        if updated.tokens > settings.max_cost_tokens or updated.dollars > settings.max_cost_dollars:
            logger.warning(
                "Cost ceiling exceeded for session %s: %.2f/%.2f dollars, %d/%d tokens",
                session_id,
                updated.dollars,
                settings.max_cost_dollars,
                updated.tokens,
                settings.max_cost_tokens,
            )
            return JSONResponse(
                {
                    "error": "cost_ceiling_exceeded",
                    "message": "Session cost ceiling exceeded",
                    "session_id": session_id,
                    "cost_tokens": updated.tokens,
                    "cost_dollars": round(updated.dollars, 4),
                    "max_cost_tokens": settings.max_cost_tokens,
                    "max_cost_dollars": settings.max_cost_dollars,
                },
                status_code=402,
            )

        self._costs[session_id] = updated
        return response


def _session_id_from_request(request: Request) -> str | None:
    header_session_id = request.headers.get("x-session-id")
    if header_session_id:
        return header_session_id
    match = re.search(r"/api/sessions/([^/]+)", request.url.path)
    if match:
        return match.group(1)
    return None


cost_ceiling_middleware = CostCeilingMiddleware
