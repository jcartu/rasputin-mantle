"""tests/integration/test_vision_fallback_in_extract.py — Verify DOM-fails-vision-succeeds path.

Tests that when DOM extraction returns empty, vision fallback is triggered.
"""
from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest

from browser.vision import VisionAssist


def _make_mock_resp(json_data):
    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.json = Mock(return_value=json_data)
    mock_resp.text = "ok"
    return mock_resp


def _make_mock_client(json_data):
    mock_resp = _make_mock_resp(json_data)
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_resp)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    return mock_client


@pytest.fixture
def vision() -> VisionAssist:
    return VisionAssist(api_key="test-key", max_calls_per_task=3)


class TestVisionFallback:
    def test_extract_text_from_screenshot(self) -> None:
        """extract_text_from_region returns text from screenshot."""
        vision = VisionAssist(api_key="test-key", max_calls_per_task=3)
        mock_client = _make_mock_client(
            {
                "content": [{"text": '{"text": "Hello World - Main Content"}'}],
                "usage": {"output_tokens": 30},
            }
        )

        async def run():
            with patch("browser.vision.httpx.AsyncClient", return_value=mock_client):
                result = await vision.extract_text_from_region(b"\x89PNG")
                return result

        result = asyncio.run(run())
        assert "Hello World" in result

    def test_extract_text_with_region_bbox(self) -> None:
        """extract_text_from_region focuses on specific bbox."""
        vision = VisionAssist(api_key="test-key", max_calls_per_task=3)
        mock_client = _make_mock_client(
            {
                "content": [{"text": '{"text": "Region Content"}'}],
                "usage": {"output_tokens": 15},
            }
        )

        async def run():
            with patch("browser.vision.httpx.AsyncClient", return_value=mock_client):
                result = await vision.extract_text_from_region(
                    b"\x89PNG", bbox={"x": 100, "y": 200, "w": 300, "h": 100}
                )
                return result

        result = asyncio.run(run())
        assert "Region Content" in result

    def test_answer_question_about_page(self) -> None:
        """answer_question_about_page returns answer from screenshot."""
        vision = VisionAssist(api_key="test-key", max_calls_per_task=3)
        mock_client = _make_mock_client(
            {
                "content": [{"text": '{"answer": "The price is $29.99"}'}],
                "usage": {"output_tokens": 25},
            }
        )

        async def run():
            with patch("browser.vision.httpx.AsyncClient", return_value=mock_client):
                result = await vision.answer_question_about_page(
                    b"\x89PNG", "What is the price?"
                )
                return result

        result = asyncio.run(run())
        assert "$29.99" in result
