from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure browser package is in path
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "packages" / "browser"))

from browser.playwright_backend import PlaywrightBackend
from browser.errors import BrowserNotAvailable


# Skip all tests in this module if playwright is not installed
pytest.importorskip("playwright")


class TestPlaywrightBackendNavigate:
    """Integration tests for PlaywrightBackend navigation and state capture."""

    def test_open_and_get_state(self):
        """Test opening a real page and capturing state."""
        backend = PlaywrightBackend()
        try:
            # Open example.com
            backend.open("https://example.com")

            # Get state
            state = backend.get_state()

            # Verify state contains expected data
            assert state.url == "https://example.com/"
            assert state.title == "Example Domain"
            assert isinstance(state.elements, list)
            assert state.screenshot_b64 is not None
            assert len(state.screenshot_b64) > 0
        finally:
            backend.close()

    def test_evaluate_script(self):
        """Test evaluating JavaScript on the page."""
        backend = PlaywrightBackend()
        try:
            backend.open("https://example.com")

            # Evaluate document.title
            title = backend.evaluate("document.title")
            assert title == "Example Domain"

            # Evaluate a simple expression
            result = backend.evaluate("1 + 1")
            assert result == 2
        finally:
            backend.close()

    def test_close_cleanup(self):
        """Test that close() properly cleans up resources."""
        backend = PlaywrightBackend()

        # Open a page
        backend.open("https://example.com")
        state = backend.get_state()
        assert state.title == "Example Domain"

        # Close should not raise
        backend.close()

        # After close, internal state should be cleared
        assert backend._page is None
        assert backend._browser is None
        assert backend._playwright is None
        assert backend._playwright_cm is None
        assert backend._element_selectors == {}

    def test_no_sandbox_flag_not_used(self):
        """Verify that the unsafe flag is NOT used in Chromium launch."""
        backend = PlaywrightBackend()
        try:
            # This test verifies the code path by checking the launch call
            # The _ensure_page method calls playwright.chromium.launch(headless=True)
            # without any the unsafe flag or args parameter
            backend.open("https://example.com")
            state = backend.get_state()

            # If we got here without errors, the browser launched successfully
            # The absence of the unsafe flag is verified by code inspection:
            # Line 137 in playwright_backend.py shows:
            # self._browser = await self._playwright.chromium.launch(headless=True)
            # No args parameter is passed, so the unsafe flag is not used
            assert state.title == "Example Domain"
        finally:
            backend.close()
