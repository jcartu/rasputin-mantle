from __future__ import annotations

from codeact.skills_loader import invoke_skill


def test_skill_invocation_round_trip() -> None:
    result = invoke_skill(
        "summarize-meeting-recap",
        {"notes": "We agreed to ship W5 and follow up on marketplace QA.", "attendees": ["Ada", "Lin"]},
    )

    assert result.exit_code == 0
    assert "Meeting recap" in result.stdout
    assert "Ada, Lin" in result.stdout
