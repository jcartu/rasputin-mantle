"""tests/integration/test_vision_find_element.py — Verify vision element finding.

Tests VisionAssist.find_element_bbox with mock API responses.
"""
from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest

from browser.vision import VisionAssist, VisionBudgetExceeded


def _make_mock_resp(json_data):
    """Create a proper mock response — .json() must NOT be async."""
    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.json = Mock(return_value=json_data)
    mock_resp.text = "ok"
    return mock_resp


def _make_mock_client(json_data):
    """Create a mock httpx.AsyncClient with proper async context manager."""
    mock_resp = _make_mock_resp(json_data)
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_resp)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    return mock_client


@pytest.fixture
def vision() -> VisionAssist:
    return VisionAssist(api_key="test-key", max_calls_per_task=3)


class TestVisionFindElement:
    def test_find_element_returns_bbox(self) -> None:
        """find_element_bbox returns bounding box dict."""
        vision = VisionAssist(api_key="test-key", max_calls_per_task=3)
        mock_client = _make_mock_client(
            {
                "content": [{"text": '{"x": 100, "y": 200, "w": 150, "h": 40}'}],
                "usage": {"output_tokens": 20},
            }
        )

        async def run():
            with patch("browser.vision.httpx.AsyncClient", return_value=mock_client):
                result = await vision.find_element_bbox(b"\x89PNG", "the login button")
                return result

        result = asyncio.run(run())
        assert result is not None
        assert "x" in result
        assert "y" in result

    def test_find_element_not_found_returns_none(self) -> None:
        """find_element_bbox returns None when element not visible."""
        vision = VisionAssist(api_key="test-key", max_calls_per_task=3)
        mock_client = _make_mock_client(
            {
                "content": [{"text": "null"}],
                "usage": {"output_tokens": 5},
            }
        )

        async def run():
            with patch("browser.vision.httpx.AsyncClient", return_value=mock_client):
                result = await vision.find_element_bbox(b"\x89PNG", "nonexistent element")
                return result

        result = asyncio.run(run())
        assert result is None

    def test_budget_exceeded_raises(self) -> None:
        """4th vision call raises VisionBudgetExceeded."""
        vision = VisionAssist(api_key="test-key", max_calls_per_task=3)
        vision._call_count = 3

        async def run():
            with pytest.raises(VisionBudgetExceeded):
                await vision.find_element_bbox(b"\x89PNG", "anything")

        asyncio.run(run())

    def test_cost_report_tracks_calls(self) -> None:
        """get_cost_report returns telemetry data."""
        vision = VisionAssist(api_key="test-key", max_calls_per_task=3)
        report = vision.get_cost_report()
        assert "total_calls" in report
        assert "total_cost_usd" in report
        assert report["total_calls"] == 0
        assert report["total_cost_usd"] == 0
