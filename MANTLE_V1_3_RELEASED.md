# Rasputin Mantle v1.3: Projects, Skills, Integrations, Productivity

Rasputin Mantle v1.3 completes the W0-W8 wave: desktop and extension packaging, onboarding and playbooks, replay/share surfaces, project knowledge bases, Anthropic-compatible Agent Skills, Slack/email/scheduled integrations, and productivity artifact generation.

## What shipped

- W1: Tauri desktop (Mac/Win/Linux) + Chrome/Edge extension
- W2: Onboarding flow + Playbook gallery
- W3: Replay scrubber + Public share links + OG previews
- W4: Manus Projects with knowledge bases
- W5: Agent Skills standard + marketplace + 11 seed skills
- W6: Slack + Email + Scheduled tasks
- W7: Slides + Spreadsheets + Documents productivity skills

## What deferred

- Mobile dev
- Design View
- Music
- Video
- Meeting minutes
- Collab
- Cloud Computer 24/7
- SSO
- OneDrive
- Full-stack deploy
- Unlimited context

## Phase commits table

| Wave | Scope | Commit range |
| --- | --- | --- |
| W0 | v1.2 audit cleanup, protocol install, release baseline | `e4fb239..19ab4c1` |
| W1 | Desktop shell, icons, browser extension, extension artifacts | `62660b9..ed0793c` |
| W2 | Onboarding flow and playbook gallery | `6ca159b` |
| W3 | Replay scrubber, sanitized sharing, public routes, OG previews | `44fd52e..5ecb121` |
| W4 | Projects, project knowledge bases, inherited sessions, project UI | `eb0a957..0c33552` |
| W5 | Agent Skills standard, loader/API, marketplace UI, bundled skills | `31bd53b..3511bcc` |
| W6 | Slack, email, scheduled tasks, integrations UI | `c361057..e2cdecd` |
| W7 | Slides, spreadsheets, documents, previews, productivity benchmark | `e9faf95..2cda2ba` |
| W8 | Final eval artifacts, release report, tag | this release commit |

## Engineering invariants

- Productivity benchmark passed cold: aggregate `1.00`, document `1.00`, slides `1.00`, spreadsheet `1.00` in `outputs/v1_3/productivity-bench-final.json`.
- README verification passed: `scripts/verify-readme-claims.py` reported 10 passed, 0 failed, 0 vague.
- Anti-cheating source audit was cleaned for first-party code: no hardcoded `wv-` / `prod-` task ID equality checks, no first-party `best_of`, and no first-party `MockTransport` usage.
- WV-300 baseline remains the v1.1 Opus 4.6 result: 234/300 = `0.78`; the W8 cold regression was attempted but did not complete within the execution window.

## Cost summary

`outputs/v1_3/cost-summary.json` records $0 Anthropic execution spend:

| Bucket | Spend |
| --- | ---: |
| Auditor | $0 |
| Vision | $0 |
| Judge | $0 |
| Total | $0 |

All executors ran on local 27B. Opus was reserved for audit/regression only.

## Known limitations

- WV-300 regression is pending: `ANTHROPIC_API_KEY` was available and the Opus 4.6 command was started, but the run timed out after one hour with Playwright target-closed noise before producing a complete JSON result.
- `eval/webvoyager-300/tasks.yaml` could not be byte-compared to `mantle-v1.1-released` because that tag does not contain `eval/webvoyager-300/tasks.yaml`; it contains the W7/S6 outputs and `eval/webvoyager-300/run-gpt55.sh` only.
- Integration smoke pytest collected 161 items but stopped during collection on missing uv environment dependencies/modules (`mcp_host`, `requests`, `magic`, `voice`) and missing async pytest support for targeted async tests.
- The exact repository-root grep commands also see vendored dependency text under local `.venv/` and `node_modules/` when those directories are present; first-party source occurrences were removed.

## Reproduce locally

```bash
git clone --recursive https://github.com/jcartu/rasputin-mantle
cd rasputin-mantle
cp .env.example .env
$EDITOR .env

uv sync
pnpm install
docker compose -f infra/compose.dev.yml up -d

uv run python eval/productivity/runner.py --output outputs/v1_3/productivity-bench-final.json
uv run python scripts/verify-readme-claims.py
uv run python -m pytest tests/integration/ -v --tb=short
pnpm --filter web dev
```

WV-300 requires Anthropic credentials and a long enough uninterrupted browser/eval window:

```bash
uv run python eval/webvoyager-300/runner.py --planner opus-4-6 --output outputs/v1_3/webvoyager-300-regression.json
```

## Comparison with Manus 1.6

### Where Mantle still lags

- Manus still leads on always-on hosted reliability, mobile development, Design View, built-in collaboration, meeting minutes, music/video workflows, OneDrive/SSO enterprise polish, and cloud computer 24/7 availability.
- Mantle's WV-300 W8 regression needs a completed cold Opus pass before claiming a fresh no-regression number for v1.3.
- Mantle remains self-host-first, so local dependency setup quality matters more than it does in a managed SaaS.

### Where Mantle leads

- Self-hostable by design: orchestration, gateway, sandboxing, memory, skills, and UI are inspectable and replaceable.
- Open Agent Skills surface: `SKILL.md` authoring, marketplace metadata, seed skills, and save-as-skill are repo-native.
- Project knowledge bases and productivity artifacts are local-first and export real `.pptx`, `.xlsx`, `.docx`, and `.pdf` files.
- Cost posture is transparent: local 27B execution with explicit cost accounting rather than opaque SaaS billing.

## Acknowledgment

W0-W7 were executed by the 27B orchestrator. Published metrics in `outputs/v1_3/27b-orchestrator-metrics.json`:

- Model: `qwen3.6-27b`
- Drift events: `0`
- Fallback fires: `0`
- Average audit iterations: `0`
- Waves completed: W0, W1, W2, W3, W4, W5, W6, W7
- Total commits before W8: `46`
