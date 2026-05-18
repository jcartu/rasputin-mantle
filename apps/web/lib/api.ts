/**
 * Typed API client for Rasputin Mantle gateway endpoints.
 * Uses fetch with proper typing. No Zod dependency — uses native TS interfaces.
 */

// --- Session Events ---

export type EventType =
  | 'token'
  | 'tool_call'
  | 'reasoning'
  | 'file_touch'
  | 'screenshot'
  | 'error'
  | 'completion'
  | 'heartbeat';

export interface StreamEvent {
  event_type: EventType;
  data: Record<string, unknown>;
  timestamp: number;
}

export interface SessionInfo {
  session_id: string;
  status: string;
  created_at: number;
  sandbox_id: string | null;
}

export interface ExecRequest {
  session_id: string;
  code: string;
}

export interface ExecResult {
  stdout: string;
  stderr: string;
  exit_code: number;
  duration_ms: number;
  files_changed: string[];
  results: unknown[];
}

// --- Sandbox Files ---

export interface SandboxFile {
  name: string;
  type: 'file' | 'directory';
  size: number;
  mime: string | null;
}

export interface FileContent {
  content: string;
  mime: string;
  size: number;
}

// --- Sandbox Watch ---

export interface FileChangeEvent {
  type: 'file_changed' | 'file_deleted' | 'file_created';
  path: string;
  timestamp: number;
}

// --- Neko ---

export interface NekoSession {
  url: string;
  status: 'running' | 'starting';
}

// --- Helpers ---

const BASE = '/api';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail?.message ?? `HTTP ${res.status}`);
  }
  return res.json();
}

// --- Sessions ---

export async function listSessions(): Promise<SessionInfo[]> {
  return request('/sessions');
}

export async function createSession(): Promise<SessionInfo> {
  return request('/sessions', { method: 'POST' });
}

export async function getSession(id: string): Promise<SessionInfo> {
  return request(`/sessions/${id}`);
}

export async function deleteSession(id: string): Promise<{ status: string }> {
  return request(`/sessions/${id}`, { method: 'DELETE' });
}

export async function execCode(id: string, code: string): Promise<ExecResult> {
  return request(`/sessions/${id}/exec`, {
    method: 'POST',
    body: JSON.stringify({ session_id: id, code }),
  });
}

export function streamSession(id: string): EventSource {
  return new EventSource(`/api/sessions/${id}/stream`);
}

// --- Sandbox Files ---

export async function listFiles(
  sessionId: string,
  path: string = '/',
): Promise<SandboxFile[]> {
  const params = path !== '/' ? `?path=${encodeURIComponent(path)}` : '';
  return request(`/sandbox/${sessionId}/files${params}`);
}

export async function getFile(
  sessionId: string,
  filePath: string,
): Promise<FileContent> {
  return request(`/sandbox/${sessionId}/files/${encodeURIComponent(filePath)}`);
}

// --- Sandbox Watch ---

export function watchFiles(sessionId: string): EventSource {
  return new EventSource(`/api/sandbox/${sessionId}/watch`);
}

// --- Neko ---

export async function getNekoSession(sessionId: string): Promise<NekoSession> {
  return request(`/sessions/${sessionId}/neko`, { method: 'POST' });
}
