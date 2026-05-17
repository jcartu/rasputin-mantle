from __future__ import annotations

import os

import pytest
from gateway.model_client import anthropic_chat


@pytest.mark.asyncio
async def test_real_anthropic_call_returns_usage() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        pytest.skip("ANTHROPIC_API_KEY is not set")

    result = await anthropic_chat(
        os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet"),
        [{"role": "user", "content": "Reply with exactly: mantle-ok"}],
        16,
        workspace_id="integration-anthropic",
    )

    assert result["content"]
    assert result["input_tokens"] > 0
    assert result["output_tokens"] > 0
    assert result["cost_usd"] >= 0
