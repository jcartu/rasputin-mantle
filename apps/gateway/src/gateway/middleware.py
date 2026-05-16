from __future__ import annotations

import json
import re
from dataclasses import dataclass

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from gateway.config import settings


@dataclass(frozen=True)
class CostIncrement:
    tokens: int = 0
    dollars: float = 0.0


class CostCeilingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app) -> None:  # type: ignore[no-untyped-def]
        super().__init__(app)
        self._costs: dict[str, CostIncrement] = {}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        session_id = _session_id_from_request(request)
        increment = _cost_increment_from_request(request)
        if session_id and increment:
            current = self._costs.get(session_id, CostIncrement())
            updated = CostIncrement(
                tokens=current.tokens + increment.tokens,
                dollars=current.dollars + increment.dollars,
            )
            if updated.tokens > settings.max_cost_tokens or updated.dollars > settings.max_cost_dollars:
                return JSONResponse(
                    {
                        "error": "cost_ceiling_exceeded",
                        "message": "Session cost ceiling exceeded",
                        "session_id": session_id,
                        "cost_tokens": updated.tokens,
                        "cost_dollars": updated.dollars,
                        "max_cost_tokens": settings.max_cost_tokens,
                        "max_cost_dollars": settings.max_cost_dollars,
                    },
                    status_code=402,
                )
            self._costs[session_id] = updated
        return await call_next(request)


def _session_id_from_request(request: Request) -> str | None:
    header_session_id = request.headers.get("x-session-id")
    if header_session_id:
        return header_session_id
    match = re.search(r"/api/sessions/([^/]+)", request.url.path)
    if match:
        return match.group(1)
    return None


def _cost_increment_from_request(request: Request) -> CostIncrement | None:
    cost_header = request.headers.get("x-session-cost")
    token_header = request.headers.get("x-session-tokens")
    dollar_header = request.headers.get("x-session-dollars")

    if token_header or dollar_header:
        return CostIncrement(tokens=_parse_int(token_header), dollars=_parse_float(dollar_header))
    if not cost_header:
        return None

    stripped = cost_header.strip()
    if not stripped:
        return None
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        parsed = None

    if isinstance(parsed, dict):
        return CostIncrement(
            tokens=_parse_int(parsed.get("tokens")),
            dollars=_parse_float(parsed.get("dollars")),
        )
    if "," in stripped or "=" in stripped:
        parts: dict[str, str] = {}
        for item in stripped.split(","):
            key, separator, value = item.partition("=")
            if separator:
                parts[key.strip()] = value.strip()
        return CostIncrement(tokens=_parse_int(parts.get("tokens")), dollars=_parse_float(parts.get("dollars")))
    return CostIncrement(dollars=_parse_float(stripped))


def _parse_int(value: object | None) -> int:
    if value is None or value == "":
        return 0
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _parse_float(value: object | None) -> float:
    if value is None or value == "":
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


cost_ceiling_middleware = CostCeilingMiddleware
