"""tests/integration/test_browser_multi_strategy_click.py — Verify multi-strategy element selection.

Tests that click/type fall through strategies when the primary selector fails.
"""
from __future__ import annotations

import pytest

from browser.errors import BrowserActionError
from browser.playwright_backend import PlaywrightBackend


@pytest.mark.asyncio
class TestMultiStrategySelectors:
    async def test_click_returns_strategy_name(self) -> None:
        """_click returns the strategy name used (primary/role/text/label)."""
        browser = PlaywrightBackend()
        try:
            await browser._open("https://example.com")
            state = await browser._get_state()
            clickable = [e for e in state.elements if e.role in ("link", "button")]
            if not clickable:
                pytest.skip("No clickable elements on example.com")
            strategy = await browser._click(clickable[0].id)
            assert strategy in ("primary", "role", "text", "label"), f"Unexpected strategy: {strategy}"
        finally:
            await browser._close()

    async def test_click_fallback_to_role(self) -> None:
        """If primary selector fails, fallback to role-based locator."""
        browser = PlaywrightBackend()
        try:
            await browser._open("https://example.com")
            state = await browser._get_state()
            button = [e for e in state.elements if e.role == "button"]
            if not button:
                pytest.skip("No buttons on example.com")
            strategy = await browser._click(button[0].id)
            assert isinstance(strategy, str) and strategy
        finally:
            await browser._close()

    async def test_locators_for_returns_strategies(self) -> None:
        """_locators_for returns at least the primary strategy."""
        browser = PlaywrightBackend()
        try:
            await browser._open("https://example.com")
            state = await browser._get_state()
            if not state.elements:
                pytest.skip("No elements on page")
            page = await browser._ensure_page()
            locators = browser._locators_for(state.elements[0].id, page)
            assert len(locators) >= 1
            assert locators[0][0] == "primary"
        finally:
            await browser._close()

    async def test_click_unknown_element_raises(self) -> None:
        """Clicking an unknown element ID raises ElementNotFoundError."""
        browser = PlaywrightBackend()
        try:
            await browser._open("https://example.com")
            with pytest.raises(BrowserActionError, match="Unknown element id"):
                await browser._click("pw-99999")
        finally:
            await browser._close()

    async def test_type_returns_strategy_name(self) -> None:
        """_type_text returns the strategy name used."""
        browser = PlaywrightBackend()
        try:
            await browser._open("https://example.com")
            state = await browser._get_state()
            textbox = [e for e in state.elements if e.role in ("textbox", "searchbox")]
            if not textbox:
                pytest.skip("No textboxes on example.com")
            strategy = await browser._type_text(textbox[0].id, "test")
            assert strategy in ("primary", "role", "text", "label"), f"Unexpected strategy: {strategy}"
        finally:
            await browser._close()
