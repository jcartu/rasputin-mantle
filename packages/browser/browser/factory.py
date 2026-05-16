from __future__ import annotations

import os

from browser.agent_browser_backend import AgentBrowserBackend
from browser.browser_use_backend import BrowserUseBackend
from browser.types import BrowserBackend

BrowserBackendName = str


def create_browser_backend(backend: BrowserBackendName | None = None) -> BrowserBackend:
    selected = backend or os.environ.get("MANTLE_BROWSER_BACKEND", "agent-browser")
    if selected == "agent-browser":
        return AgentBrowserBackend()
    if selected == "browser-use":
        return BrowserUseBackend()
    raise ValueError(f"Unsupported browser backend: {selected}")
