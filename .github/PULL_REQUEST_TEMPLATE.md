<!--
  Thank you for contributing to Rasputin Mantle.
  Fill in every section. PRs without a complete checklist will not be reviewed.
  -->

## Summary

<!-- One sentence: what does this PR change? -->



## Why

<!-- The case for the change. Link to issues, audit findings, or threads. -->

Closes #

## What changed

<!-- Bullet list of concrete edits. File-level granularity, not class/function. -->

-
-
-

## How it was tested

<!-- Exact commands and outputs. Not "I ran the tests" — show which tests, where, and what came back. -->

```
$ make verify
...

$ PYTHONPATH=apps/gateway/src:... uv run pytest tests/integration/test_<area>.py -v
...
```

## Phase / package surface

<!-- Tick every box that applies. -->

- [ ] `apps/gateway`
- [ ] `apps/web`
- [ ] `apps/desktop`
- [ ] `packages/browser`
- [ ] `packages/codeact`
- [ ] `packages/sandbox`
- [ ] `packages/skills`
- [ ] `packages/voice`
- [ ] `packages/mcp-host`
- [ ] `packages/wide-research`
- [ ] `packages/scheduler`
- [ ] `packages/shared`
- [ ] memory client (`apps/gateway/src/gateway/memory_client.py`)
- [ ] `kernel/` submodule
- [ ] `memory/` submodule
- [ ] `infra/`
- [ ] `eval/`
- [ ] `docs/`
- [ ] CI / `.github/`

## Invariant checklist

These are the **non-negotiable** rules. If your PR violates any of them, it will be sent back regardless of how clean the diff is.

- [ ] No `import anthropic` outside `apps/gateway/src/gateway/model_client.py`
- [ ] No `--no-sandbox` anywhere in the diff
- [ ] No `as any`, `@ts-ignore`, `@ts-expect-error`, or `# type: ignore` without a justifying comment
- [ ] No empty `except:` blocks
- [ ] No tests that assert services are dead
- [ ] No edits to `protocol/phases/*.yaml`, `Makefile`, or `scripts/verify-phase.sh` *unless* this PR is explicitly *about* the verifier
- [ ] Gateway routes return real data or `HTTP 501` — no Potemkin paths
- [ ] `from __future__ import annotations` on every new `.py` file
- [ ] Cost-incurring code reads `usage` from the upstream response; clients cannot self-report cost

## Documentation

- [ ] `README.md` updated if user-facing behaviour changed
- [ ] `CHANGELOG.md` updated under `## [Unreleased]`
- [ ] `docs/ARCHITECTURE.md` updated if components moved or interfaces changed
- [ ] `SECURITY.md` updated if the threat model changed
- [ ] Docstrings / TS comments updated on any changed public function

## Performance

<!-- If this PR could affect a measured number (WebVoyager, CodeAct, voice latency, memory LoCoMo, test count), record before/after. -->

| Metric | Before | After |
|---|--:|--:|
| `make verify` runtime | | |
| Integration tests passing | | |
| Other (specify) | | |

## Breaking changes

<!-- Anything a downstream consumer would need to update. Migration steps. -->

- [ ] No breaking changes
- [ ] Breaking changes documented below:

## Notes for reviewers

<!-- Anything you want a reviewer to look at first, things you're unsure about, alternative designs you considered. -->
