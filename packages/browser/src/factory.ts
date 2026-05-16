import { BrowserActionError } from "./errors.js";
import { AgentBrowserBackend } from "./agent-browser-backend.js";
import { BrowserUseBackend } from "./browser-use-backend.js";
import type { BrowserBackend } from "./types.js";

export type BrowserBackendName = "agent-browser" | "browser-use";

export function createBrowserBackend(backend?: BrowserBackendName): BrowserBackend {
  const raw = backend ?? process.env.MANTLE_BROWSER_BACKEND ?? "agent-browser";
  if (raw !== "agent-browser" && raw !== "browser-use") {
    throw new BrowserActionError(`Unsupported browser backend: ${raw}`);
  }
  if (raw === "agent-browser") {
    return new AgentBrowserBackend();
  }
  return new BrowserUseBackend();
}
