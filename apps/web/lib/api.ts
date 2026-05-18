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
  cost_dollars?: number;
  project_id?: string | null;
  default_planner?: string | null;
  system_prompt_addendum?: string | null;
  allowed_tools?: string[] | null;
  kb_index?: string[] | null;
}

export interface ProjectInfo {
  id: string;
  name: string;
  slug: string;
  created_at: string;
  updated_at: string;
  owner_id: string;
  visibility: 'private' | 'team' | 'public';
  default_planner: string | null;
  system_prompt_addendum: string | null;
  allowed_tools: string[];
}

export interface ProjectMember {
  project_id: string;
  user_id: string;
  role: 'owner' | 'editor' | 'viewer';
  added_at: string;
}

export interface KBFileInfo {
  id: number;
  project_id: string;
  filename: string;
  mime_type: string | null;
  size_bytes: number;
  sha256: string;
  uploaded_at: string;
  storage_path: string;
}

export interface ProjectInput {
  name: string;
  slug: string;
  visibility?: 'private' | 'team' | 'public';
  default_planner?: string | null;
  system_prompt_addendum?: string | null;
  allowed_tools?: string[];
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
  if (res.status === 204) {
    return undefined as T;
  }
  return res.json();
}

// --- Sessions ---

export async function listSessions(projectId?: string): Promise<SessionInfo[]> {
  const params = projectId ? `?project_id=${encodeURIComponent(projectId)}` : '';
  return request(`/sessions${params}`);
}

export async function createSession(projectId?: string): Promise<SessionInfo> {
  return request('/sessions', {
    method: 'POST',
    body: projectId ? JSON.stringify({ project_id: projectId }) : undefined,
  });
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

// --- Projects ---

export async function listProjects(): Promise<ProjectInfo[]> {
  return request('/projects');
}

export async function createProject(data: ProjectInput): Promise<ProjectInfo> {
  return request('/projects', { method: 'POST', body: JSON.stringify(data) });
}

export async function getProject(id: string): Promise<ProjectInfo> {
  return request(`/projects/${id}`);
}

export async function updateProject(id: string, data: Partial<ProjectInput>): Promise<ProjectInfo> {
  return request(`/projects/${id}`, { method: 'PATCH', body: JSON.stringify(data) });
}

export async function deleteProject(id: string): Promise<void> {
  await request(`/projects/${id}`, { method: 'DELETE' });
}

export async function listProjectMembers(id: string): Promise<ProjectMember[]> {
  return request(`/projects/${id}/members`);
}

export async function listProjectKb(id: string): Promise<KBFileInfo[]> {
  return request(`/projects/${id}/kb`);
}

export async function uploadProjectKb(id: string, file: File): Promise<KBFileInfo> {
  const form = new FormData();
  form.append('file', file);
  const res = await fetch(`${BASE}/projects/${id}/kb`, { method: 'POST', body: form });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail?.message ?? `HTTP ${res.status}`);
  }
  return res.json();
}

export async function deleteProjectKbFile(projectId: string, fileId: number): Promise<void> {
  await request(`/projects/${projectId}/kb/${fileId}`, { method: 'DELETE' });
}

// --- Scheduled Tasks ---

export interface ScheduledRun {
  session_id: string;
  status: string;
  ran_at: string;
}

export interface ScheduledTaskInfo {
  id: string;
  name: string;
  task_prompt: string;
  cron: string;
  start_date: string | null;
  end_date: string | null;
  max_runs: number | null;
  runs_count: number;
  last_run_at: string | null;
  next_run_at: string | null;
  paused: boolean;
  created_at: string;
  updated_at: string;
  run_history: ScheduledRun[];
}

export interface ScheduledTaskInput {
  name: string;
  task_prompt: string;
  cron: string;
  start_date?: string | null;
  end_date?: string | null;
  max_runs?: number | null;
}

export async function listScheduledTasks(): Promise<ScheduledTaskInfo[]> {
  return request('/scheduled');
}

export async function createScheduledTask(data: ScheduledTaskInput): Promise<ScheduledTaskInfo> {
  return request('/scheduled', { method: 'POST', body: JSON.stringify(data) });
}

export async function updateScheduledTask(
  id: string,
  data: Partial<ScheduledTaskInput> & { paused?: boolean },
): Promise<ScheduledTaskInfo> {
  return request(`/scheduled/${id}`, { method: 'PATCH', body: JSON.stringify(data) });
}

export async function deleteScheduledTask(id: string): Promise<{ deleted: string }> {
  return request(`/scheduled/${id}`, { method: 'DELETE' });
}

// --- Integrations ---

export interface SlackIntegrationStatus {
  configured: boolean;
  connected: boolean;
  team_name: string | null;
}

export interface MailIntegrationStatus {
  inbound_configured: boolean;
  outbound_configured: boolean;
  allowed_senders: string[];
}

export async function getSlackIntegrationStatus(): Promise<SlackIntegrationStatus> {
  return request('/slack/status');
}

export async function disconnectSlackIntegration(): Promise<{ disconnected: boolean }> {
  return request('/slack/disconnect', { method: 'DELETE' });
}

export async function getMailIntegrationStatus(): Promise<MailIntegrationStatus> {
  return request('/mail/status');
}
