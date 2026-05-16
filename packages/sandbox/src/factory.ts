import { LocalDockerBackend } from "./docker-backend.js";
import { E2BBackend } from "./e2b-backend.js";
import type { SandboxBackend } from "./types.js";

export type SandboxBackendName = "docker" | "e2b";

export function createSandboxBackend(backend?: SandboxBackendName): SandboxBackend {
  const selected = backend ?? process.env.MANTLE_SANDBOX_BACKEND ?? "docker";
  if (selected === "docker") {
    return new LocalDockerBackend();
  }
  if (selected === "e2b") {
    return new E2BBackend();
  }
  throw new Error(`Unsupported sandbox backend: ${selected}`);
}
