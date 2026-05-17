from __future__ import annotations

from browser.agent_browser_backend import AgentBrowserBackend
from browser.auth import AuthWallSignal, AuthWallType, LoginWallDetector
from browser.browser_use_backend import BrowserUseBackend
from browser.errors import BrowserActionError, BrowserNotAvailable
from browser.factory import create_browser_backend
from browser.playwright_backend import PlaywrightBackend
from browser.types import BrowserBackend, BrowserElement, BrowserState
from browser.vision import VisionAssist, VisionBudgetExceeded

__version__ = "0.1.0"

__all__ = [
    "AgentBrowserBackend",
    "AuthWallSignal",
    "AuthWallType",
    "BrowserActionError",
    "BrowserBackend",
    "BrowserElement",
    "BrowserNotAvailable",
    "BrowserState",
    "BrowserUseBackend",
    "LoginWallDetector",
    "PlaywrightBackend",
    "VisionAssist",
    "VisionBudgetExceeded",
    "create_browser_backend",
]
