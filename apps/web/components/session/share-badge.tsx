'use client';

import * as React from 'react';
import { Button } from '@/components/ui/button';

export interface ShareBadgeProps {
  sessionId: string;
  visible: boolean;
  onUnshare?: () => void;
}

export function ShareBadge({ sessionId, visible, onUnshare }: ShareBadgeProps): React.ReactElement | null {
  const [busy, setBusy] = React.useState(false);
  if (!visible) return null;

  const href = `/replay/${encodeURIComponent(sessionId)}`;
  const unshare = async () => {
    setBusy(true);
    try {
      const response = await fetch(`/api/share/${encodeURIComponent(sessionId)}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ share_public: false, expires_at: null }),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      onUnshare?.();
    } finally {
      setBusy(false);
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 'var(--spacing-2)',
        padding: 'var(--spacing-2) var(--spacing-3)',
        backgroundColor: 'color-mix(in oklch, var(--color-accent) 12%, var(--color-background-elevated))',
        color: 'var(--color-accent)',
        borderBottom: '1px solid var(--color-border)',
        fontSize: 'var(--text-sm)',
      }}
    >
      <span>This session is shared publicly</span>
      <span aria-hidden>·</span>
      <a href={href} style={{ color: 'inherit', textDecoration: 'underline' }}>view public link</a>
      <span aria-hidden>·</span>
      <Button variant="link" size="xs" loading={busy} onClick={() => void unshare()} style={{ color: 'inherit', padding: 0, minHeight: 0 }}>
        unshare
      </Button>
    </div>
  );
}

export default ShareBadge;
