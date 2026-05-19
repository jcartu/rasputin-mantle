from __future__ import annotations

import json

import httpx
import pytest

from gateway.model_client import ModelCallError, anthropic_chat, vllm_chat


class HandlerTransport(httpx.AsyncBaseTransport):
    def __init__(self, handler):
        self._handler = handler

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        response = await self._handler(request)
        response.request = request
        return response


@pytest.mark.asyncio
async def test_anthropic_chat_posts_expected_request_and_returns_uniform_result() -> None:
    captured: dict[str, object] = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["headers"] = dict(request.headers)
        captured["body"] = json.loads(request.content)
        return httpx.Response(
            200,
            json={
                "model": "claude-3-5-sonnet",
                "content": [{"type": "text", "text": "hello"}],
                "usage": {"input_tokens": 100, "output_tokens": 50},
            },
        )

    result = await anthropic_chat(
        "claude-3-5-sonnet",
        [{"role": "user", "content": "hi"}],
        64,
        workspace_id="ws-1",
        api_key="test-key",
        transport=HandlerTransport(handler),
    )

    assert captured["url"] == "https://api.anthropic.com/v1/messages"
    headers = captured["headers"]
    assert isinstance(headers, dict)
    assert headers["x-api-key"] == "test-key"
    assert headers["anthropic-version"] == "2023-06-01"
    assert captured["body"] == {
        "model": "claude-3-5-sonnet",
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 64,
    }
    assert result["model"] == "claude-3-5-sonnet"
    assert result["content"] == "hello"
    assert result["input_tokens"] == 100
    assert result["output_tokens"] == 50
    assert result["cost_usd"] == pytest.approx(0.00105)
    assert isinstance(result["latency_ms"], int)


@pytest.mark.asyncio
async def test_anthropic_chat_raises_model_call_error_on_http_error() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"error": "bad key"})

    with pytest.raises(ModelCallError) as exc_info:
        await anthropic_chat(
            "claude-3-5-sonnet",
            [{"role": "user", "content": "hi"}],
            64,
            api_key="bad-key",
            transport=HandlerTransport(handler),
        )

    assert exc_info.value.provider == "anthropic"
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_anthropic_chat_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    with pytest.raises(ModelCallError, match="ANTHROPIC_API_KEY"):
        await anthropic_chat("claude-3-5-sonnet", [{"role": "user", "content": "hi"}], 64)


@pytest.mark.asyncio
async def test_vllm_chat_posts_expected_request_and_returns_uniform_result() -> None:
    captured: dict[str, object] = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["headers"] = dict(request.headers)
        captured["body"] = json.loads(request.content)
        return httpx.Response(
            200,
            json={
                "model": "qwen3.6-27b",
                "choices": [{"message": {"content": "local hello"}}],
                "usage": {"prompt_tokens": 11, "completion_tokens": 7},
            },
        )

    result = await vllm_chat(
        "qwen3.6-27b",
        [{"role": "user", "content": "hi"}],
        64,
        base_url="http://vllm.test",
        api_key="dummy",
        transport=HandlerTransport(handler),
    )

    assert captured["url"] == "http://vllm.test/v1/chat/completions"
    headers = captured["headers"]
    assert isinstance(headers, dict)
    assert headers["authorization"] == "Bearer dummy"
    assert result == {
        "model": "qwen3.6-27b",
        "content": "local hello",
        "input_tokens": 11,
        "output_tokens": 7,
        "cost_usd": 0.0,
        "latency_ms": result["latency_ms"],
    }


@pytest.mark.asyncio
async def test_vllm_chat_omits_authorization_when_key_is_empty() -> None:
    captured: dict[str, str] = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured.update(dict(request.headers))
        return httpx.Response(
            200,
            json={
                "model": "qwen3.6-27b",
                "choices": [{"message": {"content": "ok"}}],
                "usage": {"prompt_tokens": 1, "completion_tokens": 1},
            },
        )

    await vllm_chat(
        "qwen3.6-27b",
        [{"role": "user", "content": "hi"}],
        64,
        base_url="http://vllm.test",
        api_key="",
        transport=HandlerTransport(handler),
    )

    assert "authorization" not in captured


@pytest.mark.asyncio
async def test_vllm_chat_raises_model_call_error_on_http_error() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="boom")

    with pytest.raises(ModelCallError) as exc_info:
        await vllm_chat(
            "qwen3.6-27b",
            [{"role": "user", "content": "hi"}],
            64,
            base_url="http://vllm.test",
            transport=HandlerTransport(handler),
        )

    assert exc_info.value.provider == "vllm"
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_model_client_logs_structured_json(caplog: pytest.LogCaptureFixture) -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "model": "qwen3.6-27b",
                "choices": [{"message": {"content": "ok"}}],
                "usage": {"prompt_tokens": 3, "completion_tokens": 4},
            },
        )

    caplog.set_level("INFO", logger="gateway.model_client")
    await vllm_chat(
        "qwen3.6-27b",
        [{"role": "user", "content": "hi"}],
        64,
        workspace_id="ws-log",
        base_url="http://vllm.test",
        transport=HandlerTransport(handler),
    )

    record = json.loads(caplog.records[-1].message)
    assert record["workspace"] == "ws-log"
    assert record["model"] == "qwen3.6-27b"
    assert record["tokens_in"] == 3
    assert record["tokens_out"] == 4
    assert record["status"] == "ok"
