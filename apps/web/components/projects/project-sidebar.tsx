'use client';

import * as React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { ChevronDown, ChevronRight, Folder, Plus, User } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useToast } from '@/components/ui/toast';
import { createProject, listProjects, listSessions, type ProjectInfo, type SessionInfo } from '@/lib/api';

export function ProjectSidebar() {
  const router = useRouter();
  const { toast } = useToast();
  const [projects, setProjects] = React.useState<ProjectInfo[]>([]);
  const [sessionsByProject, setSessionsByProject] = React.useState<Record<string, SessionInfo[]>>({});
  const [expanded, setExpanded] = React.useState<Set<string>>(() => new Set(['personal']));

  const load = React.useCallback(async () => {
    const [projectData, personalSessions] = await Promise.all([listProjects(), listSessions('personal')]);
    setProjects(projectData);
    const entries = await Promise.all(projectData.map(async (project) => [project.id, await listSessions(project.id)] as const));
    setSessionsByProject(Object.fromEntries([['personal', personalSessions], ...entries]));
  }, []);

  React.useEffect(() => {
    void load().catch((error) => {
      toast({ title: 'Failed to load projects', description: error instanceof Error ? error.message : 'Unknown error', variant: 'error' });
    });
  }, [load, toast]);

  const toggle = (id: string) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const addProject = async () => {
    const name = window.prompt('Project name');
    if (!name) return;
    const slug = name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || `project-${Date.now()}`;
    try {
      const project = await createProject({ name, slug });
      await load();
      router.push(`/projects/${project.id}`);
    } catch (error) {
      toast({ title: 'Failed to create project', description: error instanceof Error ? error.message : 'Unknown error', variant: 'error' });
    }
  };

  return (
    <aside style={{ height: '100%', padding: '16px', display: 'flex', flexDirection: 'column', gap: 'var(--spacing-3)' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <strong>Workspaces</strong>
        <Button size="xs" variant="ghost" onClick={addProject} aria-label="New project"><Plus size={14} /></Button>
      </div>
      <div style={{ overflow: 'auto', display: 'grid', gap: 'var(--spacing-2)' }}>
        <ProjectGroup id="personal" name="Personal" icon={<User size={14} />} expanded={expanded.has('personal')} onToggle={toggle} sessions={sessionsByProject.personal ?? []} href="/" />
        {projects.map((project) => (
          <ProjectGroup
            key={project.id}
            id={project.id}
            name={project.name}
            icon={<Folder size={14} />}
            expanded={expanded.has(project.id)}
            onToggle={toggle}
            sessions={sessionsByProject[project.id] ?? []}
            href={`/projects/${project.id}`}
            newHref={`/projects/${project.id}/new`}
          />
        ))}
      </div>
      <Button variant="secondary" onClick={addProject} iconLeft={<Plus size={14} />}>New project</Button>
    </aside>
  );
}

interface ProjectGroupProps {
  id: string;
  name: string;
  icon: React.ReactNode;
  expanded: boolean;
  onToggle: (id: string) => void;
  sessions: SessionInfo[];
  href: string;
  newHref?: string;
}

function ProjectGroup({ id, name, icon, expanded, onToggle, sessions, href, newHref }: ProjectGroupProps) {
  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-1)' }}>
        <button type="button" onClick={() => onToggle(id)} style={iconButtonStyle} aria-label={`Toggle ${name}`}>
          {expanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        </button>
        <Link href={href} style={projectLinkStyle}>{icon}<span>{name}</span></Link>
        {newHref ? <Link href={newHref} style={{ color: 'var(--color-foreground-muted)' }}><Plus size={13} /></Link> : null}
      </div>
      {expanded ? (
        <div style={{ marginLeft: 24, marginTop: 6, display: 'grid', gap: 4 }}>
          {sessions.slice(0, 5).map((session) => (
            <Link key={session.session_id} href={`/session/${session.session_id}`} style={sessionLinkStyle}>
              {new Date(session.created_at * 1000).toLocaleDateString()} · {session.status}
            </Link>
          ))}
          {sessions.length === 0 ? <span style={{ color: 'var(--color-foreground-faint)', fontSize: 'var(--text-xs)' }}>No sessions</span> : null}
        </div>
      ) : null}
    </div>
  );
}

const iconButtonStyle: React.CSSProperties = { background: 'transparent', border: 0, color: 'var(--color-foreground-muted)', cursor: 'pointer', padding: 2 };
const projectLinkStyle: React.CSSProperties = { flex: 1, display: 'flex', alignItems: 'center', gap: 8, color: 'var(--color-foreground)', textDecoration: 'none', fontSize: 'var(--text-sm)', minWidth: 0 };
const sessionLinkStyle: React.CSSProperties = { color: 'var(--color-foreground-muted)', textDecoration: 'none', fontSize: 'var(--text-xs)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' };
