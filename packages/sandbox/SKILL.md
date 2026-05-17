---
name: sandbox
description: Sandbox execution backend providing isolated code execution via Docker containers.
version: 1.0.0
author: Mantle
license: MIT
capability: sandbox_execution
platforms:
  - linux
---

This is a markdown playbook — invoke via bash, not skill_mcp()

## Overview

The `sandbox` package provides a secure, isolated execution environment for untrusted code. It abstracts container lifecycle management and exposes a simple API for code execution, file I/O, and resource cleanup.

## Core API: LocalDockerBackend

### Constructor: `create(image: str, workdir: str = "/workspace") -> LocalDockerBackend`

Creates and starts a new sandbox container.

**Parameters:**
- `image` (string): Docker image URI (default: `rasputin-mantle:sandbox-latest`)
- `workdir` (string): Working directory inside container (default: `/workspace`)

**Returns:** `LocalDockerBackend` instance with active container.

**Lifecycle:** Container is created and started immediately. Use `destroy()` to clean up.

### Method: `exec_code(code: str, language: str = "python") -> str`

Executes code inside the sandbox and returns stdout.

**Parameters:**
- `code` (string): Source code to execute
- `language` (string): Language identifier ("python", "bash", "javascript", etc.)

**Returns:** Standard output as string.

**Raises:** `SandboxError` if execution fails or times out.

**Timeout:** 30 seconds per execution (configurable).

### Method: `read(path: str) -> str`

Reads a file from the sandbox filesystem.

**Parameters:**
- `path` (string): Absolute or relative path within container

**Returns:** File contents as string.

**Raises:** `SandboxError` if file not found or unreadable.

### Method: `write(path: str, content: str) -> None`

Writes content to a file in the sandbox.

**Parameters:**
- `path` (string): Absolute or relative path within container
- `content` (string): File contents

**Behavior:** Creates parent directories if needed. Overwrites existing files.

**Raises:** `SandboxError` if write fails.

### Method: `list_files(path: str = ".") -> list[str]`

Lists files and directories in a sandbox path.

**Parameters:**
- `path` (string): Directory path (default: current working directory)

**Returns:** List of relative paths (files and directories).

**Raises:** `SandboxError` if path not found.

### Method: `destroy() -> None`

Stops and removes the sandbox container.

**Behavior:** Idempotent. Safe to call multiple times. Cleans up all resources.

**Lifecycle:** After calling `destroy()`, the instance is unusable. Create a new one with `create()`.

## Container Image

**Default Image:** `rasputin-mantle:sandbox-latest`

**Includes:**
- Python 3.11+
- Node.js 20+
- Bash shell
- Standard Unix utilities
- pip, npm package managers

**Default Workdir:** `/workspace`

**Security:**
- Runs as unprivileged user (uid 1000)
- No network access by default
- Read-only root filesystem (except /workspace)
- Resource limits: 2GB RAM, 1 CPU core

## Lifecycle Notes

1. **Creation:** `create()` starts a container immediately. Network and filesystem are isolated.
2. **Execution:** Each `exec_code()` call runs in the same container. State persists between calls.
3. **File Persistence:** Files written via `write()` persist until `destroy()` is called.
4. **Cleanup:** Always call `destroy()` when done. Containers are not automatically cleaned up.
5. **Reuse:** A single `LocalDockerBackend` instance can execute multiple code snippets.

## Example Usage

```python
from sandbox import LocalDockerBackend

# Create sandbox
backend = LocalDockerBackend.create(image="rasputin-mantle:sandbox-latest")

# Execute code
result = backend.exec_code("print('Hello from sandbox')", language="python")
print(result)  # "Hello from sandbox\n"

# Write and read files
backend.write("data.txt", "Hello, world!")
content = backend.read("data.txt")
print(content)  # "Hello, world!"

# List files
files = backend.list_files()
print(files)  # ["data.txt", ...]

# Cleanup
backend.destroy()
```

## Error Handling

All methods raise `SandboxError` with descriptive messages:
- Container creation failures
- Code execution timeouts
- File I/O errors
- Resource exhaustion
- Container not found (after destroy)
