from __future__ import annotations

import asyncio
import base64
from typing import Any

from playwright.async_api import Browser, Page, Playwright, async_playwright

from browser.errors import BrowserActionError, BrowserNotAvailable
from browser.types import BrowserBackend, BrowserElement, BrowserState

ELEMENT_SNAPSHOT_SCRIPT = r"""
() => {
  const interactiveSelector = [
    'a[href]',
    'button',
    'input',
    'textarea',
    'select',
    '[role]',
    '[contenteditable="true"]',
    '[tabindex]:not([tabindex="-1"])'
  ].join(',');

  function cssEscape(value) {
    if (window.CSS && typeof window.CSS.escape === 'function') {
      return window.CSS.escape(value);
    }
    return String(value).replace(/[^a-zA-Z0-9_-]/g, '\\$&');
  }

  function selectorFor(element) {
    if (element.id) {
      return `#${cssEscape(element.id)}`;
    }
    for (const attr of ['data-testid', 'data-test', 'aria-label', 'name']) {
      const value = element.getAttribute(attr);
      if (value) {
        return `${element.tagName.toLowerCase()}[${attr}="${String(value).replace(/"/g, '\\"')}"]`;
      }
    }

    const parts = [];
    let current = element;
    while (current && current.nodeType === Node.ELEMENT_NODE && current !== document.body) {
      const tag = current.tagName.toLowerCase();
      const siblings = Array.from(current.parentElement?.children || []).filter(
        (sibling) => sibling.tagName === current.tagName
      );
      const index = siblings.indexOf(current) + 1;
      parts.unshift(siblings.length > 1 ? `${tag}:nth-of-type(${index})` : tag);
      current = current.parentElement;
    }
    return parts.length ? parts.join(' > ') : element.tagName.toLowerCase();
  }

  function roleFor(element) {
    const explicitRole = element.getAttribute('role');
    if (explicitRole) {
      return explicitRole;
    }
    const tag = element.tagName.toLowerCase();
    if (tag === 'a') return 'link';
    if (tag === 'button') return 'button';
    if (tag === 'input') return element.getAttribute('type') || 'textbox';
    if (tag === 'textarea') return 'textbox';
    if (tag === 'select') return 'combobox';
    return tag;
  }

  return Array.from(document.querySelectorAll(interactiveSelector)).map((element, index) => {
    const attributes = {};
    for (const attr of ['id', 'name', 'type', 'href', 'aria-label', 'placeholder', 'value', 'data-testid']) {
      const value = element.getAttribute(attr);
      if (value !== null) {
        attributes[attr] = value;
      }
    }
    return {
      id: `pw-${index}`,
      role: roleFor(element),
      text: (
        element.innerText || element.getAttribute('aria-label') || element.getAttribute('value') || ''
      ).trim() || null,
      attributes,
      selector: selectorFor(element)
    };
  });
}
"""


class PlaywrightBackend(BrowserBackend):
    def __init__(self) -> None:
        self._playwright_cm: Any | None = None
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._page: Page | None = None
        self._element_selectors: dict[str, str] = {}

    def open(self, url: str) -> None:
        self._run(self._open(url))

    def get_state(self) -> BrowserState:
        return self._run(self._get_state())

    def click(self, element_id: str) -> None:
        self._run(self._click(element_id))

    def type(self, element_id: str, text: str) -> None:
        self.type_text(element_id, text)

    def type_text(self, element_id: str, text: str) -> None:
        self._run(self._type_text(element_id, text))

    def evaluate(self, script: str) -> Any:
        return self._run(self._evaluate(script))

    def close(self) -> None:
        self._run(self._close())

    def _run(self, awaitable: Any) -> Any:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(awaitable)
        awaitable.close()
        raise BrowserActionError("PlaywrightBackend sync API cannot be called from a running event loop")

    async def _ensure_page(self) -> Page:
        if self._page is not None:
            return self._page

        try:
            self._playwright_cm = async_playwright()
            self._playwright = await self._playwright_cm.__aenter__()
            self._browser = await self._playwright.chromium.launch(headless=True)
            self._page = await self._browser.new_page()
        except ImportError as exc:
            raise BrowserNotAvailable("playwright is not installed") from exc
        except Exception as exc:
            await self._close()
            raise BrowserActionError(f"Failed to start Playwright browser: {exc}") from exc
        return self._page

    async def _open(self, url: str) -> None:
        page = await self._ensure_page()
        try:
            await page.goto(url, wait_until="domcontentloaded")
        except Exception as exc:
            raise BrowserActionError(f"Failed to open {url}: {exc}") from exc

    async def _get_state(self) -> BrowserState:
        page = await self._ensure_page()
        try:
            raw_elements = await page.evaluate(ELEMENT_SNAPSHOT_SCRIPT)
            elements: list[BrowserElement] = []
            selectors: dict[str, str] = {}
            for raw in raw_elements:
                if not isinstance(raw, dict):
                    continue
                element_id = str(raw.get("id") or "")
                selector = raw.get("selector")
                if not element_id or not isinstance(selector, str):
                    continue
                selectors[element_id] = selector
                attrs = raw.get("attributes") if isinstance(raw.get("attributes"), dict) else {}
                elements.append(
                    BrowserElement(
                        id=element_id,
                        role=str(raw.get("role") or "unknown"),
                        text=raw.get("text") if isinstance(raw.get("text"), str) else None,
                        attributes={str(key): str(value) for key, value in attrs.items()},
                    )
                )
            self._element_selectors = selectors
            screenshot_b64 = base64.b64encode(await page.screenshot(full_page=True)).decode("ascii")
            return BrowserState(
                url=page.url,
                elements=elements,
                title=await page.title(),
                screenshot_b64=screenshot_b64,
            )
        except Exception as exc:
            raise BrowserActionError(f"Failed to capture Playwright state: {exc}") from exc

    async def _click(self, element_id: str) -> None:
        page = await self._ensure_page()
        selector = self._selector_for(element_id)
        try:
            await page.locator(selector).first.click()
        except Exception as exc:
            raise BrowserActionError(f"Failed to click element {element_id}: {exc}") from exc

    async def _type_text(self, element_id: str, text: str) -> None:
        page = await self._ensure_page()
        selector = self._selector_for(element_id)
        try:
            await page.locator(selector).first.fill(text)
        except Exception as exc:
            raise BrowserActionError(f"Failed to type into element {element_id}: {exc}") from exc

    async def _evaluate(self, script: str) -> Any:
        page = await self._ensure_page()
        try:
            return await page.evaluate(script)
        except Exception as exc:
            raise BrowserActionError(f"Failed to evaluate script: {exc}") from exc

    async def _close(self) -> None:
        try:
            if self._browser is not None:
                await self._browser.close()
            if self._playwright_cm is not None:
                await self._playwright_cm.__aexit__(None, None, None)
        finally:
            self._browser = None
            self._page = None
            self._playwright = None
            self._playwright_cm = None
            self._element_selectors = {}

    def _selector_for(self, element_id: str) -> str:
        selector = self._element_selectors.get(element_id)
        if selector is None:
            raise BrowserActionError(f"Unknown element id: {element_id}; call get_state() before interacting")
        return selector
