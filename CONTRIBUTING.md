# Contributing to Rasputin Mantle

Thank you for considering a contribution. This document is the contract between you and the codebase. Read it once; it pays for itself.

## Philosophy

Rasputin Mantle exists to be **a self-hostable agent platform with no Potemkin code.** Every contribution must respect three invariants:

1. **No Potemkin routes.** A route returns real data or HTTP 501. Tests test real behaviour. No assertions that services are dead.
2. **Sandboxing is non-negotiable.** The agent never runs code on the host. Every `exec` flows through a sandbox handle.
3. **The verifier is sacred.** Pre-commit hooks and the auditor enforce phase rubrics. Don't disable, loosen, or work around them.

If you cannot meet these, your PR will not merge.

## Quick setup

```bash
git clone --recursive https://github.com/jcartu/rasputin-mantle
cd rasputin-mantle
cp .env.example .env       # fill in ANTHROPIC_API_KEY, VLLM_BASE_URL
uv sync && pnpm install
docker compose -f infra/compose.dev.yml up -d
make verify                # must be green before you start hacking
```

## How to find something useful to do

- **Issues tagged `good-first-issue`** — small, well-scoped tasks with clear acceptance criteria.
- **The honest-gaps section of [`MANTLE_V1_RELEASED.md`](MANTLE_V1_RELEASED.md)** — every gap is a roadmap item.
- **The `forbidden_patterns` lists in `protocol/phases/*.yaml`** — anything matching a forbidden pattern is a bug.

## Style — Python

- `from __future__ import annotations` on **every** `.py` file.
- `ruff` with `target-version = "py311"`, `line-length = 120`.
- `snake_case` for files, `kebab-case` for directories.
- Type hints required on public functions. Private helpers may omit.
- No top-level mutable state. No global `httpx.Client`.
- `pytest` for tests in flat `tests/`. Use `pytest-asyncio` for async tests.
- HTTP clients: `httpx`. Never `requests`. Never `urllib`.

## Style — TypeScript

- ESM modules. **No barrel exports** — they break tree-shaking.
- Strict TypeScript (`strict: true`).
- React 19 conventions: no `forwardRef`, `ref` is a regular prop.
- Tailwind v4 — class-based, no `@apply` in components.
- File names: `kebab-case.ts` for modules, `PascalCase.tsx` for components.

## Style — Rust

- Edition 2021.
- `rustfmt` defaults. `clippy` warnings are errors.
- Use `anyhow::Result` at boundaries, `thiserror` for libraries.

## Commit format

```
<scope>: <imperative summary, ≤72 chars>

<optional body explaining *why*, wrapped at 80 chars>

<optional footer with breaking changes, issue refs>
```

**Examples:**

```
gateway: enforce cost ceiling server-side

The previous middleware trusted the client-supplied x-est-cost-usd header.
Replace with server-side COST_TABLE lookup against the upstream usage.

Refs: AUDIT_2026_05_16.md #B3
```

```
browser: add loop detection to PlaywrightBackend

After 3 identical actions the agent emits body.innerText to break loops.
```

```
chore: bump playwright 1.58 → 1.60
```

## Pull request checklist

Before opening a PR:

- [ ] `make verify` is green locally
- [ ] `ruff check .` and `ruff format --check .` pass
- [ ] `pnpm typecheck` passes
- [ ] All integration tests touched by your change pass with the full `PYTHONPATH` from [`MANTLE_V1_RELEASED.md`](MANTLE_V1_RELEASED.md)
- [ ] You added a test for the new behaviour (or explained why the existing tests cover it)
- [ ] You did not modify `protocol/phases/*.yaml`, `Makefile`, or `scripts/verify-phase.sh` (unless your PR is explicitly *about* tightening the verifier — and then expect a longer review)
- [ ] No `import anthropic` outside `apps/gateway/src/gateway/model_client.py`
- [ ] No `--no-sandbox` anywhere in the diff
- [ ] No `as any`, `@ts-ignore`, or `@ts-expect-error`
- [ ] CHANGELOG.md is updated under `## [Unreleased]`

## Tests

- **Unit tests** live next to the code they cover.
- **Integration tests** live in `tests/integration/` and may require Docker.
- **Eval suites** live in `eval/<name>/` with a `runner.py` and a `tasks.yaml`.

**Never** add a test that asserts a service is unavailable. If the service should be live in the phase under test, make it live or skip the test with a clear reason.

## Reporting bugs

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.yml). Include:

- The exact command you ran
- The full traceback or HTTP response body
- Output of `git rev-parse HEAD`
- Output of `docker compose -f infra/compose.dev.yml ps` (which services were up)

## Reporting security vulnerabilities

**Do not open a public issue.** Email the maintainer or use GitHub's [private security advisory](https://github.com/jcartu/rasputin-mantle/security/advisories/new). See [SECURITY.md](SECURITY.md) for the threat model.

## License

By contributing you agree your contribution is licensed under the [MIT License](LICENSE).
