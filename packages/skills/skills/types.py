from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SkillMeta:
    name: str
    description: str
    version: str = "1.0.0"
    author: str = ""
    license: str = "MIT"
    capability: str = ""  # Mantle extension: maps to catalog key
    platforms: list[str] = ()
    tags: list[str] = ()
    prerequisites: dict[str, Any] = ()


@dataclass(frozen=True)
class SkillBundle:
    meta: SkillMeta
    path: str  # filesystem path to SKILL.md
    content: str  # full file content
    files: list[str]  # other files in the skill folder
