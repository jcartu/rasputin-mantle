'use client';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardBody, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';

interface IntegrationCardProps {
  name: string;
  description: string;
  connected: boolean;
  configured: boolean;
  metadata?: string;
  actionLabel?: string;
  onAction?: () => void;
}

export function IntegrationCard({ name, description, connected, configured, metadata, actionLabel, onAction }: IntegrationCardProps) {
  return (
    <Card className="flex h-full flex-col">
      <CardHeader>
        <div className="flex items-start justify-between gap-3">
          <CardTitle>{name}</CardTitle>
          <Badge variant={connected ? 'success' : configured ? 'warn' : 'secondary'}>
            {connected ? 'connected' : configured ? 'configured' : 'not configured'}
          </Badge>
        </div>
      </CardHeader>
      <CardBody className="flex-1" style={{ display: 'grid', gap: 'var(--spacing-2)' }}>
        <p style={{ color: 'var(--color-foreground-muted)', fontSize: 'var(--text-sm)' }}>{description}</p>
        {metadata ? <p style={{ color: 'var(--color-foreground-faint)', fontSize: 'var(--text-xs)' }}>{metadata}</p> : null}
      </CardBody>
      {actionLabel && onAction ? (
        <CardFooter withBorder>
          <Button variant={connected ? 'destructive' : 'outline'} size="sm" onClick={onAction}>{actionLabel}</Button>
        </CardFooter>
      ) : null}
    </Card>
  );
}
