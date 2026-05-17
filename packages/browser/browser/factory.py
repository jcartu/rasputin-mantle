from __future__ import annotations

import os
from typing import Literal

from browser.agent_browser_backend import AgentBrowserBackend
from browser.browser_use_backend import BrowserUseBackend
from browser.errors import BrowserActionError
from browser.playwright_backend import PlaywrightBackend
from browser.types import BrowserBackend

BrowserBackendName = Literal["agent-browser", "browser-use", "playwright"]


def create_browser_backend(backend: BrowserBackendName | None = None) -> BrowserBackend:
    selected = backend or os.environ.get("MANTLE_BROWSER_BACKEND", "agent-browser")
    if selected == "agent-browser":
        return AgentBrowserBackend()
    if selected == "browser-use":
        return BrowserUseBackend()
    if selected == "playwright":
        return PlaywrightBackend()
    raise BrowserActionError(f"Unsupported browser backend: {selected}")
