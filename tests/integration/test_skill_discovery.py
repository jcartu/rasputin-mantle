from __future__ import annotations

from codeact.skills_loader import discover_skills


def test_skill_discovery_finds_all_w5_seeds() -> None:
    names = {skill.name for skill in discover_skills()}
    assert {
        "research-competitor-analysis",
        "research-literature-review",
        "build-landing-page",
        "build-internal-dashboard",
        "summarize-meeting-recap",
        "summarize-weekly-news-digest",
        "schedule-daily-standup",
        "schedule-weekly-report",
    }.issubset(names)
