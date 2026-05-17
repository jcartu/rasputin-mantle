from __future__ import annotations

from pathlib import Path

import pytest
from skills.errors import SkillParseError
from skills.loader import load_skill
from skills.parser import parse_skill_md
from skills.registry import SkillRegistry

ROOT = Path(__file__).resolve().parent.parent.parent


class TestSkillsLoaderLoadAll:
    """Test loading all 3 SKILL.md files via the skills loader."""

    def test_load_browser_skill(self) -> None:
        """Load packages/browser/SKILL.md and verify frontmatter parses."""
        skill_path = ROOT / "packages" / "browser" / "SKILL.md"
        assert skill_path.exists(), f"SKILL.md not found at {skill_path}"

        content = skill_path.read_text(encoding="utf-8")
        meta = parse_skill_md(content)

        assert meta.name == "browser"
        assert meta.description
        assert meta.version == "1.0.0"
        assert meta.license == "MIT"
        assert meta.capability == "browser_automation"

    def test_load_skills_skill(self) -> None:
        """Load packages/skills/SKILL.md and verify frontmatter parses."""
        skill_path = ROOT / "packages" / "skills" / "SKILL.md"
        assert skill_path.exists(), f"SKILL.md not found at {skill_path}"

        content = skill_path.read_text(encoding="utf-8")
        meta = parse_skill_md(content)

        assert meta.name == "skills"
        assert meta.description
        assert meta.version == "1.0.0"
        assert meta.license == "MIT"
        assert meta.capability == "skill_loader"

    def test_load_sandbox_skill(self) -> None:
        """Load packages/sandbox/SKILL.md and verify frontmatter parses."""
        skill_path = ROOT / "packages" / "sandbox" / "SKILL.md"
        assert skill_path.exists(), f"SKILL.md not found at {skill_path}"

        content = skill_path.read_text(encoding="utf-8")
        meta = parse_skill_md(content)

        assert meta.name == "sandbox"
        assert meta.description
        assert meta.version == "1.0.0"
        assert meta.license == "MIT"
        assert meta.capability == "sandbox_execution"

    def test_registry_loads_all_skills(self) -> None:
        """Test that SkillRegistry loads all 3 skills without returning []."""
        skills_root = ROOT / "packages"
        registry = SkillRegistry(str(skills_root))

        all_skills = registry.list_all()
        assert len(all_skills) >= 3, f"Expected at least 3 skills, got {len(all_skills)}"

        skill_names = {skill.name for skill in all_skills}
        assert "browser" in skill_names
        assert "skills" in skill_names
        assert "sandbox" in skill_names

    def test_registry_get_by_name(self) -> None:
        """Test that registry can retrieve skills by name."""
        skills_root = ROOT / "packages"
        registry = SkillRegistry(str(skills_root))

        browser_skill = registry.get("browser")
        assert browser_skill.name == "browser"
        assert browser_skill.capability == "browser_automation"

        skills_skill = registry.get("skills")
        assert skills_skill.name == "skills"
        assert skills_skill.capability == "skill_loader"

        sandbox_skill = registry.get("sandbox")
        assert sandbox_skill.name == "sandbox"
        assert sandbox_skill.capability == "sandbox_execution"

    def test_load_skill_bundle(self) -> None:
        """Test load_skill() returns SkillBundle with metadata and content."""
        skills_root = ROOT / "packages"
        bundle = load_skill(str(skills_root), "browser")

        assert bundle.meta.name == "browser"
        assert bundle.path
        assert bundle.content
        assert "---" in bundle.content  # YAML frontmatter present
        assert isinstance(bundle.files, list)


class TestSkillParseErrorHandling:
    """Test that malformed frontmatter raises SkillParseError."""

    def test_missing_opening_delimiter(self) -> None:
        """Malformed: missing opening --- delimiter."""
        content = "name: test\ndescription: test\n---\n\nThis is a markdown playbook — invoke via bash, not skill_mcp()"
        with pytest.raises(SkillParseError, match="must start with YAML frontmatter delimiter"):
            parse_skill_md(content)

    def test_missing_closing_delimiter(self) -> None:
        """Malformed: missing closing --- delimiter."""
        content = "---\nname: test\ndescription: test\n\nThis is a markdown playbook — invoke via bash, not skill_mcp()"
        with pytest.raises(SkillParseError, match="missing closing delimiter"):
            parse_skill_md(content)

    def test_missing_required_name_field(self) -> None:
        """Malformed: missing required 'name' field."""
        content = "---\ndescription: test\n---\n\nThis is a markdown playbook — invoke via bash, not skill_mcp()"
        with pytest.raises(SkillParseError, match="missing required field: name"):
            parse_skill_md(content)

    def test_missing_required_description_field(self) -> None:
        """Malformed: missing required 'description' field."""
        content = "---\nname: test\n---\n\nThis is a markdown playbook — invoke via bash, not skill_mcp()"
        with pytest.raises(SkillParseError, match="missing required field: description"):
            parse_skill_md(content)

    def test_missing_playbook_preamble(self) -> None:
        """Malformed: missing markdown playbook preamble in body."""
        content = "---\nname: test\ndescription: test\n---\n\nSome other content"
        with pytest.raises(SkillParseError, match="missing required markdown playbook preamble"):
            parse_skill_md(content)

    def test_invalid_yaml_frontmatter(self) -> None:
        """Malformed: invalid YAML syntax in frontmatter."""
        content = (
            "---\nname: test\ndescription: :\n---\n\n"
            "This is a markdown playbook — invoke via bash, not skill_mcp()"
        )
        with pytest.raises(SkillParseError, match="Invalid YAML frontmatter"):
            parse_skill_md(content)

    def test_invalid_skill_name_pattern(self) -> None:
        """Malformed: skill name violates pattern (uppercase not allowed)."""
        content = (
            "---\nname: InvalidName\ndescription: test\n---\n\n"
            "This is a markdown playbook — invoke via bash, not skill_mcp()"
        )
        with pytest.raises(SkillParseError, match="lowercase, hyphenated"):
            parse_skill_md(content)

    def test_description_exceeds_max_length(self) -> None:
        """Malformed: description exceeds 1024 character limit."""
        long_desc = "x" * 1025
        content = (
            f"---\nname: test\ndescription: {long_desc}\n---\n\n"
            "This is a markdown playbook — invoke via bash, not skill_mcp()"
        )
        with pytest.raises(SkillParseError, match="exceeds 1024 characters"):
            parse_skill_md(content)

    def test_file_exceeds_max_size(self) -> None:
        """Malformed: SKILL.md file exceeds 100,000 character limit."""
        large_content = "x" * 100_001
        with pytest.raises(SkillParseError, match="exceeds 100000 characters"):
            parse_skill_md(large_content)
