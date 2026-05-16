from __future__ import annotations

from pathlib import Path

import pytest
from skills.errors import SkillParseError
from skills.loader import load_skill
from skills.manifest import generate_manifest
from skills.parser import parse_skill_md
from skills.registry import SkillRegistry

VALID_SKILL = """---
name: webdev
description: Build and refine web applications.
version: 1.2.3
author: Mantle
license: MIT
capability: webapp_builder
platforms:
  - linux
metadata:
  hermes:
    tags:
      - web
      - frontend
prerequisites:
  python: ">=3.11"
---
This is a markdown playbook — invoke via bash, not skill_mcp()

Use the bundled scripts to scaffold a web app.
"""


def test_parse_skill_md_with_valid_frontmatter() -> None:
    meta = parse_skill_md(VALID_SKILL)

    assert meta.name == "webdev"
    assert meta.description == "Build and refine web applications."
    assert meta.version == "1.2.3"
    assert meta.author == "Mantle"
    assert meta.license == "MIT"
    assert meta.capability == "webapp_builder"
    assert meta.platforms == ["linux"]
    assert meta.tags == ["web", "frontend"]
    assert meta.prerequisites == {"python": ">=3.11"}


def test_parse_skill_md_rejects_missing_name() -> None:
    content = """---
description: Missing a name.
---
This is a markdown playbook — invoke via bash, not skill_mcp()
"""

    with pytest.raises(SkillParseError, match="missing required field: name"):
        parse_skill_md(content)


def test_parse_skill_md_rejects_missing_frontmatter_at_byte_zero() -> None:
    content = "\n---\nname: webdev\ndescription: Invalid.\n---\nBody"

    with pytest.raises(SkillParseError, match="YAML frontmatter delimiter"):
        parse_skill_md(content)


def test_parse_skill_md_rejects_long_description() -> None:
    content = f"""---
name: webdev
description: {"x" * 1025}
---
This is a markdown playbook — invoke via bash, not skill_mcp()
"""

    with pytest.raises(SkillParseError, match="1024"):
        parse_skill_md(content)


def test_parse_skill_md_rejects_missing_playbook_preamble() -> None:
    content = """---
name: webdev
description: Missing playbook preamble.
---
Use this skill without the required warning.
"""

    with pytest.raises(SkillParseError, match="preamble"):
        parse_skill_md(content)


def test_registry_scans_mock_skills(tmp_path: Path) -> None:
    _write_skill(tmp_path, "webdev", VALID_SKILL)
    _write_skill(
        tmp_path,
        "slides",
        """---
name: slides
description: Create slide decks.
capability: slides
metadata:
  hermes:
    tags:
      - presentation
---
This is a markdown playbook — invoke via bash, not skill_mcp()
""",
    )

    registry = SkillRegistry(str(tmp_path))

    assert registry.get("webdev").capability == "webapp_builder"
    assert [skill.name for skill in registry.list_all()] == ["slides", "webdev"]
    assert [skill.name for skill in registry.by_capability("slides")] == ["slides"]
    assert [skill.name for skill in registry.by_tag("web")] == ["webdev"]
    assert set(registry.to_dict()) == {"slides", "webdev"}


def test_manifest_generation(tmp_path: Path) -> None:
    _write_skill(tmp_path, "webdev", VALID_SKILL)
    registry = SkillRegistry(str(tmp_path))

    manifest = generate_manifest(registry)

    assert list(manifest) == ["skills"]
    assert manifest["skills"][0]["name"] == "webdev"
    assert manifest["skills"][0]["capability"] == "webapp_builder"
    assert len(manifest["skills"][0]["sha256"]) == 64
    assert manifest["skills"][0]["trust_level"] == "bundled"


def test_load_skill_with_mock_data(tmp_path: Path) -> None:
    skill_dir = _write_skill(tmp_path, "webdev", VALID_SKILL)
    script_path = skill_dir / "scripts" / "build.py"
    script_path.parent.mkdir()
    script_path.write_text("from __future__ import annotations\n", encoding="utf-8")

    bundle = load_skill(str(tmp_path), "webdev")

    assert bundle.meta.name == "webdev"
    assert bundle.path == str(skill_dir / "SKILL.md")
    assert bundle.content == VALID_SKILL
    assert bundle.files == [str(script_path)]


def _write_skill(root: Path, name: str, content: str) -> Path:
    skill_dir = root / name
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")
    return skill_dir
