from __future__ import annotations

import os

import httpx
import pytest
from gateway.config import settings
from gateway.model_client import vllm_chat


@pytest.mark.asyncio
async def test_real_vllm_call_returns_usage() -> None:
    base_url = (os.environ.get("VLLM_BASE_URL") or settings.vllm_base_url).rstrip("/")
    if not base_url:
        pytest.skip("VLLM_BASE_URL is not set")
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"{base_url}/v1/models")
            response.raise_for_status()
    except httpx.HTTPError as exc:
        pytest.skip(f"vLLM is not reachable: {exc}")

    result = await vllm_chat(
        os.environ.get("VLLM_MODEL") or settings.vllm_model,
        [{"role": "user", "content": "Reply with exactly: mantle-ok"}],
        16,
        workspace_id="integration-vllm",
        base_url=base_url,
        api_key=os.environ.get("VLLM_API_KEY") or settings.vllm_api_key,
    )

    assert result["content"]
    assert result["input_tokens"] >= 0
    assert result["output_tokens"] >= 0
    assert result["cost_usd"] >= 0
