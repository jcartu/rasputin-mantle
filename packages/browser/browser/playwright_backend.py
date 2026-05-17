from __future__ import annotations

import asyncio
import base64
import json
from pathlib import Path
from typing import Any

from playwright.async_api import Browser, Page, Playwright, async_playwright
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from browser.auth import AuthWallSignal, LoginWallDetector
from browser.errors import BrowserActionError, BrowserNotAvailable, ElementNotFoundError
from browser.types import BrowserBackend, BrowserElement, BrowserState
from browser.vision import VisionAssist, VisionBudgetExceeded

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
    def __init__(
        self,
        screenshot_dir: str | None = None,
        storage_state_path: str | None = None,
        vision_api_key: str | None = None,
    ) -> None:
        self._playwright_cm: Any | None = None
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._page: Page | None = None
        self._element_selectors: dict[str, str] = {}
        self._elements: dict[str, BrowserElement] = {}
        self.screenshot_dir = screenshot_dir
        self.storage_state_path = storage_state_path
        self.step_counter = 0
        self._vision: VisionAssist | None = VisionAssist(vision_api_key) if vision_api_key else None

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

    def wait_for_selector_sync(self, selector: str, state: str = "visible", timeout: int = 5000) -> bool:
        return self._run(self.wait_for_selector(selector, state, timeout))

    def capture_screenshot_sync(self, path: str | None = None) -> bytes:
        return self._run(self.capture_screenshot(path))

    def save_storage_state_sync(self, path: str) -> None:
        self._run(self.save_storage_state(path))

    def scroll_to_sync(self, element_id: str) -> None:
        self._run(self.scroll_to(element_id))

    def _run(self, awaitable: Any) -> Any:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(awaitable)
        awaitable.close()
        raise BrowserActionError("PlaywrightBackend sync API cannot be called from a running event loop")

    async def _ensure_page(self) -> Page:
        return await self._ensure_page_with_state(self.storage_state_path)

    async def _ensure_page_with_state(self, storage_state_path: str | None = None) -> Page:
        if self._page is not None:
            return self._page

        try:
            self._playwright_cm = async_playwright()
            self._playwright = await self._playwright_cm.__aenter__()
            self._browser = await self._playwright.chromium.launch(headless=True)
            if storage_state_path is not None and Path(storage_state_path).exists():
                self._page = await self._browser.new_page(storage_state=storage_state_path)
            else:
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
            await page.wait_for_load_state("networkidle", timeout=10000)
        except Exception as exc:
            raise BrowserActionError(f"Failed to open {url}: {exc}") from exc

    async def _get_state(self) -> BrowserState:
        page = await self._ensure_page()
        try:
            raw_elements = await page.evaluate(ELEMENT_SNAPSHOT_SCRIPT)
            elements: list[BrowserElement] = []
            selectors: dict[str, str] = {}
            element_lookup: dict[str, BrowserElement] = {}
            for raw in raw_elements:
                if not isinstance(raw, dict):
                    continue
                element_id = str(raw.get("id") or "")
                selector = raw.get("selector")
                if not element_id or not isinstance(selector, str):
                    continue
                selectors[element_id] = selector
                attrs = raw.get("attributes") if isinstance(raw.get("attributes"), dict) else {}
                element = BrowserElement(
                    id=element_id,
                    role=str(raw.get("role") or "unknown"),
                    text=raw.get("text") if isinstance(raw.get("text"), str) else None,
                    attributes={str(key): str(value) for key, value in attrs.items()},
                )
                elements.append(element)
                element_lookup[element_id] = element
            self._element_selectors = selectors
            self._elements = element_lookup
            screenshot = await page.screenshot(full_page=True)
            await self._save_step_screenshot(screenshot)
            screenshot_b64 = base64.b64encode(screenshot).decode("ascii")
            # Hybrid fallback: if DOM extraction returned nothing, try vision
            if not elements and self._vision is not None:
                try:
                    vision_elements = await self._vision_fallback(screenshot)
                    elements.extend(vision_elements)
                except VisionBudgetExceeded:
                    pass  # budget exhausted, return empty state
                except Exception:
                    pass  # vision fallback failed, return empty state
            # Detect auth walls
            auth_wall = self._detect_auth_wall(page.url, await page.title(), elements)
            return BrowserState(
                url=page.url,
                elements=elements,
                title=await page.title(),
                screenshot_b64=screenshot_b64,
                auth_wall=auth_wall,
            )
        except Exception as exc:
            raise BrowserActionError(f"Failed to capture Playwright state: {exc}") from exc

    async def _click(self, element_id: str) -> str:
        return await self._retry_element_action(element_id, "click", None)

    async def _type_text(self, element_id: str, text: str) -> str:
        return await self._retry_element_action(element_id, "type", text)

    async def wait_for_selector(self, selector: str, state: str = "visible", timeout: int = 5000) -> bool:
        page = await self._ensure_page()
        try:
            await page.wait_for_selector(selector, state=state, timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            return False
        except Exception as exc:
            raise BrowserActionError(f"Failed to wait for selector {selector}: {exc}") from exc

    async def capture_screenshot(self, path: str | None = None) -> bytes:
        page = await self._ensure_page()
        try:
            screenshot = await page.screenshot(full_page=True)
            if path is not None:
                target = Path(path)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(screenshot)
            return screenshot
        except Exception as exc:
            raise BrowserActionError(f"Failed to capture screenshot: {exc}") from exc

    async def save_storage_state(self, path: str) -> None:
        page = await self._ensure_page()
        try:
            target = Path(path)
            target.parent.mkdir(parents=True, exist_ok=True)
            await page.context.storage_state(path=path)
        except Exception as exc:
            raise BrowserActionError(f"Failed to save storage state: {exc}") from exc

    async def scroll_to(self, element_id: str) -> None:
        page = await self._ensure_page()
        selector = self._selector_for(element_id)
        try:
            await page.locator(selector).first.scroll_into_view_if_needed()
        except ElementNotFoundError:
            raise
        except Exception as exc:
            raise BrowserActionError(f"Failed to scroll to element {element_id}: {exc}") from exc

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
            self._elements = {}

    def _selector_for(self, element_id: str) -> str:
        selector = self._element_selectors.get(element_id)
        if selector is None:
            raise ElementNotFoundError(f"Unknown element id: {element_id}; call get_state() before interacting")
        return selector

    async def _retry_element_action(self, element_id: str, action: str, text: str | None) -> str:
        last_error: BrowserActionError | None = None
        delays = (0.5, 1.0, 2.0)
        for attempt in range(3):
            try:
                return await self._try_element_action(element_id, action, text)
            except BrowserActionError as exc:
                last_error = exc
                try:
                    await self._get_state()
                except BrowserActionError:
                    pass
                if attempt < 2:
                    await asyncio.sleep(delays[attempt])
        if last_error is not None:
            raise last_error
        raise BrowserActionError(f"Failed to {action} element {element_id}")

    async def _try_element_action(self, element_id: str, action: str, text: str | None) -> str:
        page = await self._ensure_page()
        strategy_errors: list[str] = []
        for strategy, locator in self._locators_for(element_id, page):
            try:
                if action == "click":
                    await locator.click()
                elif action == "type" and text is not None:
                    await locator.fill(text)
                else:
                    raise BrowserActionError(f"Unsupported element action: {action}")
                return strategy
            except Exception as exc:
                strategy_errors.append(f"{strategy}: {exc}")
        if not strategy_errors:
            raise ElementNotFoundError(f"No selector strategies available for element {element_id}")
        raise BrowserActionError(f"Failed to {action} element {element_id}: {'; '.join(strategy_errors)}")

    def _locators_for(self, element_id: str, page: Page) -> list[tuple[str, Any]]:
        selector = self._selector_for(element_id)
        element = self._elements.get(element_id)
        strategies: list[tuple[str, Any]] = [("primary", page.locator(selector).first)]
        if element is None:
            return strategies
        if element.role and element.text:
            strategies.append(("role", page.get_by_role(element.role, name=element.text).first))
        if element.text:
            strategies.append(("text", page.locator(f"text={json.dumps(element.text)}").first))
        aria_label = element.attributes.get("aria-label")
        if aria_label:
            strategies.append(("label", page.get_by_label(aria_label).first))
        return strategies

    async def _save_step_screenshot(self, screenshot: bytes) -> None:
        if self.screenshot_dir is None:
            return
        target_dir = Path(self.screenshot_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / f"step-{self.step_counter}.png"
        target.write_bytes(screenshot)
        self.step_counter += 1

    async def _vision_fallback(self, screenshot: bytes) -> list[BrowserElement]:
        """Fallback: use vision to find interactive elements when DOM is empty."""
        prompt = (
            "Find all interactive elements on this page (buttons, links, inputs, textareas, selects). "
            "Return a JSON array of objects with keys: role, text, x, y, w, h. "
            "If no interactive elements are visible, return an empty array."
        )
        result = await self._vision._call_vision(screenshot, prompt, "find_all_elements")
        if not isinstance(result, list):
            # Handle raw_text fallback or single object
            if isinstance(result, dict) and "raw_text" in result:
                return []
            return []
        elements: list[BrowserElement] = []
        for i, item in enumerate(result):
            if not isinstance(item, dict):
                continue
            role = item.get("role", "unknown")
            text = item.get("text")
            bbox = {
                "x": int(item.get("x", 0)),
                "y": int(item.get("y", 0)),
                "w": int(item.get("w", 0)),
                "h": int(item.get("h", 0)),
            }
            elements.append(
                BrowserElement(
                    id=f"vision-{i}",
                    role=str(role),
                    text=text if isinstance(text, str) else None,
                    bbox=bbox,
                    source="vision",
                )
            )
        return elements

    def reset_vision_task(self) -> None:
        """Reset vision budget for a new task."""
        if self._vision is not None:
            self._vision.reset_task()
    def get_vision_cost_report(self) -> dict:
        """Return vision cost telemetry."""
        if self._vision is None:
            return {"enabled": False}
        return {"enabled": True, **self._vision.get_cost_report()}

    def _detect_auth_wall(
        self,
        url: str,
        title: str,
        elements: list[BrowserElement],
    ) -> AuthWallSignal | None:
        """Check if the current page is behind an auth wall."""
        detector = LoginWallDetector()
        return detector.detect(url, title, elements)
