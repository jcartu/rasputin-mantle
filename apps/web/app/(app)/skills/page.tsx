'use client';

import * as React from 'react';

import { SkillCard } from '@/components/skills/skill-card';
import { EmptyState } from '@/components/ui/empty-state';
import { TabContent, TabList, Tabs, TabTrigger } from '@/components/ui/tab';
import { useToast } from '@/components/ui/toast';
import { listSkills, type SkillSummary } from '@/lib/skills';

export default function SkillsPage() {
  const [skills, setSkills] = React.useState<SkillSummary[]>([]);
  const [isLoading, setIsLoading] = React.useState(true);
  const { toast } = useToast();

  React.useEffect(() => {
    listSkills()
      .then(setSkills)
      .catch((error) => {
        toast({
          title: 'Failed to load skills',
          description: error instanceof Error ? error.message : 'Unknown error',
          variant: 'destructive',
        });
      })
      .finally(() => setIsLoading(false));
  }, [toast]);

  return (
    <div className="container space-y-8 py-8">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Agent Skills Marketplace</h1>
        <p className="text-muted-foreground">Browse reusable SKILL.md workflows discovered from bundled, session, and user skill folders.</p>
      </div>

      <Tabs defaultValue="public">
        <TabList className="mb-6">
          <TabTrigger value="public">Browse public</TabTrigger>
          <TabTrigger value="mine">My skills</TabTrigger>
          <TabTrigger value="team">Team skills</TabTrigger>
        </TabList>
        <TabContent value="public">
          {isLoading ? (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {Array.from({ length: 8 }).map((_, index) => <div key={index} className="h-56 animate-pulse rounded-xl bg-muted" />)}
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {skills.map((skill) => (
                <SkillCard
                  key={skill.name}
                  skill={skill}
                  onInstall={() => toast({ title: 'Install queued', description: `${skill.name} can be copied to ~/.mantle/skills/.` })}
                />
              ))}
            </div>
          )}
        </TabContent>
        <TabContent value="mine">
          <EmptyState title="My skills are coming soon" description="Saved sessions and installed personal skills will appear here." />
        </TabContent>
        <TabContent value="team">
          <EmptyState title="Team skills are coming soon" description="Team-shared skills will connect to project membership in a later wave." />
        </TabContent>
      </Tabs>
    </div>
  );
}
