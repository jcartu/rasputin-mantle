'use client';

import Link from 'next/link';
import type { CSSProperties } from 'react';
import { Folder, User } from 'lucide-react';
import type { ProjectInfo } from '@/lib/api';

interface ProjectSwitcherProps {
  projects: ProjectInfo[];
  activeProjectId?: string;
}

export function ProjectSwitcher({ projects, activeProjectId }: ProjectSwitcherProps) {
  return (
    <div style={{ display: 'grid', gap: 'var(--spacing-1)' }}>
      <Link href="/" style={itemStyle(!activeProjectId)}>
        <User size={14} />
        <span>Personal</span>
      </Link>
      {projects.map((project) => (
        <Link key={project.id} href={`/projects/${project.id}`} style={itemStyle(activeProjectId === project.id)}>
          <Folder size={14} />
          <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{project.name}</span>
        </Link>
      ))}
    </div>
  );
}

function itemStyle(active: boolean): CSSProperties {
  return {
    display: 'flex',
    alignItems: 'center',
    gap: 'var(--spacing-2)',
    padding: '8px 10px',
    borderRadius: 'var(--radius-md)',
    color: active ? 'var(--color-foreground)' : 'var(--color-foreground-muted)',
    backgroundColor: active ? 'var(--color-accent-subtle)' : 'transparent',
    textDecoration: 'none',
    fontSize: 'var(--text-sm)',
  };
}
