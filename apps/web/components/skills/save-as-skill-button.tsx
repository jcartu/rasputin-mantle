'use client';

import * as React from 'react';
import { BookmarkPlus } from 'lucide-react';

import { SaveAsSkillModal } from '@/components/skills/save-as-skill-modal';
import { Button } from '@/components/ui/button';
import { useToast } from '@/components/ui/toast';

export interface SaveAsSkillButtonProps {
  sessionId: string;
}

export function SaveAsSkillButton({ sessionId }: SaveAsSkillButtonProps) {
  const [open, setOpen] = React.useState(false);
  const { toast } = useToast();
  return (
    <>
      <Button variant="secondary" size="sm" onClick={() => setOpen(true)} iconLeft={<BookmarkPlus className="h-4 w-4" />}>
        Save as Skill
      </Button>
      <SaveAsSkillModal
        sessionId={sessionId}
        open={open}
        onOpenChange={setOpen}
        onSaved={(skillName) => toast({ title: 'Skill saved', description: `${skillName} is now in My skills.` })}
      />
    </>
  );
}
