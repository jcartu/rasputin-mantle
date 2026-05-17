from __future__ import annotations

import os
from typing import Literal

from browser.agent_browser_backend import AgentBrowserBackend
from browser.browser_use_backend import BrowserUseBackend
from browser.errors import BrowserActionError
from browser.playwright_backend import PlaywrightBackend
from browser.types import BrowserBackend

BrowserBackendName = Literal["agent-browser", "browser-use", "playwright"]


def create_browser_backend(
    backend: BrowserBackendName | None = None,
    vision_api_key: str | None = None,
) -> BrowserBackend:
    selected = backend or os.environ.get("MANTLE_BROWSER_BACKEND", "agent-browser")
    vision_key = vision_api_key or os.environ.get("ANTHROPIC_API_KEY")
    if selected == "agent-browser":
        return AgentBrowserBackend()
    if selected == "browser-use":
        return BrowserUseBackend()
    if selected == "playwright":
        return PlaywrightBackend(vision_api_key=vision_key)
    raise BrowserActionError(f"Unsupported browser backend: {selected}")
