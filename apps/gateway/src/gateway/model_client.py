from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime, timezone
from typing import Any

import httpx

from gateway.config import settings
from gateway.middleware import _compute_cost

logger = logging.getLogger(__name__)

ANTHROPIC_MESSAGES_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_TIMEOUT = httpx.Timeout(timeout=120.0, connect=10.0, read=120.0, write=30.0, pool=10.0)


class ModelCallError(RuntimeError):
    def __init__(self, provider: str, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.provider = provider
        self.status_code = status_code


async def anthropic_chat(
    model: str,
    messages: list[dict[str, Any]],
    max_tokens: int,
    *,
    workspace_id: str | None = None,
    api_key: str | None = None,
    temperature: float | None = None,
    timeout: httpx.Timeout | float | None = None,
    transport: httpx.AsyncBaseTransport | None = None,
) -> dict[str, Any]:
    key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        raise ModelCallError("anthropic", "ANTHROPIC_API_KEY is not set")

    payload: dict[str, Any] = {"model": model, "messages": messages, "max_tokens": max_tokens}
    if temperature is not None:
        payload["temperature"] = temperature

    headers = {
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    started = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=timeout or DEFAULT_TIMEOUT, transport=transport) as client:
            response = await client.post(ANTHROPIC_MESSAGES_URL, headers=headers, json=payload)
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        latency_ms = _latency_ms(started)
        _log_model_call(workspace_id, model, 0, 0, 0.0, latency_ms, "error")
        raise ModelCallError(
            "anthropic",
            f"Anthropic request failed with HTTP {exc.response.status_code}: {_response_excerpt(exc.response)}",
            status_code=exc.response.status_code,
        ) from exc
    except httpx.HTTPError as exc:
        latency_ms = _latency_ms(started)
        _log_model_call(workspace_id, model, 0, 0, 0.0, latency_ms, "error")
        raise ModelCallError("anthropic", f"Anthropic request failed: {exc}") from exc

    latency_ms = _latency_ms(started)
    try:
        data = response.json()
        content = _anthropic_content(data)
        usage = data.get("usage") or {}
        input_tokens = int(usage.get("input_tokens") or 0)
        output_tokens = int(usage.get("output_tokens") or 0)
    except (KeyError, TypeError, ValueError) as exc:
        _log_model_call(workspace_id, model, 0, 0, 0.0, latency_ms, "error")
        raise ModelCallError("anthropic", "Anthropic response did not contain usable content and usage") from exc

    actual_model = str(data.get("model") or model)
    cost_usd = _compute_cost(actual_model, input_tokens, output_tokens)
    _log_model_call(workspace_id, actual_model, input_tokens, output_tokens, cost_usd, latency_ms, "ok")
    return {
        "model": actual_model,
        "content": content,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": cost_usd,
        "latency_ms": latency_ms,
    }


async def vllm_chat(
    model: str,
    messages: list[dict[str, Any]],
    max_tokens: int,
    *,
    workspace_id: str | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
    temperature: float | None = None,
    timeout: httpx.Timeout | float | None = None,
    transport: httpx.AsyncBaseTransport | None = None,
) -> dict[str, Any]:
    resolved_base_url = (base_url or settings.vllm_base_url or os.environ.get("VLLM_BASE_URL", "")).rstrip("/")
    if not resolved_base_url:
        raise ModelCallError("vllm", "VLLM_BASE_URL is not set")

    payload: dict[str, Any] = {"model": model, "messages": messages, "max_tokens": max_tokens}
    if temperature is not None:
        payload["temperature"] = temperature

    headers = {"content-type": "application/json"}
    resolved_api_key = api_key if api_key is not None else settings.vllm_api_key or os.environ.get("VLLM_API_KEY", "")
    if resolved_api_key:
        headers["Authorization"] = f"Bearer {resolved_api_key}"

    started = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=timeout or DEFAULT_TIMEOUT, transport=transport) as client:
            response = await client.post(f"{resolved_base_url}/v1/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        latency_ms = _latency_ms(started)
        _log_model_call(workspace_id, model, 0, 0, 0.0, latency_ms, "error")
        raise ModelCallError(
            "vllm",
            f"vLLM request failed with HTTP {exc.response.status_code}: {_response_excerpt(exc.response)}",
            status_code=exc.response.status_code,
        ) from exc
    except httpx.HTTPError as exc:
        latency_ms = _latency_ms(started)
        _log_model_call(workspace_id, model, 0, 0, 0.0, latency_ms, "error")
        raise ModelCallError("vllm", f"vLLM request failed: {exc}") from exc

    latency_ms = _latency_ms(started)
    try:
        data = response.json()
        content = str(data["choices"][0]["message"]["content"])
        usage = data.get("usage") or {}
        input_tokens = int(usage.get("prompt_tokens") or usage.get("input_tokens") or 0)
        output_tokens = int(usage.get("completion_tokens") or usage.get("output_tokens") or 0)
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        _log_model_call(workspace_id, model, 0, 0, 0.0, latency_ms, "error")
        raise ModelCallError("vllm", "vLLM response did not contain usable content and usage") from exc

    actual_model = str(data.get("model") or model)
    cost_usd = _compute_cost(actual_model, input_tokens, output_tokens)
    _log_model_call(workspace_id, actual_model, input_tokens, output_tokens, cost_usd, latency_ms, "ok")
    return {
        "model": actual_model,
        "content": content,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": cost_usd,
        "latency_ms": latency_ms,
    }

async def openai_chat(
    model: str,
    messages: list[dict[str, Any]],
    max_tokens: int,
    *,
    workspace_id: str | None = None,
    api_key: str | None = None,
    temperature: float | None = None,
    thinking_enabled: bool = False,
    thinking_budget_tokens: int | None = None,
    timeout: httpx.Timeout | float | None = None,
    transport: httpx.AsyncBaseTransport | None = None,
) -> dict[str, Any]:
    resolved_api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
    if not resolved_api_key:
        raise ModelCallError("openai", "OPENAI_API_KEY is not set")

    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
    }
    if temperature is not None:
        payload["temperature"] = temperature
    # Extended thinking (GPT-5.5+ models)
    if thinking_enabled:
        payload["thinking"] = {
            "type": "enabled",
            "budget_tokens": thinking_budget_tokens or 16384,
        }

    headers = {"content-type": "application/json"}
    headers["Authorization"] = f"Bearer {resolved_api_key}"

    started = time.perf_counter()
    try:
        async with httpx.AsyncClient(
            timeout=timeout or DEFAULT_TIMEOUT,
            transport=transport,
        ) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        latency_ms = _latency_ms(started)
        _log_model_call(workspace_id, model, 0, 0, 0.0, latency_ms, "error")
        raise ModelCallError(
            "openai",
            f"OpenAI request failed with HTTP {exc.response.status_code}: {_response_excerpt(exc.response)}",
            status_code=exc.response.status_code,
        ) from exc
    except httpx.HTTPError as exc:
        latency_ms = _latency_ms(started)
        _log_model_call(workspace_id, model, 0, 0, 0.0, latency_ms, "error")
        raise ModelCallError("openai", f"OpenAI request failed: {exc}") from exc

    latency_ms = _latency_ms(started)
    try:
        data = response.json()
        content = str(data["choices"][0]["message"]["content"])
        usage = data.get("usage") or {}
        input_tokens = int(usage.get("prompt_tokens") or usage.get("input_tokens") or 0)
        output_tokens = int(usage.get("completion_tokens") or usage.get("output_tokens") or 0)
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        _log_model_call(workspace_id, model, 0, 0, 0.0, latency_ms, "error")
        raise ModelCallError(
            "openai", "OpenAI response did not contain usable content and usage"
        ) from exc

    actual_model = str(data.get("model") or model)
    cost_usd = _compute_cost(actual_model, input_tokens, output_tokens)
    _log_model_call(workspace_id, actual_model, input_tokens, output_tokens, cost_usd, latency_ms, "ok")
    return {
        "model": actual_model,
        "content": content,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": cost_usd,
        "latency_ms": latency_ms,
    }



def _anthropic_content(data: dict[str, Any]) -> str:
    parts = data["content"]
    if not isinstance(parts, list):
        raise TypeError("content must be a list")
    text_parts: list[str] = []
    for part in parts:
        if isinstance(part, dict) and part.get("type") == "text":
            text_parts.append(str(part.get("text") or ""))
    return "".join(text_parts)


def _latency_ms(started: float) -> int:
    return max(0, round((time.perf_counter() - started) * 1000))


def _response_excerpt(response: httpx.Response) -> str:
    return response.text[:500]


def _log_model_call(
    workspace_id: str | None,
    model: str,
    input_tokens: int,
    output_tokens: int,
    cost_usd: float,
    latency_ms: int,
    status: str,
) -> None:
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "workspace": workspace_id,
        "model": model,
        "tokens_in": input_tokens,
        "tokens_out": output_tokens,
        "cost_usd": cost_usd,
        "latency_ms": latency_ms,
        "status": status,
    }
    logger.info(json.dumps(record, separators=(",", ":")))
