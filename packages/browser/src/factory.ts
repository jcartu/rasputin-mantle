import { AgentBrowserBackend } from "./agent-browser-backend.js";
import { BrowserUseBackend } from "./browser-use-backend.js";
import type { BrowserBackend } from "./types.js";

export type BrowserBackendName = "agent-browser" | "browser-use";

export function createBrowserBackend(backend?: BrowserBackendName): BrowserBackend {
  const selected = backend ?? process.env.MANTLE_BROWSER_BACKEND ?? "agent-browser";
  if (selected === "agent-browser") {
    return new AgentBrowserBackend();
  }
  if (selected === "browser-use") {
    return new BrowserUseBackend();
  }
  throw new Error(`Unsupported browser backend: ${selected}`);
}
