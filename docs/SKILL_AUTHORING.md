# Authoring Skills

A skill is a single `SKILL.md` file that describes how an agent should use a capability or tool. The skills loader (`packages/skills/skill_loader.py`) reads SKILL.md files, validates their frontmatter, and exposes the resulting capabilities through the catalog. Skills are how Mantle stays extensible without code changes — drop a SKILL.md into the right place, restart the gateway, and the agent has a new tool.

## Anatomy

```markdown
---
name: pdf-extract
version: 1.0.0
inputs:
  - name: pdf_url
    type: string
    description: HTTPS URL to a PDF file. Must be < 50 MB.
required: [pdf_url]
returns: object
returns_schema:
  text: string
  pages: integer
  metadata: object
tags: [files, ocr]
license: MIT
---

# pdf-extract

Use this when you need the textual content of a PDF. The skill downloads the
file, runs OCR if the PDF is scanned, and returns the extracted text plus
basic metadata.

## When to use

- Reading research papers, reports, invoices, scanned documents.
- When you need text content, not the visual layout.

## When NOT to use

- For visual layout (use `pdf-screenshot` instead).
- For files larger than 50 MB (split first).
- For password-protected PDFs (the skill will fail; ask the user).

## Examples

```python
result = invoke("pdf-extract", {"pdf_url": "https://arxiv.org/pdf/2503.12345"})
print(result["text"][:500])
```

## Errors

- `PDF_TOO_LARGE`: file exceeds 50 MB. Split or download separately.
- `PDF_ENCRYPTED`: password required. Ask user for password and retry.
- `PDF_DOWNLOAD_FAILED`: URL not reachable. Check the URL and retry.
```

## Frontmatter fields

| Field            | Type               | Required | Notes                                                              |
|------------------|--------------------|----------|--------------------------------------------------------------------|
| `name`           | string             | yes      | Snake_case-or-kebab-case identifier. Unique across the catalog.    |
| `version`        | semver string      | yes      | Breaking changes bump major.                                       |
| `inputs`         | list of objects    | yes      | Each: `name`, `type`, `description`. `type` is JSON schema type.  |
| `required`       | list of strings    | yes      | Names of inputs that must be provided.                             |
| `returns`        | string             | yes      | JSON schema type of return value.                                  |
| `returns_schema` | object             | no       | If `returns: object`, a schema of the keys and their types.        |
| `tags`           | list of strings    | yes      | Categorization. Helps the agent decide when this skill applies.    |
| `license`        | string             | yes      | SPDX identifier. Checked by license-gate workflow.                 |

The Pydantic schema lives in `packages/skills/skill_loader.py` as `SkillFrontmatter`. The loader rejects any SKILL.md whose frontmatter fails validation, with a clear error pointing at the offending field. Don't ship broken frontmatter and expect a graceful degradation — the loader is strict.

## Body conventions

The body is for the agent to read at the moment it considers using the skill. Optimize for "an LLM scanning this for 50 tokens to decide if this is the right tool":

- **One-paragraph description first.** What this skill does, in plain language.
- **"When to use" and "When NOT to use".** Concrete, comparative. Distinguishes this skill from adjacent ones in the catalog.
- **One worked example.** Minimal `invoke(...)` call with realistic input.
- **Errors section.** Each named error code with what the agent should do.

Don't:
- Lecture on PDF format internals (the agent doesn't care; it just wants to know if and how to use the skill).
- List every possible parameter combination (the schema is in the frontmatter).
- Use marketing language.

## Where SKILL.md files live

Three valid locations, in load priority order:

1. **`packages/<package>/SKILL.md`** — first-party skills shipped with Mantle. One per package; describes the package's primary capability.
2. **`~/.mantle/skills/<name>/SKILL.md`** — user-installed skills. Loaded at gateway boot. Persisted across upgrades.
3. **`skills/` inside a session's sandbox** — task-local skills. Only available within that session. Useful for one-off tools you don't want in the global catalog.

The loader scans all three, validates each, and registers them under `/api/catalog/skills`.

## Skill testing

Every skill ships with a test in the same directory: `SKILL.md` + `test_skill.py`. The test asserts:

1. Frontmatter validates.
2. A canonical input produces a return matching `returns_schema`.
3. Each named error code is reachable from at least one input scenario.

The skills loader's own contract test (run by `make eval-codeact`) iterates every SKILL.md in the repo, invokes its `test_skill.py`, and reports per-skill pass/fail.

## Catalog vs skills

The catalog (rasputin-omnitool's 28 capabilities) is the kernel: lower-level primitives like `shell.exec`, `fs.read`, `browser.navigate`, `search.web`. Catalog tools are implemented in Python in the omnitool repo and don't have SKILL.md files — they're documented in `packages/codeact/CATALOG.md` instead.

Skills compose catalog tools. The `pdf-extract` skill probably calls `fs.write` (to save the download), `shell.exec` (to run a PDF text extractor), and `fs.read` (to load the result) under the hood. The agent sees the skill as one tool; the implementation can be many.

A good rule: if it's a stable, narrow primitive that other skills will compose, it belongs in the catalog. If it's an opinionated, task-specific composition, it belongs as a skill.

## Common authoring pitfalls

- **Vague tags.** `[utility]` is useless. `[files, pdf, ocr]` lets the agent filter the catalog meaningfully when deciding what to use.
- **Missing error codes.** If your implementation can return errors, name them. The agent will use the name when reporting back to the user; opaque exceptions confuse it.
- **Overlapping skills.** Two skills called `web-extract` and `webpage-text` doing the same thing is worse than one good skill. Consolidate.
- **License blanks.** Set `license: MIT` (or whatever you actually shipped under). The license-gate workflow blocks merges where it's missing or unrecognized.
- **Version drift.** Bump `version` on breaking changes (input/return shape). The agent caches skill metadata; a silent shape change confuses it.
