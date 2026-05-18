'use client';

import * as React from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import Select from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import type { ProjectInfo, ProjectInput } from '@/lib/api';

const PLANNERS = [
  { value: '', label: 'No default' },
  { value: 'gpt-5.5', label: 'GPT-5.5' },
  { value: 'opus-4-6', label: 'Opus 4.6' },
  { value: 'sonnet-4-6', label: 'Sonnet 4.6' },
  { value: 'kimi-k2-6', label: 'Kimi K2 6' },
];

const TOOLS = ['browser', 'codeact', 'files', 'memory', 'research', 'voice'].map((tool) => ({ value: tool, label: tool }));

interface ProjectSettingsFormProps {
  project: ProjectInfo;
  onSaveAction: (input: Partial<ProjectInput>) => Promise<void>;
}

export function ProjectSettingsForm({ project, onSaveAction }: ProjectSettingsFormProps) {
  const [name, setName] = React.useState(project.name);
  const [slug, setSlug] = React.useState(project.slug);
  const [planner, setPlanner] = React.useState(project.default_planner ?? '');
  const [prompt, setPrompt] = React.useState(project.system_prompt_addendum ?? '');
  const [tools, setTools] = React.useState<string[]>(project.allowed_tools);
  const [saving, setSaving] = React.useState(false);

  return (
    <form
      style={{ display: 'grid', gap: 'var(--spacing-4)', maxWidth: 720 }}
      onSubmit={(event) => {
        event.preventDefault();
        setSaving(true);
        void onSaveAction({
          name,
          slug,
          default_planner: planner || null,
          system_prompt_addendum: prompt || null,
          allowed_tools: tools,
        }).finally(() => setSaving(false));
      }}
    >
      <Input label="Name" value={name} onChange={(event) => setName(event.target.value)} />
      <Input label="Slug" value={slug} onChange={(event) => setSlug(event.target.value)} />
      <label style={{ display: 'grid', gap: 'var(--spacing-1)', color: 'var(--color-foreground-muted)', fontSize: 'var(--text-sm)' }}>
        Default planner
        <Select options={PLANNERS} value={planner} onChange={(value) => setPlanner(String(value))} />
      </label>
      <Textarea
        label="System prompt addendum"
        value={prompt}
        onChange={(event) => setPrompt(event.target.value)}
        style={{ fontFamily: 'var(--font-mono)' }}
      />
      <label style={{ display: 'grid', gap: 'var(--spacing-1)', color: 'var(--color-foreground-muted)', fontSize: 'var(--text-sm)' }}>
        Allowed tools
        <Select multiple options={TOOLS} value={tools} onChange={(value) => setTools(Array.isArray(value) ? value : [value])} />
      </label>
      <Button type="submit" disabled={saving}>{saving ? 'Saving…' : 'Save settings'}</Button>
    </form>
  );
}
