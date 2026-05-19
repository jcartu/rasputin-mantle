from __future__ import annotations

from codeact.skills_loader import discover_skills, invoke_skill


def test_productivity_skills_are_discovered_and_costed() -> None:
    skills = {skill.name: skill for skill in discover_skills()}
    assert skills["slides"].capability == "presentation"
    assert skills["spreadsheet"].capability == "spreadsheet"
    assert skills["document"].capability == "document"

    result = invoke_skill(
        "slides",
        {"outline": {"title": "Cost", "sections": []}, "output_dir": "/tmp/mantle-skill-cost"},
    )
    assert result.exit_code == 0
    assert result.estimated_cost_usd >= 0.01
    assert result.cost_metadata["meter"] == "skill-invocation"
    assert result.cost_metadata["skill"] == "slides"
