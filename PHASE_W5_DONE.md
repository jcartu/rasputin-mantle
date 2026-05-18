# Phase W5 Done — Agent Skills standard + marketplace

## Completion checklist

- [x] Documented Agent Skills standard in `docs/AGENT_SKILLS_SPEC.md`.
- [x] Added `packages/codeact/codeact/skills_loader.py` with discovery, validation, per-session cache invalidation, detail, invocation, and save-as-skill support.
- [x] Exposed backend routes for `GET /api/skills`, `GET /api/skills/{name}`, `POST /api/skills/{name}/invoke`, and `POST /api/sessions/{session_id}/save-as-skill`.
- [x] Created 8 seed skills under `packages/skills/`, each with valid `SKILL.md` frontmatter and at least one script.
- [x] Added marketplace route, skill detail route, and skill components in `apps/web/`.
- [x] Added integration coverage for discovery, spec validation, invocation, and save-as-skill round trip.

## Verification

- `uv run python packages/codeact/codeact/skills_loader.py --list`
- `uv run pytest tests/integration/test_skill_discovery.py tests/integration/test_skill_validates_against_spec.py tests/integration/test_skill_invocation_round_trip.py tests/integration/test_save_as_skill.py`
- `pnpm --filter web build`
