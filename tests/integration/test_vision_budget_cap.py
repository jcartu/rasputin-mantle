"""tests/integration/test_vision_budget_cap.py — Verify 3-call budget enforcement.

Tests that the 4th vision call within a task is rejected.
"""
from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest

from browser.vision import VisionAssist, VisionBudgetExceeded


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
    "content": [{"text": '{"x": 1, "y": 1, "w": 10, "h": 10}'}],
    "usage": {"output_tokens": 10},
}


class TestVisionBudgetCap:
    def test_budget_starts_at_max(self) -> None:
        """New VisionAssist has full budget."""
        vision = VisionAssist(api_key="test-key", max_calls_per_task=3)
        assert vision.remaining_budget == 3
        assert vision.calls_made == 0

    def test_budget_decrements_on_call(self) -> None:
        """Each unique call decrements budget."""
        vision = VisionAssist(api_key="test-key", max_calls_per_task=3)
        mock_client = _make_mock_client(_SUCCESS_JSON)

        async def run():
            with patch("browser.vision.httpx.AsyncClient", return_value=mock_client):
                await vision.find_element_bbox(b"\x89PNG", "element 1")
                assert vision.remaining_budget == 2
                await vision.find_element_bbox(b"\x89PNG", "element 2")
                assert vision.remaining_budget == 1
                await vision.find_element_bbox(b"\x89PNG", "element 3")
                assert vision.remaining_budget == 0

        asyncio.run(run())

    def test_fourth_call_raises_budget_exceeded(self) -> None:
        """4th unique call raises VisionBudgetExceeded."""
        vision = VisionAssist(api_key="test-key", max_calls_per_task=3)
        mock_client = _make_mock_client(_SUCCESS_JSON)

        async def run():
            with patch("browser.vision.httpx.AsyncClient", return_value=mock_client):
                await vision.find_element_bbox(b"\x89PNG", "e1")
                await vision.find_element_bbox(b"\x89PNG", "e2")
                await vision.find_element_bbox(b"\x89PNG", "e3")
                with pytest.raises(VisionBudgetExceeded):
                    await vision.find_element_bbox(b"\x89PNG", "e4")

        asyncio.run(run())

    def test_reset_task_restores_budget(self) -> None:
        """reset_task() restores budget to max."""
        vision = VisionAssist(api_key="test-key", max_calls_per_task=3)
        mock_client = _make_mock_client(_SUCCESS_JSON)

        async def run():
            with patch("browser.vision.httpx.AsyncClient", return_value=mock_client):
                await vision.find_element_bbox(b"\x89PNG", "e1")
                assert vision.remaining_budget == 2
                vision.reset_task()
                assert vision.remaining_budget == 3

        asyncio.run(run())
