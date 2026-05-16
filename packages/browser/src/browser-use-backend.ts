import { spawn } from "node:child_process";

import { BrowserActionError, BrowserNotAvailable } from "./errors.js";
import type { BrowserBackend, BrowserElement, BrowserState } from "./types.js";

const COMMAND_TIMEOUT_MS = 30_000;
const ELEMENT_LINE_RE = /^\s*\[(\d+)]\s+([^\s]+)(?:\s+"([^"]*)")?/;
const URL_LINE_RE = /^\s*(?:url|current url|page url):\s*(\S+)/i;

interface CommandResult {
  stdout: string;
  stderr: string;
}

function runBrowserUse(args: string[]): Promise<CommandResult> {
  return new Promise((resolve, reject) => {
    const child = spawn("browser-use", args, { stdio: ["ignore", "pipe", "pipe"] });
    const stdoutChunks: Buffer[] = [];
    const stderrChunks: Buffer[] = [];

    const timeout = setTimeout(() => {
      child.kill("SIGTERM");
      reject(new BrowserActionError(`browser-use ${args.join(" ")} timed out after 30s`));
    }, COMMAND_TIMEOUT_MS);

    child.stdout.on("data", (chunk: Buffer) => stdoutChunks.push(chunk));
    child.stderr.on("data", (chunk: Buffer) => stderrChunks.push(chunk));
    child.on("error", (error: NodeJS.ErrnoException) => {
      clearTimeout(timeout);
      if (error.code === "ENOENT") {
        reject(new BrowserNotAvailable("browser-use CLI is not available on PATH"));
        return;
      }
      reject(new BrowserActionError(error.message));
    });
    child.on("close", (code) => {
      clearTimeout(timeout);
      const stdout = Buffer.concat(stdoutChunks).toString("utf-8");
      const stderr = Buffer.concat(stderrChunks).toString("utf-8");
      if (code !== 0) {
        reject(new BrowserActionError((stderr || stdout || `browser-use exited with code ${code}`).trim()));
        return;
      }
      resolve({ stdout, stderr });
    });
  });
}

function parseState(stdout: string): BrowserState {
  const elements: BrowserElement[] = [];
  let url = "";

  for (const line of stdout.split("\n")) {
    const urlMatch = URL_LINE_RE.exec(line);
    if (urlMatch?.[1] !== undefined) {
      url = urlMatch[1];
      continue;
    }

    const match = ELEMENT_LINE_RE.exec(line);
    if (match?.[1] === undefined || match[2] === undefined) {
      continue;
    }
    elements.push({ id: match[1], role: match[2], text: match[3] });
  }

  return { url, elements };
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

export class BrowserUseBackend implements BrowserBackend {
  async open(url: string): Promise<void> {
    await runBrowserUse(["open", url]);
  }

  async getState(): Promise<BrowserState> {
    const result = await runBrowserUse(["state"]);
    return parseState(result.stdout);
  }

  async click(elementId: string): Promise<void> {
    await runBrowserUse(["click", elementId]);
  }

  async type(elementId: string, text: string): Promise<void> {
    await runBrowserUse(["input", elementId, text]);
  }

  async evaluate(script: string): Promise<unknown> {
    const result = await runBrowserUse(["eval", script]);
    return parseEval(result.stdout);
  }

  async close(): Promise<void> {
    await runBrowserUse(["close"]);
  }
}
