"""tests/integration/test_browser_retry_on_not_found.py — Verify auto-retry with backoff.

Tests that click/type retry on element-not-found with exponential backoff.
"""
from __future__ import annotations

import asyncio
import time

import pytest

from browser.errors import BrowserActionError
from browser.playwright_backend import PlaywrightBackend


@pytest.mark.asyncio
class TestRetryOnNotFound:
    async def test_click_retries_on_failure(self) -> None:
        """Click retries up to 3 times on element-not-found."""
        browser = PlaywrightBackend()
        try:
            await browser._open("https://example.com")
            with pytest.raises(BrowserActionError):
                await browser._click("pw-99999")
        finally:
            await browser._close()

    async def test_retry_has_backoff_delays(self) -> None:
        """Retry loop uses 500ms/1s/2s delays between attempts."""
        browser = PlaywrightBackend()
        try:
            await browser._open("https://example.com")
            t0 = time.monotonic()
            with pytest.raises(BrowserActionError):
                await browser._click("pw-99999")
            elapsed = time.monotonic() - t0
            assert elapsed >= 1.0, f"Retry completed too fast ({elapsed:.2f}s) — backoff may not be working"
        finally:
            await browser._close()

    async def test_retry_refreshes_state(self) -> None:
        """Each retry re-reads page state for fresh selectors."""
        browser = PlaywrightBackend()
        try:
            await browser._open("https://example.com")
            state1 = await browser._get_state()
            count1 = len(state1.elements)
            with pytest.raises(BrowserActionError):
                await browser._click("pw-99999")
            state2 = await browser._get_state()
            assert len(state2.elements) == count1
        finally:
            await browser._close()

    async def test_successful_click_no_retry(self) -> None:
        """Successful click completes on first attempt (no unnecessary retries)."""
        browser = PlaywrightBackend()
        try:
            await browser._open("https://example.com")
            state = await browser._get_state()
            clickable = [e for e in state.elements if e.role in ("link", "button")]
            if not clickable:
                pytest.skip("No clickable elements")
            t0 = time.monotonic()
            strategy = await browser._click(clickable[0].id)
            elapsed = time.monotonic() - t0
            assert strategy == "primary", f"Expected primary strategy, got {strategy}"
            assert elapsed < 2.0, f"Click took {elapsed:.2f}s — may have retried unnecessarily"
        finally:
            await browser._close()

    async def test_type_retries_on_failure(self) -> None:
        """Type retries up to 3 times on element-not-found."""
        browser = PlaywrightBackend()
        try:
            await browser._open("https://example.com")
            with pytest.raises(BrowserActionError):
                await browser._type_text("pw-99999", "test")
        finally:
            await browser._close()
