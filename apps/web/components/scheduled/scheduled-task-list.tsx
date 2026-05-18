'use client';

import { CalendarClock, Pause, Pencil, Play, Trash2 } from 'lucide-react';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardBody, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { EmptyState } from '@/components/ui/empty-state';
import type { ScheduledTaskInfo } from '@/lib/api';

interface ScheduledTaskListProps {
  tasks: ScheduledTaskInfo[];
  onEditAction: (task: ScheduledTaskInfo) => void;
  onDeleteAction: (id: string) => void;
  onToggleAction: (id: string, paused: boolean) => void;
}

function formatDate(value: string | null): string {
  return value ? new Date(value).toLocaleString() : '—';
}

export function ScheduledTaskList({ tasks, onEditAction, onDeleteAction, onToggleAction }: ScheduledTaskListProps) {
  if (tasks.length === 0) {
    return (
      <EmptyState
        icon={<CalendarClock size={24} />}
        title="No scheduled tasks"
        description="Create a recurring task to run an agent prompt on a cron schedule."
      />
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
      {tasks.map((task) => (
        <Card key={task.id} className="flex h-full flex-col">
          <CardHeader>
            <div className="flex items-start justify-between gap-3">
              <CardTitle>{task.name}</CardTitle>
              <Badge variant={task.paused ? 'secondary' : 'success'}>{task.paused ? 'paused' : 'active'}</Badge>
            </div>
            <code style={{ color: 'var(--color-foreground-muted)', fontFamily: 'var(--font-mono)', fontSize: 'var(--text-xs)' }}>
              {task.cron}
            </code>
          </CardHeader>
          <CardBody className="flex-1" style={{ display: 'grid', gap: 'var(--spacing-3)' }}>
            <p style={{ color: 'var(--color-foreground-muted)', fontSize: 'var(--text-sm)' }}>{task.task_prompt}</p>
            <div style={{ color: 'var(--color-foreground-muted)', fontSize: 'var(--text-xs)' }}>
              <div>Next run: {formatDate(task.next_run_at)}</div>
              <div>Last run: {formatDate(task.last_run_at)}</div>
              <div>Runs: {task.runs_count}{task.max_runs ? ` / ${task.max_runs}` : ''}</div>
            </div>
            <div style={{ color: 'var(--color-foreground-faint)', fontSize: 'var(--text-xs)' }}>
              {task.run_history.length > 0 ? `History: ${task.run_history[0].status} at ${formatDate(task.run_history[0].ran_at)}` : 'No run history yet'}
            </div>
          </CardBody>
          <CardFooter className="flex items-center justify-between gap-2" withBorder>
            <div className="flex gap-2">
              <Button size="sm" variant="outline" iconLeft={<Pencil size={14} />} onClick={() => onEditAction(task)}>Edit</Button>
              <Button
                size="sm"
                variant="outline"
                iconLeft={task.paused ? <Play size={14} /> : <Pause size={14} />}
                onClick={() => onToggleAction(task.id, !task.paused)}
              >
                {task.paused ? 'Resume' : 'Pause'}
              </Button>
            </div>
            <Button size="sm" variant="destructive" iconLeft={<Trash2 size={14} />} onClick={() => onDeleteAction(task.id)}>
              Delete
            </Button>
          </CardFooter>
        </Card>
      ))}
    </div>
  );
}
