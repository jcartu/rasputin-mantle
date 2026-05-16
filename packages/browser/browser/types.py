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
