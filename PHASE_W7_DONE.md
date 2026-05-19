# Phase W7 — Productivity skills complete

## Checklist

- [x] Slides skill registered with Anthropic Agent Skills frontmatter.
- [x] Slides script produces real `.pptx` files with four starter templates, notes, images, and matplotlib chart embedding.
- [x] Spreadsheet skill registered and produces real `.xlsx` files.
- [x] Spreadsheet subskills cover financial models, comparison matrices, and data cleaning.
- [x] Financial model workbooks use openpyxl formula strings across P&L, balance sheet, and cash-flow sheets.
- [x] Document skill registered and produces `.docx` and `.pdf` files with minimal, academic, and business styles.
- [x] Artifact viewer lazy-previews `.pptx`, `.xlsx`, `.docx`, and `.pdf` artifacts and keeps downloads available.
- [x] Productivity benchmark authored with 30 single-attempt tasks and Sonnet 4.6 structural judge metadata.
- [x] Benchmark run written to `outputs/v1_3/productivity-bench.json`.
- [x] Integration tests added for slides, spreadsheet, financial formulas, document output, and skill cost tracking.

## Verification

- `uv run python -m compileall ...` — passed.
- `uv run pytest tests/integration/test_slides_skill_round_trip.py tests/integration/test_spreadsheet_skill_round_trip.py tests/integration/test_spreadsheet_financial_model_has_formulas.py tests/integration/test_document_skill_round_trip.py tests/integration/test_skill_cost_tracking.py tests/integration/test_skill_discovery.py tests/integration/test_skill_validates_against_spec.py tests/integration/test_skill_invocation_round_trip.py` — 8 passed.
- `uv run python eval/productivity/runner.py --output outputs/v1_3/productivity-bench.json` — aggregate 1.00, per-format 1.00.
- `pnpm -r --if-present run typecheck` — passed.
- `pnpm --filter web build` — passed.
- `uv run python scripts/verify-readme-claims.py` — 10 passed, 0 failed.
- LSP diagnostics on changed Python/TypeScript files — clean.
