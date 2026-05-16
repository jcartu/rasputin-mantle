from __future__ import annotations

import hashlib

from skills.registry import SkillRegistry


def generate_manifest(registry: SkillRegistry, trust_level: str = "bundled") -> dict[str, list[dict[str, str]]]:
    skills: list[dict[str, str]] = []
    for meta in registry.list_all():
        skill_path = registry.path_for(meta.name)
        try:
            sha = hashlib.sha256(skill_path.read_bytes()).hexdigest()
        except OSError:
            sha = ""
        skills.append(
            {
                "name": meta.name,
                "description": meta.description,
                "version": meta.version,
                "capability": meta.capability,
                "sha256": sha,
                "license": meta.license,
                "trust_level": trust_level,
            }
        )
    return {"skills": skills}
