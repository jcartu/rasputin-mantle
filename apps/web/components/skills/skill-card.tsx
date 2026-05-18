import Link from 'next/link';
import { Download, Sparkles } from 'lucide-react';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardBody, CardFooter, CardHeader } from '@/components/ui/card';
import type { SkillSummary } from '@/lib/skills';

export interface SkillCardProps {
  skill: SkillSummary;
  onInstall?: (skill: SkillSummary) => void;
}

export function SkillCard({ skill, onInstall }: SkillCardProps) {
  return (
    <Card className="flex h-full flex-col">
      <CardHeader className="space-y-3">
        <div className="flex items-start justify-between gap-3">
          <Link href={`/skills/${skill.name}`} className="min-w-0 text-lg font-semibold hover:underline">
            {skill.name}
          </Link>
          <Badge>{skill.capability}</Badge>
        </div>
        <p className="text-xs text-muted-foreground">by {skill.author || 'Mantle'} · {skill.source}</p>
      </CardHeader>
      <CardBody className="flex-1 space-y-4">
        <p className="text-sm text-muted-foreground line-clamp-3">{skill.description}</p>
        <div className="flex flex-wrap gap-2">
          {skill.tags.slice(0, 4).map((tag) => (
            <Badge key={tag} variant="outline">{tag}</Badge>
          ))}
        </div>
      </CardBody>
      <CardFooter className="flex gap-2">
        <Button variant="secondary" size="sm" onClick={() => onInstall?.(skill)} iconLeft={<Download className="h-4 w-4" />}>
          Install
        </Button>
        <Link href={`/skills/${skill.name}`} className="ml-auto">
          <Button variant="ghost" size="sm" iconLeft={<Sparkles className="h-4 w-4" />}>
            Details
          </Button>
        </Link>
      </CardFooter>
    </Card>
  );
}
