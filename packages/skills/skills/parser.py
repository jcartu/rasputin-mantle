from __future__ import annotations

import re
from typing import Any

import yaml

from skills.errors import SkillParseError
from skills.types import SkillMeta

MAX_SKILL_MD_CHARS = 100_000
MAX_DESCRIPTION_CHARS = 1024
NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
PLAYBOOK_PREAMBLE = "This is a markdown playbook — invoke via bash, not skill_mcp()"


def parse_skill_md(content: str) -> SkillMeta:
    if len(content) > MAX_SKILL_MD_CHARS:
        raise SkillParseError("SKILL.md exceeds 100000 characters")
    if not content.startswith("---"):
        raise SkillParseError("SKILL.md must start with YAML frontmatter delimiter at byte 0")

    lines = content.splitlines()
    if not lines or lines[0] != "---":
        raise SkillParseError("SKILL.md frontmatter opening delimiter must be exactly '---'")

    try:
        close_index = lines[1:].index("---") + 1
    except ValueError as exc:
        raise SkillParseError("SKILL.md frontmatter missing closing delimiter") from exc

    frontmatter = "\n".join(lines[1:close_index])
    try:
        raw_meta = yaml.safe_load(frontmatter) or {}
    except yaml.YAMLError as exc:
        raise SkillParseError(f"Invalid YAML frontmatter: {exc}") from exc

    if not isinstance(raw_meta, dict):
        raise SkillParseError("SKILL.md frontmatter must be a YAML mapping")

    body = "\n".join(lines[close_index + 1 :])
    if PLAYBOOK_PREAMBLE not in body:
        raise SkillParseError("SKILL.md body missing required markdown playbook preamble")

    return _meta_from_mapping(raw_meta)


def _meta_from_mapping(raw_meta: dict[Any, Any]) -> SkillMeta:
    name = _required_string(raw_meta, "name")
    if not NAME_PATTERN.fullmatch(name):
        raise SkillParseError("Skill name must be lowercase, hyphenated, and no more than 64 characters")

    description = _required_string(raw_meta, "description")
    if len(description) > MAX_DESCRIPTION_CHARS:
        raise SkillParseError("Skill description exceeds 1024 characters")

    return SkillMeta(
        name=name,
        description=description,
        version=_optional_string(raw_meta, "version", "1.0.0"),
        author=_optional_string(raw_meta, "author", ""),
        license=_optional_string(raw_meta, "license", "MIT"),
        capability=_optional_string(raw_meta, "capability", ""),
        platforms=_string_list(raw_meta.get("platforms", ()), "platforms"),
        tags=_metadata_tags(raw_meta),
        prerequisites=_dict_value(raw_meta.get("prerequisites", {}), "prerequisites"),
    )


def _required_string(raw_meta: dict[Any, Any], key: str) -> str:
    if key not in raw_meta:
        raise SkillParseError(f"Skill frontmatter missing required field: {key}")
    value = raw_meta[key]
    if not isinstance(value, str) or not value.strip():
        raise SkillParseError(f"Skill frontmatter field must be a non-empty string: {key}")
    return value


def _optional_string(raw_meta: dict[Any, Any], key: str, default: str) -> str:
    value = raw_meta.get(key, default)
    if value is None:
        return default
    if not isinstance(value, str):
        raise SkillParseError(f"Skill frontmatter field must be a string: {key}")
    return value


def _string_list(value: Any, key: str) -> list[str]:
    if value in (None, ()):
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise SkillParseError(f"Skill frontmatter field must be a list of strings: {key}")
    return value


def _dict_value(value: Any, key: str) -> dict[str, Any]:
    if value in (None, ()):
        return {}
    if not isinstance(value, dict):
        raise SkillParseError(f"Skill frontmatter field must be a mapping: {key}")
    return {str(item_key): item_value for item_key, item_value in value.items()}


def _metadata_tags(raw_meta: dict[Any, Any]) -> list[str]:
    metadata = raw_meta.get("metadata", {})
    if metadata in (None, ()):
        return []
    if not isinstance(metadata, dict):
        raise SkillParseError("Skill frontmatter field must be a mapping: metadata")

    hermes = metadata.get("hermes", {})
    if hermes in (None, ()):
        return []
    if not isinstance(hermes, dict):
        raise SkillParseError("Skill frontmatter field must be a mapping: metadata.hermes")

    return _string_list(hermes.get("tags", ()), "metadata.hermes.tags")
