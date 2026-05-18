'use client';

import * as React from 'react';
import { CalendarClock, Plus } from 'lucide-react';

import { ScheduledTaskForm } from '@/components/scheduled/scheduled-task-form';
import { ScheduledTaskList } from '@/components/scheduled/scheduled-task-list';
import { Button } from '@/components/ui/button';
import Dialog from '@/components/ui/dialog';
import { EmptyState } from '@/components/ui/empty-state';
import { Skeleton } from '@/components/ui/skeleton';
import { useToast } from '@/components/ui/toast';
import {
  createScheduledTask,
  deleteScheduledTask,
  listScheduledTasks,
  updateScheduledTask,
  type ScheduledTaskInfo,
  type ScheduledTaskInput,
} from '@/lib/api';

export default function ScheduledPage() {
  const [tasks, setTasks] = React.useState<ScheduledTaskInfo[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [saving, setSaving] = React.useState(false);
  const [dialogOpen, setDialogOpen] = React.useState(false);
  const [editing, setEditing] = React.useState<ScheduledTaskInfo | null>(null);
  const { toast } = useToast();

  const refresh = React.useCallback(async () => {
    const nextTasks = await listScheduledTasks();
    setTasks(nextTasks);
  }, []);

  React.useEffect(() => {
    refresh()
      .catch((error) => toast({ title: 'Failed to load scheduled tasks', description: error instanceof Error ? error.message : 'Unknown error', variant: 'destructive' }))
      .finally(() => setLoading(false));
  }, [refresh, toast]);

  async function handleSubmit(value: ScheduledTaskInput) {
    setSaving(true);
    try {
      if (editing) {
        const updated = await updateScheduledTask(editing.id, value);
        setTasks((current) => current.map((task) => (task.id === updated.id ? updated : task)));
        toast({ title: 'Scheduled task updated', variant: 'success' });
      } else {
        const created = await createScheduledTask(value);
        setTasks((current) => [created, ...current]);
        toast({ title: 'Scheduled task created', variant: 'success' });
      }
      setDialogOpen(false);
      setEditing(null);
    } catch (error) {
      toast({ title: 'Failed to save scheduled task', description: error instanceof Error ? error.message : 'Unknown error', variant: 'destructive' });
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(id: string) {
    try {
      await deleteScheduledTask(id);
      setTasks((current) => current.filter((task) => task.id !== id));
      toast({ title: 'Scheduled task deleted', variant: 'success' });
    } catch (error) {
      toast({ title: 'Failed to delete scheduled task', description: error instanceof Error ? error.message : 'Unknown error', variant: 'destructive' });
    }
  }

  async function handleToggle(id: string, paused: boolean) {
    try {
      const updated = await updateScheduledTask(id, { paused });
      setTasks((current) => current.map((task) => (task.id === id ? updated : task)));
      toast({ title: paused ? 'Scheduled task paused' : 'Scheduled task resumed', variant: 'success' });
    } catch (error) {
      toast({ title: 'Failed to update scheduled task', description: error instanceof Error ? error.message : 'Unknown error', variant: 'destructive' });
    }
  }

  return (
    <div className="container space-y-8 py-8">
      <div className="flex items-center justify-between gap-4">
        <div className="space-y-2">
          <h1 className="text-3xl font-bold tracking-tight">Scheduled tasks</h1>
          <p style={{ color: 'var(--color-foreground-muted)' }}>Run recurring agent prompts with cron, run limits, and history.</p>
        </div>
        <Button iconLeft={<Plus size={16} />} onClick={() => { setEditing(null); setDialogOpen(true); }}>New task</Button>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 3 }).map((_, index) => <Skeleton key={index} height={220} />)}
        </div>
      ) : tasks.length === 0 ? (
        <EmptyState
          icon={<CalendarClock size={24} />}
          title="No scheduled tasks"
          description="Create a recurring task to run an agent prompt on a cron schedule."
          action={<Button onClick={() => setDialogOpen(true)}>Create task</Button>}
        />
      ) : (
        <ScheduledTaskList
          tasks={tasks}
          onEditAction={(task) => { setEditing(task); setDialogOpen(true); }}
          onDeleteAction={(id) => { void handleDelete(id); }}
          onToggleAction={(id, paused) => { void handleToggle(id, paused); }}
        />
      )}

      <Dialog
        isOpen={dialogOpen}
        onClose={() => { setDialogOpen(false); setEditing(null); }}
        title={editing ? 'Edit scheduled task' : 'Create scheduled task'}
        size="lg"
      >
        <ScheduledTaskForm
          saving={saving}
          initialValue={editing ?? undefined}
          onSubmitAction={handleSubmit}
          onCancelAction={() => { setDialogOpen(false); setEditing(null); }}
        />
      </Dialog>
    </div>
  );
}
