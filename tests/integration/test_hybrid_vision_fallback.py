"""tests/integration/test_hybrid_vision_fallback.py — Verify PlaywrightBackend hybrid DOM→vision wiring.

Tests that when DOM extraction returns empty, vision fallback is triggered
and vision-sourced elements are properly merged into BrowserState.
"""
from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, Mock, patch

from browser.vision import VisionBudgetExceeded


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


class TestHybridFallback:
    """Test PlaywrightBackend._get_state() hybrid DOM→vision fallback."""

    def test_vision_not_called_when_dom_has_elements(self) -> None:
        """When DOM returns elements, vision fallback must NOT be triggered."""
        vision_called = False

        async def run():
            nonlocal vision_called
            with patch("browser.playwright_backend.async_playwright") as mpw:
                mock_pw = AsyncMock()
                mock_browser = AsyncMock()
                mock_page = AsyncMock()

                # DOM returns elements
                mock_page.evaluate = AsyncMock(return_value=[
                    {"id": "pw-0", "role": "button", "text": "Submit", "attributes": {}, "selector": "#submit"},
                ])
                mock_page.screenshot = AsyncMock(return_value=b"\x89PNG")
                mock_page.title = AsyncMock(return_value="Test Page")
                mock_page.url = "https://example.com"

                mock_browser.new_page = AsyncMock(return_value=mock_page)
                mock_pw.chromium.launch = AsyncMock(return_value=mock_browser)
                mock_cm = AsyncMock()
                mock_cm.__aenter__ = AsyncMock(return_value=mock_pw)
                mock_cm.__aexit__ = AsyncMock(return_value=None)
                mpw.return_value = mock_cm

                from browser.playwright_backend import PlaywrightBackend

                pb = PlaywrightBackend(vision_api_key="test-key")
                # Patch vision to detect if it's called
                original_vision = pb._vision
                call_tracker = Mock(wraps=original_vision)
                pb._vision = call_tracker

                state = await pb._get_state()

                # Vision should NOT have been called
                vision_called = call_tracker._call_vision.called
                await pb._close()

                return state

        state = asyncio.run(run())
        assert len(state.elements) == 1
        assert state.elements[0].source == "dom"
        assert vision_called is False

    def test_vision_called_when_dom_empty(self) -> None:
        """When DOM returns empty, vision fallback IS triggered."""
        async def run():
            with patch("browser.playwright_backend.async_playwright") as mpw:
                mock_pw = AsyncMock()
                mock_browser = AsyncMock()
                mock_page = AsyncMock()

                # DOM returns empty
                mock_page.evaluate = AsyncMock(return_value=[])
                mock_page.screenshot = AsyncMock(return_value=b"\x89PNG")
                mock_page.title = AsyncMock(return_value="Test Page")
                mock_page.url = "https://example.com"

                mock_browser.new_page = AsyncMock(return_value=mock_page)
                mock_pw.chromium.launch = AsyncMock(return_value=mock_browser)
                mock_cm = AsyncMock()
                mock_cm.__aenter__ = AsyncMock(return_value=mock_pw)
                mock_cm.__aexit__ = AsyncMock(return_value=None)
                mpw.return_value = mock_cm

                from browser.playwright_backend import PlaywrightBackend

                pb = PlaywrightBackend(vision_api_key="test-key")

                # Patch _call_vision to return vision elements
                vision_result = [
                    {"role": "button", "text": "Login", "x": 100, "y": 200, "w": 80, "h": 30},
                    {"role": "textbox", "text": None, "x": 100, "y": 240, "w": 300, "h": 40},
                ]
                pb._vision._call_vision = AsyncMock(return_value=vision_result)

                state = await pb._get_state()
                await pb._close()

                return state

        state = asyncio.run(run())
        assert len(state.elements) == 2
        assert state.elements[0].source == "vision"
        assert state.elements[0].id == "vision-0"
        assert state.elements[0].role == "button"
        assert state.elements[0].text == "Login"
        assert state.elements[0].bbox == {"x": 100, "y": 200, "w": 80, "h": 30}
        assert state.elements[1].source == "vision"
        assert state.elements[1].id == "vision-1"
        assert state.elements[1].role == "textbox"
        assert state.elements[1].text is None

    def test_vision_budget_exceeded_does_not_crash(self) -> None:
        """When vision budget is exceeded, _get_state returns empty gracefully."""
        async def run():
            with patch("browser.playwright_backend.async_playwright") as mpw:
                mock_pw = AsyncMock()
                mock_browser = AsyncMock()
                mock_page = AsyncMock()

                mock_page.evaluate = AsyncMock(return_value=[])
                mock_page.screenshot = AsyncMock(return_value=b"\x89PNG")
                mock_page.title = AsyncMock(return_value="Test Page")
                mock_page.url = "https://example.com"

                mock_browser.new_page = AsyncMock(return_value=mock_page)
                mock_pw.chromium.launch = AsyncMock(return_value=mock_browser)
                mock_cm = AsyncMock()
                mock_cm.__aenter__ = AsyncMock(return_value=mock_pw)
                mock_cm.__aexit__ = AsyncMock(return_value=None)
                mpw.return_value = mock_cm

                from browser.playwright_backend import PlaywrightBackend

                pb = PlaywrightBackend(vision_api_key="test-key")
                pb._vision._call_vision = AsyncMock(side_effect=VisionBudgetExceeded("budget exceeded"))

                state = await pb._get_state()
                await pb._close()

                return state

        state = asyncio.run(run())
        assert len(state.elements) == 0
        assert state.title == "Test Page"

    def test_vision_failure_does_not_crash(self) -> None:
        """When vision API fails, _get_state returns empty gracefully."""
        async def run():
            with patch("browser.playwright_backend.async_playwright") as mpw:
                mock_pw = AsyncMock()
                mock_browser = AsyncMock()
                mock_page = AsyncMock()

                mock_page.evaluate = AsyncMock(return_value=[])
                mock_page.screenshot = AsyncMock(return_value=b"\x89PNG")
                mock_page.title = AsyncMock(return_value="Test Page")
                mock_page.url = "https://example.com"

                mock_browser.new_page = AsyncMock(return_value=mock_page)
                mock_pw.chromium.launch = AsyncMock(return_value=mock_browser)
                mock_cm = AsyncMock()
                mock_cm.__aenter__ = AsyncMock(return_value=mock_pw)
                mock_cm.__aexit__ = AsyncMock(return_value=None)
                mpw.return_value = mock_cm

                from browser.playwright_backend import PlaywrightBackend

                pb = PlaywrightBackend(vision_api_key="test-key")
                pb._vision._call_vision = AsyncMock(side_effect=Exception("API error"))

                state = await pb._get_state()
                await pb._close()

                return state

        state = asyncio.run(run())
        assert len(state.elements) == 0
        assert state.title == "Test Page"

    def test_vision_disabled_when_no_api_key(self) -> None:
        """When no vision_api_key, _vision is None and fallback is skipped."""
        async def run():
            with patch("browser.playwright_backend.async_playwright") as mpw:
                mock_pw = AsyncMock()
                mock_browser = AsyncMock()
                mock_page = AsyncMock()

                mock_page.evaluate = AsyncMock(return_value=[])
                mock_page.screenshot = AsyncMock(return_value=b"\x89PNG")
                mock_page.title = AsyncMock(return_value="Test Page")
                mock_page.url = "https://example.com"

                mock_browser.new_page = AsyncMock(return_value=mock_page)
                mock_pw.chromium.launch = AsyncMock(return_value=mock_browser)
                mock_cm = AsyncMock()
                mock_cm.__aenter__ = AsyncMock(return_value=mock_pw)
                mock_cm.__aexit__ = AsyncMock(return_value=None)
                mpw.return_value = mock_cm

                from browser.playwright_backend import PlaywrightBackend

                pb = PlaywrightBackend()  # No vision_api_key
                assert pb._vision is None

                state = await pb._get_state()
                await pb._close()

                return state

        state = asyncio.run(run())
        assert len(state.elements) == 0

    def test_vision_returns_non_list_result(self) -> None:
        """When vision returns non-list (raw_text), fallback returns empty."""
        async def run():
            with patch("browser.playwright_backend.async_playwright") as mpw:
                mock_pw = AsyncMock()
                mock_browser = AsyncMock()
                mock_page = AsyncMock()

                mock_page.evaluate = AsyncMock(return_value=[])
                mock_page.screenshot = AsyncMock(return_value=b"\x89PNG")
                mock_page.title = AsyncMock(return_value="Test Page")
                mock_page.url = "https://example.com"

                mock_browser.new_page = AsyncMock(return_value=mock_page)
                mock_pw.chromium.launch = AsyncMock(return_value=mock_browser)
                mock_cm = AsyncMock()
                mock_cm.__aenter__ = AsyncMock(return_value=mock_pw)
                mock_cm.__aexit__ = AsyncMock(return_value=None)
                mpw.return_value = mock_cm

                from browser.playwright_backend import PlaywrightBackend

                pb = PlaywrightBackend(vision_api_key="test-key")
                pb._vision._call_vision = AsyncMock(return_value={"raw_text": "I couldn't parse this"})

                state = await pb._get_state()
                await pb._close()

                return state

        state = asyncio.run(run())
        assert len(state.elements) == 0

    def test_reset_vision_task(self) -> None:
        """reset_vision_task resets call count and cache."""
        from browser.playwright_backend import PlaywrightBackend

        pb = PlaywrightBackend(vision_api_key="test-key")
        pb._vision._call_count = 2
        pb._vision._cache = {"key": "value"}

        pb.reset_vision_task()
        assert pb._vision._call_count == 0
        assert len(pb._vision._cache) == 0

    def test_get_vision_cost_report_enabled(self) -> None:
        """get_vision_cost_report returns telemetry when vision is enabled."""
        from browser.playwright_backend import PlaywrightBackend

        pb = PlaywrightBackend(vision_api_key="test-key")
        report = pb.get_vision_cost_report()
        assert report["enabled"] is True
        assert "total_calls" in report

    def test_get_vision_cost_report_disabled(self) -> None:
        """get_vision_cost_report returns disabled flag when no vision."""
        from browser.playwright_backend import PlaywrightBackend

        pb = PlaywrightBackend()
        report = pb.get_vision_cost_report()
        assert report == {"enabled": False}


class TestFactoryVisionKey:
    """Test factory passes vision_api_key correctly."""

    def test_factory_passes_vision_key_to_playwright(self) -> None:
        """Factory passes vision_api_key to PlaywrightBackend."""
        from browser.factory import create_browser_backend

        with patch("browser.factory.PlaywrightBackend") as MockBackend:
            create_browser_backend(backend="playwright", vision_api_key="my-key")
            MockBackend.assert_called_once_with(vision_api_key="my-key")

    def test_factory_uses_env_key_when_none_provided(self) -> None:
        """Factory falls back to ANTHROPIC_API_KEY env var."""
        from browser.factory import create_browser_backend

        with patch("browser.factory.PlaywrightBackend") as MockBackend:
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "env-key"}):
                create_browser_backend(backend="playwright")
                MockBackend.assert_called_once_with(vision_api_key="env-key")
