import { Download, Play } from 'lucide-react';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardBody, CardHeader } from '@/components/ui/card';
import type { SkillDetail as SkillDetailData } from '@/lib/skills';

export interface SkillDetailProps {
  skill: SkillDetailData;
  onInstall?: () => void;
  onUse?: () => void;
}

export function SkillDetail({ skill, onInstall, onUse }: SkillDetailProps) {
  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            <h1 className="text-3xl font-bold tracking-tight">{skill.name}</h1>
            <Badge>{skill.capability}</Badge>
          </div>
          <p className="max-w-3xl text-muted-foreground">{skill.description}</p>
          <div className="flex flex-wrap gap-2">
            {skill.tags.map((tag) => <Badge key={tag} variant="outline">{tag}</Badge>)}
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" onClick={onInstall} iconLeft={<Download className="h-4 w-4" />}>Install</Button>
          <Button onClick={onUse} iconLeft={<Play className="h-4 w-4" />}>Use in session</Button>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
        <Card>
          <CardHeader withBorder>
            <h2 className="text-xl font-semibold">SKILL.md</h2>
          </CardHeader>
          <CardBody>
            <MarkdownBlock markdown={skill.readme} />
          </CardBody>
        </Card>
        <aside className="space-y-4">
          <InfoCard title="When to use" value={skill.when_to_use} />
          <InfoCard title="Version" value={skill.version} />
          <InfoCard title="License" value={skill.license} />
          <InfoCard title="Scripts" value={skill.scripts.length ? skill.scripts.join('\n') : 'No scripts'} />
          <InfoCard title="Usage examples" value={skill.examples.length ? skill.examples.join('\n') : 'Provide JSON args, then invoke the first bundled script.'} />
        </aside>
      </div>
    </div>
  );
}

function InfoCard({ title, value }: { title: string; value: string }) {
  return (
    <Card>
      <CardHeader className="pb-2"><h3 className="text-sm font-semibold">{title}</h3></CardHeader>
      <CardBody className="pt-0"><p className="whitespace-pre-wrap text-sm text-muted-foreground">{value}</p></CardBody>
    </Card>
  );
}

function MarkdownBlock({ markdown }: { markdown: string }) {
  const lines = markdown.split('\n');
  return (
    <div className="space-y-3 text-sm leading-6">
      {lines.map((line, index) => {
        const key = `${index}-${line}`;
        if (line.startsWith('# ')) return <h1 key={key} className="text-2xl font-bold">{line.slice(2)}</h1>;
        if (line.startsWith('## ')) return <h2 key={key} className="pt-3 text-xl font-semibold">{line.slice(3)}</h2>;
        if (line.startsWith('### ')) return <h3 key={key} className="pt-2 text-lg font-semibold">{line.slice(4)}</h3>;
        if (line.startsWith('- ')) return <p key={key} className="pl-4 text-muted-foreground">• {line.slice(2)}</p>;
        if (!line.trim()) return <div key={key} className="h-1" />;
        return <p key={key} className="text-muted-foreground">{line}</p>;
      })}
    </div>
  );
}
