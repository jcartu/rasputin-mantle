export class SandboxBackendUnavailable extends Error {
  constructor(message: string) {
    super(message);
    this.name = "SandboxBackendUnavailable";
  }
}

export class SandboxExecError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "SandboxExecError";
  }
}
