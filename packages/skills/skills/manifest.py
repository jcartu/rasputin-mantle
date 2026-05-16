from __future__ import annotations

import hashlib

from skills.registry import SkillRegistry


def generate_manifest(registry: SkillRegistry) -> dict[str, list[dict[str, str]]]:
    skills: list[dict[str, str]] = []
    for meta in registry.list_all():
        skill_path = registry.path_for(meta.name)
        skills.append(
            {
                "name": meta.name,
                "description": meta.description,
                "version": meta.version,
                "capability": meta.capability,
                "sha256": hashlib.sha256(skill_path.read_bytes()).hexdigest(),
                "license": meta.license,
                "trust_level": "bundled",
            }
        )
    return {"skills": skills}
