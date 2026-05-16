from __future__ import annotations

import os

from browser.agent_browser_backend import AgentBrowserBackend
from browser.browser_use_backend import BrowserUseBackend
from browser.errors import BrowserActionError
from typing import Literal

BrowserBackendName = Literal["agent-browser", "browser-use"]


def create_browser_backend(backend: BrowserBackendName | None = None) -> BrowserBackend:
    selected = backend or os.environ.get("MANTLE_BROWSER_BACKEND", "agent-browser")
    if selected == "agent-browser":
        return AgentBrowserBackend()
    if selected == "browser-use":
        return BrowserUseBackend()
    raise BrowserActionError(f"Unsupported browser backend: {selected}")
