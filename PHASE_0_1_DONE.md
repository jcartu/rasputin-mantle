# Phase 0 + Phase 1 — Completion Report

## Shipped

### Phase 0 — Repo + CI Scaffold
- [x] Monorepo initialized at `~/rasputin-mantle` with pnpm + uv workspaces
- [x] Two git submodules added:
  - `kernel/` → `jcartu/rasputin-omnitool`
  - `memory/` → `jcartu/rasputin-memory`
- [x] CI workflows committed:
  - `license-gate.yml` — runs `python -m rasputin_omnitool license-review` on PRs
  - `eval-nightly.yml` — daily cron, runs Promptfoo CodeAct suite
  - `absorb-nightly.yml` — daily cron, stub with `rasputin_omnitool bakeoff --no-external`
- [x] `AGENTS.md` at repo root (imperative style, matches rasputin-memory conventions)
- [x] `docs/SECURITY.md` — §8 checklist with Phase 0/1 status annotations
- [x] `docs/ARCHITECTURE.md` — §3 diagram + §4 rationale, marked "current intent"
- [x] `RASPUTIN_MANTLE_BUILD_PLAN.md` copied into repo
- [x] `pnpm i` clean
- [x] `uv sync` clean
- [x] Athena (frontend) agent merged into `~/.config/opencode/oh-my-openagent.jsonc`

### Phase 1 — Sandbox + CodeAct + Promptfoo
- [x] `packages/sandbox` — ComputeSDK abstraction:
  - TypeScript: `SandboxBackend` interface, LocalDockerBackend, E2BBackend, createSandboxBackend()`
  - Python: `SandboxBackend` ABC + `LocalDockerBackend` + `E2BBackend` + `create_backend()`
  - E2B stubbed behind feature flag (throws `SandboxBackendUnavailable`)
- [x] `packages/codeact` — `execute_code({code})` → `{stdout, stderr, results, files_changed, duration_ms, exit_code}`
  - TypeScript + Python implementations
  - Workspace snapshot/diff for `files_changed` detection
- [x] `eval/promptfoo/codeact.yaml` — 10 deterministic tasks:
  - **10/10 PASS** (100% pass rate, exceeds 8/10 gate)
  - Tasks: primes, csv_write, base64_decode, directory_walk, json_parse, list_sort, regex_emails, matrix_multiply, file_rename, error_handling
- [x] `infra/compose.dev.yml` — `sandbox-runtime` service boots without error

## Verification

```
$ pnpm i && uv sync && docker compose -f infra/compose.dev.yml up -d
$ pnpm test
Successes: 10
Failures: 0
Errors: 0
Pass Rate: 100.00%
```

## What Slipped

- Nothing slipped. All 8 kickoff deliverables completed.

## What Should Change Before Phase 2

1. **CI workflows need a remote repo.** Currently local-only. Push to GitHub to activate scheduled runs.
2. **E2B backend is a stub.** Phase 2 needs a real `MANTLE_E2B=1` + `E2B_API_KEY` to unblock the E2B path.
3. **TypeScript packages lack tsconfig.json.** They compile but have no strict type checking. Add `tsconfig.json` to `packages/sandbox` and `packages/codeact` before Phase 2 adds more TS code.
4. **`pnpm approve-builds` needed.** promptfoo's native deps (sharp, esbuild, better-sqlite3) need build scripts approved. Add a postinstall hook or document this step.
5. **Kernel `requires-python = ">=3.11"`** conflicts with host Python 3.14. The `uv sync` workspace handles this, but CI should pin `python-version: "3.12"` to match the kernel's tested range.

## Phase 2 Preview

Per build plan §6: Browser + Skills (Days 4–6, Hephaestus + Prometheus)
- `packages/browser`: wrap `browser-use` and `agent-browser`
- `packages/skills`: SKILL.md loader, bundle first six skills
- Gate: WebVoyager-100 nightly ≥ 60% pass rate
