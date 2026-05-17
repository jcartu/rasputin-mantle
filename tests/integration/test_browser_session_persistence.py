"""tests/integration/test_browser_session_persistence.py — Verify session/cookie persistence.

Tests that storage state can be saved and restored across browser sessions.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from browser.playwright_backend import PlaywrightBackend


@pytest.mark.asyncio
class TestSessionPersistence:
    async def test_save_storage_state_creates_file(self, tmp_path: Path) -> None:
        """save_storage_state writes a JSON file."""
        browser = PlaywrightBackend()
        try:
            await browser._open("https://example.com")
            path = str(tmp_path / "storage.json")
            await browser.save_storage_state(path)
            assert Path(path).exists()
            data = json.loads(Path(path).read_text())
            assert "origins" in data or "cookies" in data
        finally:
            await browser._close()

    async def test_storage_state_contains_cookies(self, tmp_path: Path) -> None:
        """Storage state captures cookies set by the page."""
        browser = PlaywrightBackend()
        try:
            await browser._open("https://example.com")
            await browser._evaluate("document.cookie = 'test=hello; path=/';")
            path = str(tmp_path / "storage.json")
            await browser.save_storage_state(path)
            data = json.loads(Path(path).read_text())
            cookies = data.get("cookies", [])
            test_cookies = [c for c in cookies if c.get("name") == "test"]
            assert len(test_cookies) >= 1, f"Cookie not found in storage state: {cookies}"
        finally:
            await browser._close()

    async def test_ensure_page_with_state_loads_storage(self, tmp_path: Path) -> None:
        """_ensure_page_with_state loads storage state if file exists."""
        b1 = PlaywrightBackend()
        path = str(tmp_path / "storage.json")
        try:
            await b1._open("https://example.com")
            await b1._evaluate("document.cookie = 'persisted=yes; path=/';")
            await b1.save_storage_state(path)
        finally:
            await b1._close()

        b2 = PlaywrightBackend(storage_state_path=path)
        try:
            await b2._open("https://example.com")
            cookie = await b2._evaluate("document.cookie")
            assert "persisted=yes" in str(cookie), f"Storage state not restored: {cookie}"
        finally:
            await b2._close()

    async def test_nonexistent_storage_state_is_ignored(self) -> None:
        """_ensure_page_with_state ignores missing storage state file."""
        browser = PlaywrightBackend(storage_state_path="/nonexistent/path/storage.json")
        try:
            await browser._open("https://example.com")
            state = await browser._get_state()
            assert state.url == "https://example.com/"
        finally:
            await browser._close()

    async def test_scroll_to_element(self) -> None:
        """scroll_to scrolls an element into view."""
        browser = PlaywrightBackend()
        try:
            await browser._open("https://example.com")
            state = await browser._get_state()
            if state.elements:
                await browser.scroll_to(state.elements[0].id)
        finally:
            await browser._close()
