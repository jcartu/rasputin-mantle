from __future__ import annotations

from pathlib import Path

from skills.errors import SkillNotFoundError, SkillParseError
from skills.parser import parse_skill_md
from skills.types import SkillMeta


class SkillRegistry:
    def __init__(self, skills_dir: str) -> None:
        self.skills_dir = Path(skills_dir)
        self._by_name: dict[str, SkillMeta] = {}
        self._by_capability: dict[str, list[SkillMeta]] = {}
        self._by_tag: dict[str, list[SkillMeta]] = {}
        self._paths: dict[str, Path] = {}
        self._scan()

    def _scan(self) -> None:
        self._by_name = {}
        self._by_capability = {}
        self._by_tag = {}
        self._paths = {}

        if not self.skills_dir.exists():
            return

        for skill_path in sorted(self.skills_dir.rglob("SKILL.md")):
            try:
                meta = parse_skill_md(skill_path.read_text(encoding="utf-8"))
            except OSError as exc:
                raise SkillParseError(f"Failed to read {skill_path}: {exc}") from exc

            self._by_name[meta.name] = meta
            self._paths[meta.name] = skill_path
            if meta.capability:
                self._by_capability.setdefault(meta.capability, []).append(meta)
            for tag in meta.tags:
                self._by_tag.setdefault(tag, []).append(meta)

    def get(self, name: str) -> SkillMeta:
        try:
            return self._by_name[name]
        except KeyError as exc:
            raise SkillNotFoundError(f"Skill not found: {name}") from exc

    def list_all(self) -> list[SkillMeta]:
        return list(self._by_name.values())

    def by_capability(self, cap_key: str) -> list[SkillMeta]:
        return list(self._by_capability.get(cap_key, []))

    def by_tag(self, tag: str) -> list[SkillMeta]:
        return list(self._by_tag.get(tag, []))

    def reload(self) -> None:
        self._scan()

    def to_dict(self) -> dict[str, SkillMeta]:
        return dict(self._by_name)

    def path_for(self, name: str) -> Path:
        try:
            return self._paths[name]
        except KeyError as exc:
            raise SkillNotFoundError(f"Skill not found: {name}") from exc
