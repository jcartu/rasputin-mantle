slug: 001-state-module
package: protocol
goal: Create protocol/state.py with atomic fsync+rename state persistence
files_in_scope:
  - protocol/state.py
verify: "python -c 'from protocol.state import State; s=State(\"/tmp/test-state.json\"); s.set(\"phase\",\"R0\"); s.save(); s2=State(\"/tmp/test-state.json\"); s2.load(); assert s2.get(\"phase\")==\"R0\"'"
wall_clock_minutes: 15
body: |
  Create protocol/state.py implementing a State class for managing orchestrator state with crash-safe persistence.

  Requirements:
  - Class `State(path: str)` — wraps a JSON state file at the given path
  - Methods: `load()`, `save()`, `get(key, default=None)`, `set(key, value)`, `update(dict)`, `to_dict()`
  - `save()` MUST be atomic: write to `{path}.tmp`, call `os.fsync()` on the file descriptor, then `os.replace(tmp, path)`. This prevents corruption on crash mid-write.
  - `load()` reads the JSON file; if missing, initializes empty dict (no error)
  - State should track at minimum: `phase`, `cycle_count`, `last_audit_verdict`, `last_cycle_at` (ISO timestamp)
  - Use only stdlib: `json`, `os`, `pathlib`, `datetime`
  - Include type hints throughout
  - Include a module docstring explaining the atomic write guarantee
  - Add `__repr__` for debugging

  Do NOT add any external dependencies. Do NOT import from other protocol/ modules (state is a leaf module).
