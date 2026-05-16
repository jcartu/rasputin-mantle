export type SessionStatus = "active" | "completed" | "error" | "cancelled";

export interface SessionInfo {
  session_id: string;
  status: SessionStatus;
  created_at: number;
  cost_tokens: number;
  cost_dollars: number;
}

export interface ExecRequest {
  session_id: string;
  code: string;
  timeout_seconds?: number;
}

export interface ExecResult {
  stdout: string;
  stderr: string;
  exit_code: number;
  duration_ms: number;
  files_changed: string[];
  results: unknown[];
}

export interface StreamEvent {
  event_type: "token" | "plan" | "tool_call" | "error" | "complete";
  data: Record<string, unknown>;
  timestamp: number;
}
