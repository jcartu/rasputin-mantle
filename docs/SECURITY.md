# Security

## Threat model

Two relevant adversaries:

1. **A prompt injection in untrusted content** (web page, file, email) that tries to make the agent do something destructive or exfiltrative when it's operating tools. The sandbox isolation and the gateway's allowlists are the primary defenses.

2. **A buggy or hallucinating 27B** that writes code claiming to implement the rubric but actually does something else — most commonly, returning hardcoded data instead of calling the real service. The strict Opus auditor and the mechanical floor are the primary defenses.

The audit loop is not designed to defend against an actively malicious build agent. If you don't trust your own 27B's weights, this build pipeline isn't enough.

## Sandbox invariants

- **Per-task sandboxes.** Every session gets its own container. No shared filesystem between sessions.
- **Non-root.** UID 1000 inside the container. No `--privileged`. Docker `--security-opt no-new-privileges` set on every spawn.
- **No host network.** Sandboxes use a default bridge network. They can reach the public internet (for browsing tasks) but cannot reach host services on `127.0.0.1` by default. Specific allowlists (e.g. the gateway's tool endpoints) are routed through the gateway, not direct.
- **Chromium with sandbox enabled.** `--enable-sandbox` is implicit; the build's pre-commit hook and auditor BOTH flag any addition of `--no-sandbox` as a blocker. There is no legitimate case for `--no-sandbox` in this codebase.
- **No GPU passthrough into sandboxes.** GPU work is mediated through vLLM at the gateway level.

## Auth & secrets

- **Anthropic and vLLM keys** live only in the orchestrator container and the gateway. They're loaded from `.env` (which is gitignored). They're never written to logs (the orchestrator redacts authorization headers before logging request URLs).
- **Pre-commit hook scans for new hardcoded secrets** (basic regex; not a vault — for that, use sops or a secrets manager). Anything matching `sk-ant-[a-zA-Z0-9_-]+` or `AKIA[0-9A-Z]{16}` triggers a block.
- **Postgres/Redis credentials** are env-injected through compose, never baked into images.
- **Neko admin password** is set via `NEKO_PASSWORD_ADMIN` at compose-up. Default in `.env.example` is `mantle-admin` — change it before exposing Neko beyond localhost.

## CI gates

`.github/workflows/`:

- **`license-gate.yml`** — every PR runs `rasputin_omnitool license-review` on the dependency diff. Fails the PR if a new dep has a copyleft or unknown license. Required check.
- **`phase-verify.yml`** — runs `make verify-phase-RN` matching the most recent phase tag on every PR. Required check.
- **`eval-nightly.yml`** — cron-triggered, runs the full eval suite, posts deltas as a PR comment. Not blocking, informational.
- **`absorb-nightly.yml`** — cron-triggered, runs the mantle-absorb pipeline to pick up upstream changes in rasputin-omnitool. Opens a PR if anything changed.

## What the auditor enforces beyond the floor

- `--no-sandbox`, `eval()`/`exec()` on user input, `subprocess.run(..., shell=True)` with interpolated variables, `requests.get(verify=False)`: each is a blocker.
- Direct `anthropic` or `openai` imports outside the designated gateway client file: blocker.
- New dependencies without a license-review entry: blocker.
- Hardcoded URLs and credentials: blocker.
- Skipped/swallowed exceptions in production code paths: blocker.

These are listed in full in `protocol/prompts/auditor-strict.md` along with example fix patterns.

## Cost wall

R3 ships the cost wall:
- Per-workspace daily budget enforced server-side at the gateway.
- Cost computed from `response.usage.input_tokens` and `output_tokens` against a `COST_TABLE`, never from client headers.
- HTTP 429 returned when budget exceeded. Integration test verifies the 429 path.
- Orchestrator polls daily spend rough-estimates from its own usage tally; when over `DAILY_BUDGET_USD`, sleeps an hour and resumes. This is a soft secondary cap; the gateway's wall is the hard one.

## What this build does NOT do

- **PII redaction.** The agent will browse and read whatever you point it at. If you point it at sensitive content, it stores embeddings of that content in rasputin-memory. Don't.
- **Output classification.** The model output is not scanned for unsafe content before being returned to the user. If you're deploying Mantle to untrusted users, add a classifier in front.
- **Sandbox escape detection.** We trust Docker's isolation. If you don't, run the QNAP itself on an isolated VLAN.
- **Audit log integrity.** `audit-log/` is in git, so tampering is visible in `git log`, but the audit log itself isn't signed. Don't allow ALLOW_VERIFIER_EDIT in production main branches.
