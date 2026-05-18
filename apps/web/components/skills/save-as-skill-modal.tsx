import * as React from 'react';

import { Button } from '@/components/ui/button';
import Dialog from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { saveSessionAsSkill } from '@/lib/skills';

export interface SaveAsSkillModalProps {
  sessionId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSaved?: (skillName: string) => void;
}

export function SaveAsSkillModal({ sessionId, open, onOpenChange, onSaved }: SaveAsSkillModalProps) {
  const [name, setName] = React.useState('');
  const [description, setDescription] = React.useState('');
  const [tags, setTags] = React.useState('saved-session');
  const [isSaving, setIsSaving] = React.useState(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setIsSaving(true);
    try {
      const skill = await saveSessionAsSkill(sessionId, {
        name,
        description,
        intent_tags: tags.split(',').map((tag) => tag.trim()).filter(Boolean),
        publish_publicly: false,
      });
      onSaved?.(skill.name);
      onOpenChange(false);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Dialog
      isOpen={open}
      onClose={() => onOpenChange(false)}
      title="Save as Skill"
      footer={
        <>
          <Button type="button" variant="secondary" onClick={() => onOpenChange(false)} disabled={isSaving}>Cancel</Button>
          <Button type="submit" form="save-skill-form" loading={isSaving} disabled={!name || !description}>Save skill</Button>
        </>
      }
    >
      <form id="save-skill-form" className="space-y-4" onSubmit={handleSubmit}>
        <p className="text-sm text-muted-foreground">Capture this completed session as a reusable Agent Skill.</p>
        <label className="block space-y-2 text-sm font-medium">
          <span>Name</span>
          <Input value={name} onChange={(event) => setName(event.target.value)} placeholder="weekly-metrics-review" required />
        </label>
        <label className="block space-y-2 text-sm font-medium">
          <span>Description</span>
          <Textarea value={description} onChange={(event) => setDescription(event.target.value)} placeholder="What should this skill help with?" required />
        </label>
        <label className="block space-y-2 text-sm font-medium">
          <span>Intent tags</span>
          <Input value={tags} onChange={(event) => setTags(event.target.value)} placeholder="reporting, weekly, ops" />
        </label>
      </form>
    </Dialog>
  );
}
