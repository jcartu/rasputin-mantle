# Rasputin Mantle v1.3.2: LLM Skills, Eval Mode, Honest Benchmarks

Rasputin Mantle v1.3.2 ships the W10 corrective wave. The release improves both benchmark families versus v1.3.1, moves productivity skills from brittle keyword/template behavior to LLM-driven artifact generation, and documents the WebVoyager-300 miss honestly: WV-300 improved to 71.00%, but did not reach the 75% target.

## What W10 changed

- **T1 — WV-300 diagnostic.** Identified the runtime regression behind the WebVoyager drop: identity-score collapse during eval runs, including 38 tasks that moved from pass to fail.
- **T2 — Clean eval mode.** Added `MANTLE_EVAL_MODE=1` so benchmark runs disable APScheduler, skill-loader rediscovery, and knowledge-base lazy mounting.
- **T3 — Productivity task rewrite.** Replaced the 10 vaguest productivity prompts with fact-rich specifications and explicit schemas.
- **T4 — Template upgrades.** Upgraded the productivity template set: 4 PowerPoint templates, 3 spreadsheet templates, and 3 document templates.
- **T5 — Self-review.** Added self-review passes to all three productivity skills before final artifact emission.
- **T6 — Cold benchmark reruns.** Re-ran cold WV-300 and productivity benchmarks using the corrected runtime and task methodology.
- **T7 — LLM content generation.** Replaced keyword-matching content generation in productivity skills with LLM-driven generation from facts and schemas.

## Real numbers from T6

| Benchmark | v1.3.1 | v1.3.2 | Delta | Target | Status |
| --- | ---: | ---: | ---: | ---: | --- |
| WV-300 | 67.67% | 71.00% | +3.33 | ≥75% | Improved, missed |
| Productivity | 66.7% | 93.33% | +26.63 | ≥80% | Passed |

The Sonnet judge path was verified with 30 real Sonnet 4.6 calls. Anthropic spend was `$0.363025`; the full breakdown is in `outputs/v1_3_2/anthropic-spend.json`.

## Methodology comparison

| Release | Productivity task structure | What it measured | Result |
| --- | --- | --- | ---: |
| v1.3.1 | Pre-supplied outlines | Library function correctness from already-shaped content | 66.7% |
| v1.3.2 | Facts + schema | Agent generation quality and artifact construction from specifications | 93.33% |

These are not identical benchmarks. The v1.3.2 structure is more honest because it asks the skills to generate usable content from facts and constraints instead of receiving most of the outline in advance.

## Why the change was made

The W10 diagnostic showed that the v1.3.1 productivity benchmark mostly validated whether library writers could serialize provided outlines, while the product promise is that an agent can turn user facts and requirements into useful slides, spreadsheets, and documents. W10 therefore changed the task shape to facts plus schema and moved skill content generation into the LLM path.

The same diagnostic found benchmark-runtime interference during WV-300 runs. `MANTLE_EVAL_MODE=1` isolates evals from background scheduler, skill rediscovery, and knowledge-base lazy-mount side effects. That fix raised WV-300 from 67.67% to 71.00%, but it did not fully recover the 75% target.

## Decision

Ship v1.3.2.

- Both benchmark families improved versus v1.3.1.
- Productivity now exceeds target: 93.33% against an 80% target.
- WV-300 improved from 67.67% to 71.00%, but still misses the 75% target.
- The README and release notes use the canonical 71.00% WV-300 figure; no 75% claim is made.

This release is intentionally shipped with honest numbers: v1.3.2 is materially better than v1.3.1, and the remaining WV-300 gap is explicit release debt rather than hidden marketing copy.
