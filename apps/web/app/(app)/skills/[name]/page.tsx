'use client';

import * as React from 'react';
import { useParams, useRouter } from 'next/navigation';

import { SkillDetail } from '@/components/skills/skill-detail';
import { useToast } from '@/components/ui/toast';
import { createSession } from '@/lib/api';
import { getSkill, invokeSkill, type SkillDetail as SkillDetailData } from '@/lib/skills';

export default function SkillDetailPage() {
  const params = useParams<{ name: string }>();
  const router = useRouter();
  const { toast } = useToast();
  const [skill, setSkill] = React.useState<SkillDetailData | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);

  React.useEffect(() => {
    getSkill(params.name)
      .then(setSkill)
      .catch((error) => {
        toast({ title: 'Failed to load skill', description: error instanceof Error ? error.message : 'Unknown error', variant: 'destructive' });
      })
      .finally(() => setIsLoading(false));
  }, [params.name, toast]);

  const handleUse = async () => {
    if (!skill) return;
    const session = await createSession();
    await invokeSkill(skill.name, { session_id: session.session_id });
    router.push(`/session/${session.session_id}`);
  };

  if (isLoading) return <div className="container py-8"><div className="h-96 animate-pulse rounded-xl bg-muted" /></div>;
  if (!skill) return <div className="container py-8">Skill not found.</div>;

  return (
    <div className="container py-8">
      <SkillDetail
        skill={skill}
        onInstall={() => toast({ title: 'Install queued', description: `${skill.name} can be copied to ~/.mantle/skills/.` })}
        onUse={handleUse}
      />
    </div>
  );
}
