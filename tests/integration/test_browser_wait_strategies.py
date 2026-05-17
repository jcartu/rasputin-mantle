"""tests/integration/test_browser_wait_strategies.py — Verify wait strategy hardening.

Tests that PlaywrightBackend waits properly after navigation and before interaction.
"""
from __future__ import annotations

import asyncio
import time

import pytest

from browser.errors import BrowserActionError
from browser.playwright_backend import PlaywrightBackend


@pytest.mark.asyncio
class TestWaitStrategies:
    async def test_networkidle_after_open(self) -> None:
        """After _open(), page should be in networkidle state."""
        browser = PlaywrightBackend()
        try:
            await browser._open("https://example.com")
            state = await browser._get_state()
            assert state.url == "https://example.com/"
            assert state.title == "Example Domain"
        finally:
            await browser._close()

    async def test_wait_for_selector_visible(self) -> None:
        """wait_for_selector returns True for visible elements."""
        browser = PlaywrightBackend()
        try:
            await browser._open("https://example.com")
            result = await browser.wait_for_selector("h1", state="visible", timeout=5000)
            assert result is True
        finally:
            await browser._close()

    async def test_wait_for_selector_not_found(self) -> None:
        """wait_for_selector returns False for non-existent elements."""
        browser = PlaywrightBackend()
        try:
            await browser._open("https://example.com")
            result = await browser.wait_for_selector("#nonexistent-element-xyz", state="visible", timeout=1000)
            assert result is False
        finally:
            await browser._close()

    async def test_wait_for_selector_hidden(self) -> None:
        """wait_for_selector returns False for hidden elements."""
        browser = PlaywrightBackend()
        try:
            await browser._open("https://example.com")
            result = await browser.wait_for_selector("body", state="hidden", timeout=1000)
            assert result is False
        finally:
            await browser._close()

    async def test_open_sets_networkidle_state(self) -> None:
        """Opening a page should complete networkidle before returning."""
        browser = PlaywrightBackend()
        try:
            t0 = time.monotonic()
            await browser._open("https://example.com")
            elapsed = time.monotonic() - t0
            assert elapsed < 15, f"Open took {elapsed:.1f}s — networkidle may not be working"
        finally:
            await browser._close()
