export interface Playbook {
  id: string;
  title: string;
  description: string;
  intent: string;
  prompt_template: string;
  created_by: string;
  created_at: string;
}

export interface SavePlaybookRequest {
  session_id: string;
  title: string;
  description: string;
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

export async function listPlaybooks(): Promise<Playbook[]> {
  return request('/playbooks');
}

export async function getPlaybook(id: string): Promise<Playbook> {
  return request(`/playbooks/${id}`);
}

export async function savePlaybook(data: SavePlaybookRequest): Promise<Playbook> {
  return request('/playbooks', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}
