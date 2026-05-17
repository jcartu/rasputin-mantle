---
name: skills
description: Skill loader, registry, and manifest API for discovering and loading markdown playbooks.
version: 1.0.0
author: Mantle
license: MIT
capability: skill_loader
platforms:
  - linux
---

This is a markdown playbook — invoke via bash, not skill_mcp()

## Overview

The `skills` package provides a complete skill discovery and loading system. Skills are markdown playbooks with YAML frontmatter that define metadata, capabilities, and prerequisites. This module handles parsing, validation, registry management, and manifest generation.

## Core API

### Parser: `parse_skill_md(content: str) -> SkillMeta`

Parses a SKILL.md file and validates its structure.

**Validation Rules:**
- File must start with `---` (YAML frontmatter delimiter)
- Frontmatter must close with `---` on its own line
- Body must contain the playbook preamble: `This is a markdown playbook — invoke via bash, not skill_mcp()`
- Total file size must not exceed 100,000 characters
- Description must not exceed 1,024 characters

**Raises:** `SkillParseError` if validation fails.

### Frontmatter Schema

Required fields:
- `name` (string): Skill identifier, lowercase alphanumeric with hyphens, max 64 chars
- `description` (string): One-line summary, max 1,024 chars

Optional fields:
- `version` (string, default: "1.0.0"): Semantic version
- `author` (string, default: ""): Skill author name
- `license` (string, default: "MIT"): License identifier
- `capability` (string, default: ""): Capability tag for grouping
- `platforms` (list[string], default: []): Supported platforms (e.g., "linux", "macos")
- `metadata.hermes.tags` (list[string], default: []): Search tags
- `prerequisites` (dict[string, string], default: {}): Runtime requirements (e.g., `python: ">=3.11"`)

### Registry: `SkillRegistry(root_path: str)`

Scans a directory tree for SKILL.md files and indexes them.

**Methods:**
- `get(name: str) -> SkillMeta`: Retrieve a skill by name
- `list_all() -> list[SkillMeta]`: List all skills, sorted by name
- `by_capability(cap: str) -> list[SkillMeta]`: Filter by capability
- `by_tag(tag: str) -> list[SkillMeta]`: Filter by metadata tag
- `to_dict() -> dict[str, SkillMeta]`: Export as mapping

### Loader: `load_skill(root_path: str, name: str) -> SkillBundle`

Loads a skill and its associated files (scripts, configs, etc.).

**Returns:** `SkillBundle` with:
- `meta: SkillMeta` — Parsed frontmatter
- `path: str` — Absolute path to SKILL.md
- `content: str` — Full file content
- `files: list[str]` — Paths to bundled scripts/resources

### Manifest: `generate_manifest(registry: SkillRegistry) -> dict`

Generates a marketplace manifest with SHA256 hashes and trust levels.

**Output structure:**
```yaml
skills:
  - name: skill-name
    capability: capability-tag
    sha256: <64-char hex>
    trust_level: bundled|community|unverified
```

## Example SKILL.md

```yaml
---
name: my-skill
description: Brief description of what this skill does.
version: 1.0.0
author: Your Name
license: MIT
capability: my_capability
platforms:
  - linux
metadata:
  hermes:
    tags:
      - tag1
      - tag2
prerequisites:
  python: ">=3.11"
---

This is a markdown playbook — invoke via bash, not skill_mcp()

## Usage

Instructions and examples for using this skill.
```

## Error Handling

All parsing errors raise `SkillParseError` with descriptive messages:
- Missing required fields
- Invalid YAML syntax
- Malformed frontmatter delimiters
- Missing playbook preamble
- Oversized descriptions or files
- Invalid name format
