export interface SandboxBackend {
  create(): Promise<string>;
  exec(sessionId: string, code: string): Promise<SandboxExecResult>;
  read(sessionId: string, path: string): Promise<string>;
  write(sessionId: string, path: string, data: string): Promise<void>;
  list(sessionId: string, path: string): Promise<string[]>;
  destroy(sessionId: string): Promise<void>;
}

export interface SandboxExecResult {
  stdout: string;
  stderr: string;
  exitCode: number;
}
