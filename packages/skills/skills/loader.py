from __future__ import annotations

from pathlib import Path

from skills.registry import SkillRegistry
from skills.types import SkillBundle


def load_skill(skills_dir: str, name: str) -> SkillBundle:
    registry = SkillRegistry(skills_dir)
    meta = registry.get(name)
    skill_path = registry.path_for(name)
    skill_dir = skill_path.parent
    files = [str(p) for p in sorted(skill_dir.rglob("*")) if p.is_file() and p.name != "SKILL.md"]
    return SkillBundle(
        meta=meta,
        path=str(skill_path),
        content=skill_path.read_text(encoding="utf-8"),
        files=files,
    )
