import { spawn } from "node:child_process";

import { BrowserActionError, BrowserNotAvailable } from "./errors.js";
import type { BrowserBackend, BrowserElement, BrowserState } from "./types.js";

const COMMAND_TIMEOUT_MS = 30_000;
const SIGKILL_GRACE_MS = 2_000;

interface CommandResult {
  stdout: string;
  stderr: string;
}

function runAgentBrowser(args: string[]): Promise<CommandResult> {
  return new Promise((resolve, reject) => {
    const child = spawn("agent-browser", args, { stdio: ["ignore", "pipe", "pipe"] });
    const stdoutChunks: Buffer[] = [];
    const stderrChunks: Buffer[] = [];
    let settled = false;

    const timeout = setTimeout(() => {
      if (settled) return;
      settled = true;
      child.kill("SIGTERM");
      setTimeout(() => { try { child.kill("SIGKILL"); } catch {} }, SIGKILL_GRACE_MS);
      reject(new BrowserActionError(`agent-browser ${args.join(" ")} timed out after ${COMMAND_TIMEOUT_MS / 1000}s`));
    }, COMMAND_TIMEOUT_MS);

    child.stdout.on("data", (chunk: Buffer) => stdoutChunks.push(chunk));
    child.stderr.on("data", (chunk: Buffer) => stderrChunks.push(chunk));
    child.on("error", (error: NodeJS.ErrnoException) => {
      clearTimeout(timeout);
      if (settled) return;
      settled = true;
      if (error.code === "ENOENT") {
        reject(new BrowserNotAvailable("agent-browser CLI is not available on PATH"));
        return;
      }
      reject(new BrowserActionError(error.message));
    });
    child.on("close", (code) => {
      clearTimeout(timeout);
      if (settled) return;
      settled = true;
      const stdout = Buffer.concat(stdoutChunks).toString("utf-8");
      const stderr = Buffer.concat(stderrChunks).toString("utf-8");
      if (code !== 0) {
        reject(new BrowserActionError((stderr || stdout || `agent-browser exited with code ${code}`).trim()));
        return;
      }
      resolve({ stdout, stderr });
    });
  });
}

function maybeString(value: unknown): string | undefined {
  return typeof value === "string" && value.length > 0 ? value : undefined;
}

function readStringField(value: Record<string, unknown>, keys: string[]): string | undefined {
  for (const key of keys) {
    const field = maybeString(value[key]);
    if (field !== undefined) {
      return field;
    }
  }
  return undefined;
}

function collectAttributes(value: Record<string, unknown>): Record<string, string> | undefined {
  const raw = value.attributes;
  if (raw === null || typeof raw !== "object" || Array.isArray(raw)) {
    return undefined;
  }
  const attributes: Record<string, string> = {};
  for (const [key, attrValue] of Object.entries(raw as Record<string, unknown>)) {
    if (typeof attrValue === "string") {
      attributes[key] = attrValue;
    }
  }
  return Object.keys(attributes).length > 0 ? attributes : undefined;
}

function collectElements(value: unknown, elements: BrowserElement[], seen: Set<string>, depth: number = 0): void {
  if (depth > 100) return;
  if (Array.isArray(value)) {
    for (const item of value) {
      collectElements(item, elements, seen, depth + 1);
    }
    return;
  }
  if (value === null || typeof value !== "object") {
    return;
  }

  const node = value as Record<string, unknown>;
  const id = readStringField(node, ["ref", "id"]);
  if (id !== undefined && id.startsWith("@") && !seen.has(id)) {
    seen.add(id);
    const role = readStringField(node, ["role", "type", "tag"]) ?? "unknown";
    const text = readStringField(node, ["text", "name", "label", "value"]);
    elements.push({ id, role, text, attributes: collectAttributes(node) });
  }

  for (const child of Object.values(node)) {
    collectElements(child, elements, seen, depth + 1);
  }
}

function readUrl(value: unknown): string {
  if (Array.isArray(value)) {
    for (const item of value) {
      const url = readUrl(item);
      if (url.length > 0) {
        return url;
      }
    }
    return "";
  }
  if (value === null || typeof value !== "object") {
    return "";
  }
  const node = value as Record<string, unknown>;
  const url = readStringField(node, ["url", "currentUrl", "pageUrl"]);
  if (url !== undefined) {
    return url;
  }
  for (const child of Object.values(node)) {
    const childUrl = readUrl(child);
    if (childUrl.length > 0) {
      return childUrl;
    }
  }
  return "";
}

function parseSnapshot(stdout: string): BrowserState {
  const parsed: unknown = JSON.parse(stdout);
  const elements: BrowserElement[] = [];
  collectElements(parsed, elements, new Set<string>());
  return { url: readUrl(parsed), elements };
}

function parseEval(stdout: string): unknown {
  const trimmed = stdout.trim();
  if (trimmed.length === 0) {
    return undefined;
  }
  try {
    return JSON.parse(trimmed);
  } catch {
    return trimmed;
  }
}

export class AgentBrowserBackend implements BrowserBackend {
  async open(url: string): Promise<void> {
    await runAgentBrowser(["open", "--", url]);
  }

  async getState(): Promise<BrowserState> {
    const result = await runAgentBrowser(["snapshot", "-i", "--json"]);
    try {
      return parseSnapshot(result.stdout);
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      throw new BrowserActionError(`Failed to parse agent-browser snapshot: ${message}`);
    }
  }

  async click(elementId: string): Promise<void> {
    await runAgentBrowser(["click", "--", elementId]);
  }

  async type(elementId: string, text: string): Promise<void> {
    await runAgentBrowser(["fill", "--", elementId, text]);
  }

  async evaluate(script: string): Promise<unknown> {
    const result = await runAgentBrowser(["eval", "--", script]);
    return parseEval(result.stdout);
  }

  async close(): Promise<void> {
    await runAgentBrowser(["close"]);
  }
}
