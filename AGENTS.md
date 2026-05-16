# AGENTS.md — Rasputin Mantle

> Sisyphus, read `RASPUTIN_MANTLE_BUILD_PLAN.md` in full before planning. This file. This is the short version.

## Project Structure

```
rasputin-mantle/
├── apps/gateway/          # FastAPI server, the only thing /web talks to
├── apps/web/              # Next.js 15 frontend (Phase 4)
├── packages/sandbox/      # ComputeSDK abstraction + Neko wiring
├── packages/codeact/      # CodeAct executor + tool-as-Python shim
├── packages/browser/      # browser-use + agent-browser wrappers (Phase 2)
├── packages/skills/       # SKILL.md loader, marketplace manifest (Phase 2)
├── kernel/                # GIT SUBMODULE → rasputin-omnitool
├── memory/                # GIT SUBMODULE → rasputin-memory
├── eval/promptfoo/        # Promptfoo eval suites
├── infra/                 # Docker compose, sandbox images
└── docs/                  # ARCHITECTURE.md, SECURITY.md, SKILL_AUTHORING.md
```

## Key Invariants

- **Everything self-hostable.** No required SaaS. Cloud APIs are swappable backends.
- **License-clean.** Every dependency goes through `rasputin_omnitool license-review` before merge.
- **CodeAct sandboxing is non-negotiable.** The agent never executes code on the host. Every `exec` flows through a sandbox handle.
- **No agent loops without Langfuse traces and Promptfoo evals.**
- **Reversible by default.** Any tool that mutates state outside the sandbox requires `confirm: true`.
- **Cost ceiling enforcement.** Every session has a hard token-and-dollar ceiling.
- **Gateway binds 127.0.0.1** unless `MANTLE_PUBLIC=true`.
- **No `--no-sandbox` on Chromium.** Ever.

## Configuration

Monorepo managed by pnpm (TypeScript) and uv (Python). See root `pyproject.toml` and `pnpm-workspace.yaml`.

## Running

```bash
pnpm i && uv sync
docker compose -f infra/compose.dev.yml up -d
```

## Testing

```bash
pnpm test
```

## Code Style

- Python: `from __future__ import annotations` on every `.py` file.
- ruff: `target-version = "py311"`, `line-length = 120`.
- snake_case for Python files, kebab-case for directories.
- MIT license, no per-file SPDX headers.
- pytest for tests, flat `tests/` directory.
- TypeScript: ESM modules, no barrel exports.
