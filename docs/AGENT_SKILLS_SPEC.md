# Agent Skills Standard

Pinned for Rasputin Mantle v1.3 on 2026-05-19. Mantle skills use the Anthropic Agent Skills directory format so skills can be shared across compatible agents without conversion.

## Directory layout

A skill is a directory named with the skill identifier:

```text
my-skill/
  SKILL.md
  scripts/      # optional Python or shell helpers
  templates/    # optional reusable document/code templates
  examples/     # optional example inputs and outputs
```

Only `SKILL.md` is required. Everything else is bundled with the skill and may be referenced by relative path from `SKILL.md`.

## `SKILL.md` frontmatter

`SKILL.md` must start at byte zero with YAML frontmatter delimited by `---` and must include these fields:

```yaml
---
name: my-skill
description: One sentence summary shown in discovery and marketplace views.
when_to_use: Invoke when the user needs a repeatable workflow for X.
capability: research
version: 1.0.0
license: MIT
author: Mantle
metadata:
  tags:
    - research
    - analysis
---
```

Required fields:

- `name`: lowercase letters, digits, and hyphens; max 64 characters.
- `description`: concise human-facing summary; max 1,024 characters.
- `when_to_use`: guidance agents read during discovery to decide whether to invoke the skill.
- `capability`: broad capability group such as `research`, `build`, `summarize`, or `schedule`.
- `version`: semantic version string for compatibility and updates.
- `license`: SPDX-style license identifier.

Recommended fields:

- `author`: marketplace attribution.
- `metadata.tags`: intent tags shown on marketplace cards.
- `metadata.intent_tags`: alias for tags when importing community skills.

## Body

The markdown body should explain the workflow, inputs, outputs, scripts, templates, and examples. Mantle renders the full body on the marketplace detail page.

## Bundled folders

- `scripts/`: Python or shell scripts invoked by the runtime. Scripts should accept JSON on stdin and emit JSON or markdown on stdout. Python files must include `from __future__ import annotations`.
- `templates/`: Optional static files used by the skill, such as emails, reports, dashboards, or landing-page skeletons.
- `examples/`: Optional sample inputs and expected outputs for discovery, tests, and marketplace previews.

## Discovery

Agents discover skills by scanning configured search paths for child directories containing `SKILL.md`. They read only frontmatter during planning and choose a skill when `name`, `description`, `when_to_use`, `capability`, or tags match the user goal.

Mantle search paths, in precedence order:

1. `packages/skills/` for bundled project skills.
2. `/workspace/{session}/_skills/` for session-scoped skills.
3. `~/.mantle/skills/` for user-installed skills.

Discovery is cached per session. The cache is invalidated when `/workspace/{session}/_skills/` changes.

## Invocation

When an agent selects a skill, it emits a `tool_use` block containing the skill name and JSON arguments:

```json
{
  "type": "tool_use",
  "name": "skill.invoke",
  "input": {
    "skill": "research-competitor-analysis",
    "args": {
      "topic": "self-hosted agent platforms",
      "competitors": ["Manus", "OpenHands", "Devin"]
    }
  }
}
```

The runtime resolves the skill from discovery, selects a script (default: first file in `scripts/`, or an explicit `script` argument), sends the remaining arguments as JSON on stdin, and returns stdout, stderr, exit code, and metadata to the agent.
