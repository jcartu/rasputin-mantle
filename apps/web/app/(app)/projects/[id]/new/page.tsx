'use client';

import * as React from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { useToast } from '@/components/ui/toast';
import { createSession, getProject, type ProjectInfo } from '@/lib/api';

export default function NewProjectSessionPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const { toast } = useToast();
  const [project, setProject] = React.useState<ProjectInfo | null>(null);
  const [creating, setCreating] = React.useState(false);

  React.useEffect(() => {
    void getProject(params.id).then(setProject).catch((error) => {
      toast({ title: 'Failed to load project', description: error instanceof Error ? error.message : 'Unknown error', variant: 'error' });
    });
  }, [params.id, toast]);

  const start = async () => {
    setCreating(true);
    try {
      const session = await createSession(params.id);
      router.push(`/session/${session.session_id}`);
    } catch (error) {
      toast({ title: 'Failed to create project session', description: error instanceof Error ? error.message : 'Unknown error', variant: 'error' });
      setCreating(false);
    }
  };

  return (
    <main style={{ padding: 32, display: 'grid', gap: 16, maxWidth: 720 }}>
      <h1 style={{ fontSize: 'var(--text-3xl)', fontWeight: 700 }}>New session in {project?.name ?? 'project'}</h1>
      <p style={{ color: 'var(--color-foreground-muted)' }}>
        This session inherits the project default planner, allowed tools, prompt addendum, and read-only KB mount.
      </p>
      <Button onClick={start} disabled={creating}>{creating ? 'Creating…' : 'Create session'}</Button>
    </main>
  );
}
