import { createSandboxBackend } from "@mantle/sandbox";
import type { SandboxBackend } from "@mantle/sandbox";

export interface CodeActRequest {
  code: string;
  language?: "python";
}

export interface CodeActResult {
  stdout: string;
  stderr: string;
  results: unknown[];
  files_changed: string[];
  duration_ms: number;
  exit_code: number;
}

interface FileSnapshot {
  [path: string]: string;
}

const SNAPSHOT_CODE = String.raw`
from __future__ import annotations

import hashlib
import json
from pathlib import Path

root = Path("/workspace")
snapshot: dict[str, str] = {}
for path in sorted(root.rglob("*")):
    if not path.is_file() or path.name == ".codeact_tmp.py":
        continue
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    snapshot[str(path)] = digest
print(json.dumps(snapshot, sort_keys=True))
`;

async function snapshotWorkspace(backend: SandboxBackend, sessionId: string): Promise<FileSnapshot> {
  const result = await backend.exec(sessionId, SNAPSHOT_CODE);
  if (result.exitCode !== 0) {
    throw new Error(`Failed to snapshot sandbox workspace: ${result.stderr}`);
  }
  const parsed: unknown = JSON.parse(result.stdout || "{}");
  if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
    throw new Error("Sandbox workspace snapshot was not an object");
  }

  const snapshot: FileSnapshot = {};
  for (const [path, digest] of Object.entries(parsed)) {
    if (typeof digest !== "string") {
      throw new Error(`Sandbox workspace snapshot digest for ${path} was not a string`);
    }
    snapshot[path] = digest;
  }
  return snapshot;
}

function diffSnapshots(before: FileSnapshot, after: FileSnapshot): string[] {
  const paths = new Set([...Object.keys(before), ...Object.keys(after)]);
  return [...paths].filter((path) => before[path] !== after[path]).sort();
}

function parseResults(stdout: string): unknown[] {
  const marker = "__MANTLE_RESULT__=";
  return stdout
    .split("\n")
    .filter((line) => line.startsWith(marker))
    .map((line) => JSON.parse(line.slice(marker.length)) as unknown);
}

export async function execute_code(request: CodeActRequest): Promise<CodeActResult> {
  if (request.language && request.language !== "python") {
    throw new Error(`Unsupported CodeAct language: ${request.language}`);
  }

  const backend = createSandboxBackend();
  const startedAt = Date.now();
  let sessionId: string | null = null;

  try {
    sessionId = await backend.create();
    const before = await snapshotWorkspace(backend, sessionId);
    const execResult = await backend.exec(sessionId, request.code);
    const after = await snapshotWorkspace(backend, sessionId);

    return {
      stdout: execResult.stdout,
      stderr: execResult.stderr,
      results: parseResults(execResult.stdout),
      files_changed: diffSnapshots(before, after),
      duration_ms: Date.now() - startedAt,
      exit_code: execResult.exitCode,
    };
  } finally {
    if (sessionId) {
      await backend.destroy(sessionId);
    }
  }
}
