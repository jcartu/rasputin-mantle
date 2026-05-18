'use client';

import * as React from 'react';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import type { ScheduledTaskInput } from '@/lib/api';

interface ScheduledTaskFormProps {
  initialValue?: Partial<ScheduledTaskInput>;
  saving?: boolean;
  onSubmitAction: (value: ScheduledTaskInput) => Promise<void> | void;
  onCancelAction?: () => void;
}

export function ScheduledTaskForm({ initialValue, saving = false, onSubmitAction, onCancelAction }: ScheduledTaskFormProps) {
  const [name, setName] = React.useState(initialValue?.name ?? '');
  const [taskPrompt, setTaskPrompt] = React.useState(initialValue?.task_prompt ?? '');
  const [cron, setCron] = React.useState(initialValue?.cron ?? '0 9 * * 1');
  const [startDate, setStartDate] = React.useState(initialValue?.start_date?.slice(0, 16) ?? '');
  const [endDate, setEndDate] = React.useState(initialValue?.end_date?.slice(0, 16) ?? '');
  const [maxRuns, setMaxRuns] = React.useState(initialValue?.max_runs?.toString() ?? '');

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        void onSubmitAction({
          name,
          task_prompt: taskPrompt,
          cron,
          start_date: startDate ? new Date(startDate).toISOString() : null,
          end_date: endDate ? new Date(endDate).toISOString() : null,
          max_runs: maxRuns ? Number(maxRuns) : null,
        });
      }}
      style={{ display: 'grid', gap: 'var(--spacing-4)' }}
    >
      <Input label="Name" value={name} onChange={(event) => setName(event.target.value)} required />
      <Textarea
        label="Task prompt"
        value={taskPrompt}
        onChange={(event) => setTaskPrompt(event.target.value)}
        required
      />
      <Input
        label="Cron"
        hint="Five-field cron, e.g. 0 9 * * 1"
        value={cron}
        onChange={(event) => setCron(event.target.value)}
        required
      />
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <Input label="Start date" type="datetime-local" value={startDate} onChange={(event) => setStartDate(event.target.value)} />
        <Input label="End date" type="datetime-local" value={endDate} onChange={(event) => setEndDate(event.target.value)} />
      </div>
      <Input
        label="Max runs"
        type="number"
        min={1}
        value={maxRuns}
        onChange={(event) => setMaxRuns(event.target.value)}
      />
      <div className="flex justify-end gap-2">
        {onCancelAction ? <Button type="button" variant="secondary" onClick={onCancelAction}>Cancel</Button> : null}
        <Button type="submit" loading={saving}>Save task</Button>
      </div>
    </form>
  );
}
