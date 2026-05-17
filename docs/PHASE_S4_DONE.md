# Phase S4 — VLM Screenshot Reasoning (Hybrid DOM/Vision Fallback)

## Status: SHIPPED

## What Was Built

### 1. VisionAssist Module (`packages/browser/browser/vision.py`)
- VLM-powered screenshot reasoning using Claude Sonnet 4.6
- Three methods: `find_element_bbox()`, `extract_text_from_region()`, `answer_question_about_page()`
- Per-task budget cap (3 calls max) with `VisionBudgetExceeded` exception
- Result caching by `sha256(screenshot + prompt)`
- Cost telemetry (`get_cost_report()`)

### 2. Hybrid DOM→Vision Fallback (`packages/browser/browser/playwright_backend.py`)
- `PlaywrightBackend._get_state()` now triggers vision fallback when DOM extraction returns empty
- Vision-sourced elements get `source="vision"`, `bbox={x,y,w,h}`, `id="vision-N"`
- Graceful degradation: vision budget exceeded or API failure → returns empty state (no crash)
- `reset_vision_task()` and `get_vision_cost_report()` public methods

### 3. BrowserElement Extended (`packages/browser/browser/types.py`)
- `bbox: dict[str, int] | None` — pixel coordinates from vision fallback
- `source: str` — `"dom"` (default) or `"vision"`

### 4. Factory Updated (`packages/browser/browser/factory.py`)
- `create_browser_backend()` accepts `vision_api_key` parameter
- Falls back to `ANTHROPIC_API_KEY` env var when not provided

### 5. Integration Tests (`tests/integration/test_hybrid_vision_fallback.py`)
- 11 tests covering:
  - Vision NOT called when DOM has elements
  - Vision called when DOM empty
  - Vision budget exceeded → graceful empty state
  - Vision API failure → graceful empty state
  - Vision disabled when no API key
  - Non-list vision result → graceful empty state
  - `reset_vision_task()` and `get_vision_cost_report()`
  - Factory vision key passing (explicit + env var)

## Test Results
- 26/26 vision + hybrid tests PASS
- LSP diagnostics: CLEAN (0 errors, 0 warnings)

## Files Changed
- `packages/browser/browser/types.py` — added `bbox`, `source` fields
- `packages/browser/browser/playwright_backend.py` — hybrid fallback wiring, `_vision_fallback()`, `reset_vision_task()`, `get_vision_cost_report()`
- `packages/browser/browser/factory.py` — `vision_api_key` parameter
- `tests/integration/test_hybrid_vision_fallback.py` — 11 new tests

## Known Limitations
- Vision fallback only triggers on empty DOM (not low-confidence DOM)
- No click support for vision-sourced elements (bbox-based click not implemented)
- Requires `ANTHROPIC_API_KEY` or explicit `vision_api_key` to function
