export interface SkillSummary {
  name: string;
  description: string;
  when_to_use: string;
  capability: string;
  version: string;
  license: string;
  author: string;
  tags: string[];
  path: string;
  source: string;
  sha256: string;
  readme?: string;
}

export interface SkillDetail extends SkillSummary {
  readme: string;
  scripts: string[];
  templates: string[];
  examples: string[];
}

export interface SkillInvocationResult {
  skill: string;
  script: string | null;
  stdout: string;
  stderr: string;
  exit_code: number;
  duration_ms: number;
}

export interface SaveSkillRequest {
  name: string;
  description: string;
  intent_tags: string[];
  publish_publicly: boolean;
}

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

export async function listSkills(): Promise<SkillSummary[]> {
  const response = await request<{ skills: SkillSummary[] }>('/skills');
  return response.skills;
}

export async function getSkill(name: string): Promise<SkillDetail> {
  return request(`/skills/${encodeURIComponent(name)}`);
}

export async function invokeSkill(name: string, args: Record<string, unknown> = {}): Promise<SkillInvocationResult> {
  return request(`/skills/${encodeURIComponent(name)}/invoke`, {
    method: 'POST',
    body: JSON.stringify({ args }),
  });
}

export async function saveSessionAsSkill(sessionId: string, data: SaveSkillRequest): Promise<SkillSummary> {
  return request(`/sessions/${encodeURIComponent(sessionId)}/save-as-skill`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}
