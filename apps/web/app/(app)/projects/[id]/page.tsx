'use client';

import * as React from 'react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { Clock, Plus } from 'lucide-react';
import { KBFileList } from '@/components/projects/kb-file-list';
import { KBUploader } from '@/components/projects/kb-uploader';
import { ProjectSettingsForm } from '@/components/projects/project-settings-form';
import { Button } from '@/components/ui/button';
import { Card, CardBody, CardHeader } from '@/components/ui/card';
import { useToast } from '@/components/ui/toast';
import {
  deleteProjectKbFile,
  getProject,
  listProjectKb,
  listSessions,
  updateProject,
  uploadProjectKb,
  type KBFileInfo,
  type ProjectInfo,
  type ProjectInput,
  type SessionInfo,
} from '@/lib/api';

type Tab = 'sessions' | 'knowledge' | 'settings';

export default function ProjectPage() {
  const projectId = useProjectId();
  const { toast } = useToast();
  const [tab, setTab] = React.useState<Tab>('sessions');
  const [project, setProject] = React.useState<ProjectInfo | null>(null);
  const [sessions, setSessions] = React.useState<SessionInfo[]>([]);
  const [files, setFiles] = React.useState<KBFileInfo[]>([]);
  const [loading, setLoading] = React.useState(true);

  const load = React.useCallback(async () => {
    const [projectData, sessionData, fileData] = await Promise.all([
      getProject(projectId),
      listSessions(projectId),
      listProjectKb(projectId),
    ]);
    setProject(projectData);
    setSessions(sessionData.sort((a, b) => b.created_at - a.created_at));
    setFiles(fileData);
  }, [projectId]);

  React.useEffect(() => {
    setLoading(true);
    void load()
      .catch((error) => toast({ title: 'Failed to load project', description: error instanceof Error ? error.message : 'Unknown error', variant: 'error' }))
      .finally(() => setLoading(false));
  }, [load, toast]);

  if (loading || !project) {
    return <div style={{ padding: 32, color: 'var(--color-foreground-muted)' }}>Loading project…</div>;
  }

  const save = async (input: Partial<ProjectInput>) => {
    const updated = await updateProject(projectId, input);
    setProject(updated);
    toast({ title: 'Project settings saved', variant: 'success' });
  };

  const upload = async (file: File) => {
    await uploadProjectKb(projectId, file);
    setFiles(await listProjectKb(projectId));
    toast({ title: 'Knowledge file uploaded', description: file.name, variant: 'success' });
  };

  const removeFile = async (fileId: number) => {
    await deleteProjectKbFile(projectId, fileId);
    setFiles((current) => current.filter((file) => file.id !== fileId));
  };

  return (
    <main style={{ padding: 32, display: 'grid', gap: 'var(--spacing-6)' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', gap: 'var(--spacing-4)', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: 'var(--text-3xl)', fontWeight: 700 }}>{project.name}</h1>
          <p style={{ color: 'var(--color-foreground-muted)' }}>/{project.slug} · {project.visibility}</p>
        </div>
        <Link href={`/projects/${projectId}/new`}><Button iconLeft={<Plus size={16} />}>New session</Button></Link>
      </header>

      <nav style={{ display: 'flex', gap: 8, borderBottom: '1px solid var(--color-border)' }}>
        {(['sessions', 'knowledge', 'settings'] as Tab[]).map((value) => (
          <button key={value} type="button" onClick={() => setTab(value)} style={tabStyle(tab === value)}>
            {value === 'knowledge' ? 'Knowledge base' : value[0].toUpperCase() + value.slice(1)}
          </button>
        ))}
      </nav>

      {tab === 'sessions' ? <SessionsTab sessions={sessions} /> : null}
      {tab === 'knowledge' ? <KnowledgeTab files={files} onUploadAction={upload} onDelete={removeFile} /> : null}
      {tab === 'settings' ? <ProjectSettingsForm project={project} onSaveAction={save} /> : null}
    </main>
  );
}

function SessionsTab({ sessions }: { sessions: SessionInfo[] }) {
  if (sessions.length === 0) {
    return <p style={{ color: 'var(--color-foreground-muted)' }}>No sessions in this project yet.</p>;
  }
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16 }}>
      {sessions.map((session) => (
        <Link key={session.session_id} href={`/session/${session.session_id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
          <Card>
            <CardHeader style={{ display: 'flex', gap: 8, alignItems: 'center' }}><Clock size={16} /> Session</CardHeader>
            <CardBody style={{ color: 'var(--color-foreground-muted)', fontSize: 'var(--text-sm)' }}>
              <div>{new Date(session.created_at * 1000).toLocaleString()}</div>
              <div>Status: {session.status}</div>
            </CardBody>
          </Card>
        </Link>
      ))}
    </div>
  );
}

function KnowledgeTab({ files, onUploadAction, onDelete }: { files: KBFileInfo[]; onUploadAction: (file: File) => Promise<void>; onDelete: (fileId: number) => void }) {
  return <section style={{ display: 'grid', gap: 20 }}><KBUploader onUploadAction={onUploadAction} /><KBFileList files={files} onDelete={onDelete} /></section>;
}

function useProjectId(): string {
  const params = useParams<{ id: string }>();
  return params.id;
}

function tabStyle(active: boolean): React.CSSProperties {
  return {
    padding: '10px 14px',
    border: 0,
    borderBottom: active ? '2px solid var(--color-accent)' : '2px solid transparent',
    background: 'transparent',
    color: active ? 'var(--color-foreground)' : 'var(--color-foreground-muted)',
    cursor: 'pointer',
    fontWeight: 600,
  };
}
