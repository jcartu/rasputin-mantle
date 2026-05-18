from __future__ import annotations

from codeact.skills_loader import discover_skills


def test_seed_skills_have_required_agent_skill_frontmatter() -> None:
    for skill in discover_skills():
        assert skill.name
        assert skill.description
        assert skill.when_to_use
        assert skill.capability
        assert skill.version
        assert skill.license
        assert skill.sha256
