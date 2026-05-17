# Phase R6: Voice, MCP, Desktop, Release

## Status

R6 shipped the final integration surface: voice clients, MCP host, desktop shell, GAIA-mini eval harness, and release documentation.

## Files Created

- `packages/voice/voice/__init__.py`
- `packages/voice/voice/stt.py`
- `packages/voice/voice/tts.py`
- `packages/voice/voice/eval_latency.py`
- `packages/voice/pyproject.toml`
- `packages/mcp-host/mcp_host/__init__.py`
- `packages/mcp-host/mcp_host/host.py`
- `packages/mcp-host/pyproject.toml`
- `apps/desktop/src-tauri/tauri.conf.json`
- `apps/desktop/src-tauri/Cargo.toml`
- `apps/desktop/src-tauri/src/main.rs`
- `apps/desktop/src/main.tsx`
- `apps/desktop/index.html`
- `apps/desktop/package.json`
- `apps/desktop/README.md`
- `eval/gaia-mini/runner.py`
- `eval/gaia-mini/tasks.yaml`
- `tests/integration/test_voice_round_trip.py`
- `tests/integration/test_mcp_host_handshake.py`
- `tests/integration/test_desktop_launch.py`
- `PHASE_R6_DONE.md`
- `MANTLE_V1_RELEASED.md`

## Verification Results

- LSP diagnostics: clean on `packages/voice/voice`, `packages/mcp-host/mcp_host`, `eval/gaia-mini`, and the three new integration test files.
- Targeted R6 integration command:

```bash
PYTHONPATH=apps/gateway/src:packages/browser:packages/sandbox:packages/shared:packages/codeact:packages/skills:packages/wide-research:packages/scheduler:packages/voice:packages/mcp-host python3 -m pytest tests/integration/test_voice_round_trip.py tests/integration/test_mcp_host_handshake.py tests/integration/test_desktop_launch.py -v
```

Result: **4 passed in 0.13s**.

## Honest Gaps

- Faster-Whisper and Kokoro services were not proven live on `127.0.0.1:8803` / `127.0.0.1:8804`; clients raise explicit availability exceptions when unreachable.
- Voice latency p50/p95 are unavailable until those services are running.
- GAIA-mini is an eval harness and 20-task set; no judged pass rate was produced in this run because no Anthropic judge run was executed.
- Desktop is a Tauri 2 skeleton with React chat and `MediaRecorder` mic fallback; it was not compiled in this phase.
