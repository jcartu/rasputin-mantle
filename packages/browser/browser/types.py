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


@dataclass
class BrowserState:
    url: str
    elements: list[BrowserElement]
    screenshot_path: str | None = None


class BrowserBackend(ABC):
    @abstractmethod
    def open(self, url: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_state(self) -> BrowserState:
        raise NotImplementedError

    @abstractmethod
    def click(self, element_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def type(self, element_id: str, text: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def evaluate(self, script: str) -> Any:
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError
