"""tests/integration/test_browser_screenshot_capture.py — Verify screenshot hardening.

Tests that screenshots are captured on every step and can be saved to disk.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from browser.errors import BrowserActionError
from browser.playwright_backend import PlaywrightBackend


@pytest.mark.asyncio
class TestScreenshotCapture:
    async def test_capture_screenshot_returns_bytes(self) -> None:
        """capture_screenshot returns raw PNG bytes."""
        browser = PlaywrightBackend()
        try:
            await browser._open("https://example.com")
            data = await browser.capture_screenshot()
            assert isinstance(data, bytes)
            assert len(data) > 0
            assert data[:4] == b"\x89PNG"
        finally:
            await browser._close()

    async def test_capture_screenshot_saves_to_path(self, tmp_path: Path) -> None:
        """capture_screenshot saves to file when path is provided."""
        browser = PlaywrightBackend()
        try:
            await browser._open("https://example.com")
            path = tmp_path / "test.png"
            data = await browser.capture_screenshot(str(path))
            assert path.exists()
            assert path.stat().st_size > 0
            assert data == path.read_bytes()
        finally:
            await browser._close()

    async def test_step_screenshots_auto_saved(self, tmp_path: Path) -> None:
        """get_state() auto-saves screenshots when screenshot_dir is set."""
        browser = PlaywrightBackend(screenshot_dir=str(tmp_path / "screenshots"))
        try:
            await browser._open("https://example.com")
            await browser._get_state()
            await browser._get_state()
            screenshot_dir = Path(browser.screenshot_dir)
            assert (screenshot_dir / "step-0.png").exists()
            assert (screenshot_dir / "step-1.png").exists()
        finally:
            await browser._close()

    async def test_step_counter_increments(self, tmp_path: Path) -> None:
        """Step counter increments with each get_state() call."""
        browser = PlaywrightBackend(screenshot_dir=str(tmp_path / "screenshots"))
        try:
            await browser._open("https://example.com")
            assert browser.step_counter == 0
            await browser._get_state()
            assert browser.step_counter == 1
            await browser._get_state()
            assert browser.step_counter == 2
        finally:
            await browser._close()

    async def test_screenshot_without_dir_is_noop(self) -> None:
        """get_state() without screenshot_dir doesn't save files."""
        browser = PlaywrightBackend()
        try:
            await browser._open("https://example.com")
            assert browser.screenshot_dir is None
            state = await browser._get_state()
            assert state.screenshot_b64 is not None
        finally:
            await browser._close()
