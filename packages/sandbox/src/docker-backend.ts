import { exec } from "node:child_process";
import { randomUUID } from "node:crypto";
import { mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { basename, dirname, join } from "node:path";
import { tmpdir } from "node:os";

import { SandboxExecError } from "./errors.js";
import type { SandboxBackend, SandboxExecResult } from "./types.js";

interface ShellResult {
  stdout: string;
  stderr: string;
  exitCode: number;
}

const EXEC_TIMEOUT_MS = 120_000;

function shellQuote(value: string): string {
  return `'${value.replace(/'/g, `'"'"'`)}'`;
}

function containerName(sessionId: string): string {
  return `mantle-sandbox-${sessionId}`;
}

function volumeName(sessionId: string): string {
  return `mantle-work-${sessionId}`;
}

async function runShell(command: string): Promise<ShellResult> {
  return new Promise((resolve) => {
    exec(command, { timeout: EXEC_TIMEOUT_MS, maxBuffer: 10 * 1024 * 1024 }, (error, stdout, stderr) => {
      if (!error) {
        resolve({ stdout, stderr, exitCode: 0 });
        return;
      }

      const exitCode = typeof error.code === "number" ? error.code : 1;
      resolve({ stdout, stderr, exitCode });
    });
  });
}

async function runRequired(command: string, message: string): Promise<ShellResult> {
  const result = await runShell(command);
  if (result.exitCode !== 0) {
    throw new SandboxExecError(`${message}: ${result.stderr || result.stdout}`.trim());
  }
  return result;
}

export class LocalDockerBackend implements SandboxBackend {
  async create(): Promise<string> {
    const sessionId = randomUUID().replace(/-/g, "").slice(0, 16);
    await runRequired(`docker volume create ${shellQuote(volumeName(sessionId))}`, "Failed to create sandbox volume");
    await runRequired(
      [
        "docker run -d",
        "--name",
        shellQuote(containerName(sessionId)),
        "--user",
        "1000:1000",
        "--memory",
        "512m",
        "--cpus",
        "1.0",
        "--security-opt",
        "no-new-privileges:true",
        "-v",
        shellQuote(`${volumeName(sessionId)}:/workspace`),
        "python:3.12-slim",
        "sleep infinity",
      ].join(" "),
      "Failed to create sandbox container",
    );
    return sessionId;
  }

  async exec(sessionId: string, code: string): Promise<SandboxExecResult> {
    const tempDir = await mkdtemp(join(tmpdir(), "mantle-codeact-"));
    const tempFile = join(tempDir, ".codeact_tmp.py");
    try {
      await writeFile(tempFile, code, "utf8");
      await runRequired(
        `docker cp ${shellQuote(tempFile)} ${shellQuote(`${containerName(sessionId)}:/workspace/.codeact_tmp.py`)}`,
        "Failed to copy code into sandbox",
      );
      const result = await runShell(
        `docker exec ${shellQuote(containerName(sessionId))} python3 /workspace/.codeact_tmp.py`,
      );
      return { stdout: result.stdout, stderr: result.stderr, exitCode: result.exitCode };
    } finally {
      await rm(tempDir, { recursive: true, force: true });
    }
  }

  async read(sessionId: string, path: string): Promise<string> {
    const tempDir = await mkdtemp(join(tmpdir(), "mantle-read-"));
    try {
      await runRequired(
        `docker cp ${shellQuote(`${containerName(sessionId)}:${path}`)} ${shellQuote(tempDir)}`,
        "Failed to copy file out of sandbox",
      );
      return await readFile(join(tempDir, basename(path)), "utf8");
    } finally {
      await rm(tempDir, { recursive: true, force: true });
    }
  }

  async write(sessionId: string, path: string, data: string): Promise<void> {
    const tempDir = await mkdtemp(join(tmpdir(), "mantle-write-"));
    const tempFile = join(tempDir, basename(path));
    try {
      await writeFile(tempFile, data, "utf8");
      await runRequired(
        `docker exec ${shellQuote(containerName(sessionId))} mkdir -p ${shellQuote(dirname(path))}`,
        "Failed to create sandbox destination directory",
      );
      await runRequired(
        `docker cp ${shellQuote(tempFile)} ${shellQuote(`${containerName(sessionId)}:${path}`)}`,
        "Failed to copy file into sandbox",
      );
    } finally {
      await rm(tempDir, { recursive: true, force: true });
    }
  }

  async list(sessionId: string, path: string): Promise<string[]> {
    const result = await runRequired(
      `docker exec ${shellQuote(containerName(sessionId))} ls ${shellQuote(path)}`,
      "Failed to list sandbox path",
    );
    return result.stdout.split("\n").map((entry) => entry.trim()).filter((entry) => entry.length > 0);
  }

  async destroy(sessionId: string): Promise<void> {
    await runShell(`docker rm -f ${shellQuote(containerName(sessionId))}`);
    await runShell(`docker volume rm ${shellQuote(volumeName(sessionId))}`);
  }
}
