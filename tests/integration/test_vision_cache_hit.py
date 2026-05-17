"""tests/integration/test_vision_cache_hit.py — Verify vision result caching.

Tests that repeated calls with same screenshot+prompt return cached results.
"""
from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest

from browser.vision import VisionAssist


def _make_mock_client(json_data):
    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.json = Mock(return_value=json_data)
    mock_resp.text = "ok"
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_resp)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    return mock_client


_SUCCESS_JSON = {
    "content": [{"text": '{"x": 100, "y": 200, "w": 150, "h": 40}'}],
    "usage": {"output_tokens": 20},
}


class TestVisionCache:
    def test_cache_hit_returns_same_result(self) -> None:
        """Second call with same screenshot+prompt returns cached result."""
        vision = VisionAssist(api_key="test-key", max_calls_per_task=3)
        mock_client = _make_mock_client(_SUCCESS_JSON)

        async def run():
            with patch("browser.vision.httpx.AsyncClient", return_value=mock_client):
                result1 = await vision.find_element_bbox(b"\x89PNG", "the button")
                result2 = await vision.find_element_bbox(b"\x89PNG", "the button")
                assert result1 == result2
                # Only 1 unique call made, 1 cache hit
                assert vision.calls_made == 1

        asyncio.run(run())

    def test_cache_miss_on_different_prompt(self) -> None:
        """Different prompt = cache miss = new API call."""
        vision = VisionAssist(api_key="test-key", max_calls_per_task=3)
        mock_client = _make_mock_client(
            {
                "content": [{"text": '{"x": 1, "y": 1, "w": 10, "h": 10}'}],
                "usage": {"output_tokens": 10},
            }
        )

        async def run():
            with patch("browser.vision.httpx.AsyncClient", return_value=mock_client):
                await vision.find_element_bbox(b"\x89PNG", "button A")
                await vision.find_element_bbox(b"\x89PNG", "button B")
                assert vision.calls_made == 2

        asyncio.run(run())

    def test_cache_miss_on_different_screenshot(self) -> None:
        """Different screenshot = cache miss = new API call."""
        vision = VisionAssist(api_key="test-key", max_calls_per_task=3)
        mock_client = _make_mock_client(
            {
                "content": [{"text": '{"x": 1, "y": 1, "w": 10, "h": 10}'}],
                "usage": {"output_tokens": 10},
            }
        )

        async def run():
            with patch("browser.vision.httpx.AsyncClient", return_value=mock_client):
                await vision.find_element_bbox(b"\x89PNG\x01", "the button")
                await vision.find_element_bbox(b"\x89PNG\x02", "the button")
                assert vision.calls_made == 2

        asyncio.run(run())

    def test_cost_report_shows_cache_hits(self) -> None:
        """Cost report tracks cache hits separately."""
        vision = VisionAssist(api_key="test-key", max_calls_per_task=3)
        mock_client = _make_mock_client(
            {
                "content": [{"text": '{"x": 1, "y": 1, "w": 10, "h": 10}'}],
                "usage": {"output_tokens": 10},
            }
        )

        async def run():
            with patch("browser.vision.httpx.AsyncClient", return_value=mock_client):
                await vision.find_element_bbox(b"\x89PNG", "the button")
                await vision.find_element_bbox(b"\x89PNG", "the button")
                report = vision.get_cost_report()
                assert report["total_calls"] == 2
                assert report["cached_hits"] == 1
                assert report["unique_calls"] == 1

        asyncio.run(run())
