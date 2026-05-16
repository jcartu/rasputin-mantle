# Orchestrator

## Overview

The orchestrator is the central control loop for Rasputin Mantle's build system. It manages the state machine across phases, coordinates four specialized agents (Auditor, Planner, Executor), and enforces the two-agent audit loop: plan work → execute → audit → loop until PERFECT. The orchestrator owns the state file, manages boot sequence, validates configuration, and drives the mechanical floor (pre-audit verification) before each audit cycle.

## Components

### protocol/orchestrator.py

The main orchestrator module (to be implemented) that coordinates the entire build cycle. Responsible for:
- Parsing command-line arguments and environment configuration
- Loading and validating the state file
- Instantiating and pinging all agents
- Running the main cycle loop: plan → execute → audit → decide
- Persisting state atomically after each cycle
- Handling exit codes and error conditions

### state.py

Atomic state persistence module providing crash-safe state management. The `State` class wraps a JSON state file with dict-like access and guarantees atomic writes using temporary file + fsync + atomic rename semantics. This ensures the state file is never left in a partially-written state, even if the process crashes during a save operation.

### agents/auditor.py

The Auditor agent that calls Anthropic's API for strict audit verdicts. Uses direct HTTP calls to Anthropic's API to evaluate finished work against the phase rubric. The auditor receives the full diff vs the previous phase tag, the phase rubric, and the phase-done draft. It returns a JSON verdict: either PERFECT (ship it) or PUNCH_LIST (fix these items). The auditor never participates in planning or coding.

### agents/planner.py

The Planner agent (to be implemented) that decomposes phase rubrics into executable tickets. Converts audit punch lists into fix tickets, groups related items, and emits a new ticket list for the executors. The planner bridges the auditor's feedback and the executor's work queue.

### agents/executor.py

The Executor agent (to be implemented) that performs the actual implementation work. Writes code one ticket at a time, returning unified diffs. The executor is the primary implementation agent and does not participate in audit or planning decisions.

## Boot Sequence

1. **Parse arguments** — Read command-line flags (phase, iteration, state file path, etc.)
2. **Load .env** — Load environment variables from `.env` file (ANTHROPIC_API_KEY, ANTHROPIC_MODEL, vLLM endpoints, etc.)
3. **Validate configuration** — Verify all required environment variables are set and non-empty
4. **Instantiate agents** — Create Auditor, Planner, and Executor agent instances with configured API keys and endpoints
5. **Ping agents** — Send minimal connectivity checks to each agent to verify they are reachable
6. **Load state** — Load the state file (state.json) from disk; initialize empty state if file does not exist
7. **Run cycle** — Execute the main loop: plan tickets → dispatch executors → run mechanical floor → audit → update state → persist

## Configuration

The orchestrator requires the following environment variables:

- **ANTHROPIC_API_KEY** — API key for Anthropic's API (required for Auditor)
- **ANTHROPIC_MODEL** — Model name for Auditor (e.g., `claude-opus-4`, default: `claude-opus-4`)
- **VLLM_BASE_URL** — Base URL for vLLM server (e.g., `http://localhost:8000`)
- **VLLM_PLANNER_MODEL** — Model name for Planner on vLLM (e.g., `Qwen/Qwen2.5-32B-Instruct`)
- **VLLM_EXECUTOR_MODEL** — Model name for Executor on vLLM (e.g., `Qwen/Qwen2.5-32B-Instruct`)

All variables must be set before the orchestrator boots. Missing or empty variables will cause the orchestrator to exit with code 1 (config failure).

## State

The orchestrator persists state to `state.json` with the following shape:

```json
{
  "phase": "R0",
  "cycle_count": 3,
  "last_audit_verdict": "PUNCH_LIST",
  "last_cycle_at": "2026-05-17T14:32:00Z"
}
```

**Fields:**

- **phase** — Current phase identifier (e.g., "R0", "R1", etc.)
- **cycle_count** — Number of completed cycles in the current phase
- **last_audit_verdict** — Result of the most recent audit: "PERFECT" or "PUNCH_LIST"
- **last_cycle_at** — ISO 8601 timestamp of the last completed cycle

All writes to state.json are atomic: the orchestrator writes to a temporary file, calls fsync() to ensure data is written to disk, then atomically renames the temporary file to the target path. This guarantees the state file is never left in a partially-written state.

## Exit Codes

- **0** — Success. The phase reached PERFECT verdict and was tagged.
- **1** — Configuration failure. A required environment variable is missing, empty, or invalid. Check `.env` and re-run.
- **2** — Cycle failure. An error occurred during execution, planning, or audit that could not be recovered. Check logs and state.json.

## Two-Agent Loop Reference

The orchestrator drives the two-agent audit loop described in detail in [docs/AUDIT_LOOP.md](AUDIT_LOOP.md). That document explains the feedback cycle (execute → audit → PERFECT or PUNCH_LIST), the strict-mode auditor patterns, the iteration cap, the mechanical floor, and the cost shape. The orchestrator is the dispatcher that implements that loop.
