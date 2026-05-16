import { SandboxBackendUnavailable } from "./errors.js";
import type { SandboxBackend, SandboxExecResult } from "./types.js";

const E2B_STUB_MESSAGE =
  "E2B backend is stubbed for Phase 0/1. Set E2B_API_KEY and MANTLE_SANDBOX_BACKEND=e2b for Phase 2+.";

export class E2BBackend implements SandboxBackend {
  async create(): Promise<string> {
    if (process.env.MANTLE_E2B !== "1") {
      throw new SandboxBackendUnavailable(E2B_STUB_MESSAGE);
    }
    throw new SandboxBackendUnavailable(E2B_STUB_MESSAGE);
  }

  async exec(_sessionId: string, _code: string): Promise<SandboxExecResult> {
    throw new SandboxBackendUnavailable(E2B_STUB_MESSAGE);
  }

  async read(_sessionId: string, _path: string): Promise<string> {
    throw new SandboxBackendUnavailable(E2B_STUB_MESSAGE);
  }

  async write(_sessionId: string, _path: string, _data: string): Promise<void> {
    throw new SandboxBackendUnavailable(E2B_STUB_MESSAGE);
  }

  async list(_sessionId: string, _path: string): Promise<string[]> {
    throw new SandboxBackendUnavailable(E2B_STUB_MESSAGE);
  }

  async destroy(_sessionId: string): Promise<void> {
    throw new SandboxBackendUnavailable(E2B_STUB_MESSAGE);
  }
}
