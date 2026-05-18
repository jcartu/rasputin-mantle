from __future__ import annotations

from codeact.skills_loader import save_session_as_skill


def test_save_as_skill_round_trip() -> None:
    skill = save_session_as_skill(
        session_id="test-session",
        name="test-session-saved-skill",
        description="Saved test session workflow.",
        tags=["test"],
    )

    assert skill.name == "test-session-saved-skill"
    assert skill.capability == "saved_workflow"
