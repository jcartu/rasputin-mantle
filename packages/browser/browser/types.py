from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class BrowserElement:
    id: str
    role: str
    text: str | None = None
    attributes: dict[str, str] = field(default_factory=dict)
    bbox: dict[str, int] | None = None  # {x, y, w, h} from vision fallback
    source: str = "dom"  # "dom" | "vision"

@dataclass
class BrowserState:
    url: str
    elements: list[BrowserElement]
    title: str = ""
    screenshot_b64: str | None = None


class BrowserBackend(ABC):
    @abstractmethod
    def open(self, url: str) -> None: ...

    @abstractmethod
    def get_state(self) -> BrowserState: ...

    @abstractmethod
    def click(self, element_id: str) -> None: ...

    @abstractmethod
    def type(self, element_id: str, text: str) -> None: ...

    @abstractmethod
    def evaluate(self, script: str) -> Any: ...

    @abstractmethod
    def close(self) -> None: ...

    @abstractmethod
    def wait_for_selector(self, selector: str, state: str = "visible", timeout: int = 5000) -> bool: ...

    @abstractmethod
    def capture_screenshot(self, path: str | None = None) -> bytes: ...

    @abstractmethod
    def save_storage_state(self, path: str) -> None: ...

    @abstractmethod
    def scroll_to(self, element_id: str) -> None: ...
