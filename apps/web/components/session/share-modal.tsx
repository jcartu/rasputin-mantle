'use client';

import * as React from 'react';
import { ClipboardCopy } from 'lucide-react';
import Dialog from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';

export interface ShareModalProps {
  sessionId: string;
  isOpen: boolean;
  sharePublic: boolean;
  onClose: () => void;
  onShareChange?: (sharePublic: boolean, expiresAt: string | null) => void;
}

type ExpiryChoice = '24h' | '7d' | '30d' | 'never';

const EXPIRY_MS: Record<Exclude<ExpiryChoice, 'never'>, number> = {
  '24h': 24 * 60 * 60 * 1000,
  '7d': 7 * 24 * 60 * 60 * 1000,
  '30d': 30 * 24 * 60 * 60 * 1000,
};

function expiryToIso(choice: ExpiryChoice): string | null {
  if (choice === 'never') return null;
  return new Date(Date.now() + EXPIRY_MS[choice]).toISOString();
}

export function ShareModal({
  sessionId,
  isOpen,
  sharePublic,
  onClose,
  onShareChange,
}: ShareModalProps): React.ReactElement {
  const [enabled, setEnabled] = React.useState(sharePublic);
  const [expiry, setExpiry] = React.useState<ExpiryChoice>('never');
  const [saving, setSaving] = React.useState(false);
  const [copied, setCopied] = React.useState(false);
  const publicUrl = typeof window === 'undefined' ? `/replay/${sessionId}` : `${window.location.origin}/replay/${sessionId}`;

  React.useEffect(() => {
    setEnabled(sharePublic);
  }, [sharePublic, isOpen]);

  const save = React.useCallback(async (nextEnabled: boolean, nextExpiry: ExpiryChoice = expiry) => {
    setSaving(true);
    const expiresAt = nextEnabled ? expiryToIso(nextExpiry) : null;
    try {
      const response = await fetch(`/api/share/${encodeURIComponent(sessionId)}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ share_public: nextEnabled, expires_at: expiresAt }),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      setEnabled(nextEnabled);
      onShareChange?.(nextEnabled, expiresAt);
    } finally {
      setSaving(false);
    }
  }, [expiry, onShareChange, sessionId]);

  const copy = React.useCallback(async () => {
    await navigator.clipboard.writeText(publicUrl);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1500);
  }, [publicUrl]);

  return (
    <Dialog
      isOpen={isOpen}
      onClose={onClose}
      title="Share replay"
      footer={<Button variant="secondary" onClick={onClose}>Done</Button>}
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-4)' }}>
        <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 'var(--spacing-4)' }}>
          <span>
            <span style={{ display: 'block', fontWeight: 'var(--font-weight-semibold)' }}>Public replay link</span>
            <span style={{ color: 'var(--color-foreground-muted)', fontSize: 'var(--text-sm)' }}>Anyone with the link can view the read-only replay.</span>
          </span>
          <Switch
            checked={enabled}
            disabled={saving}
            onCheckedChange={(value) => void save(value)}
            aria-label="Toggle public replay"
          />
        </label>

        <label style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-2)', fontSize: 'var(--text-sm)' }}>
          Expires
          <select
            value={expiry}
            disabled={!enabled || saving}
            onChange={(event) => {
              const next = event.target.value as ExpiryChoice;
              setExpiry(next);
              if (enabled) void save(true, next);
            }}
            style={{ height: 32, borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)', background: 'var(--color-background)', color: 'var(--color-foreground)' }}
          >
            <option value="24h">24 hours</option>
            <option value="7d">7 days</option>
            <option value="30d">30 days</option>
            <option value="never">Never</option>
          </select>
        </label>

        <div style={{ display: 'flex', gap: 'var(--spacing-2)' }}>
          <input
            readOnly
            value={publicUrl}
            aria-label="Public replay URL"
            style={{ flex: 1, height: 32, padding: '0 var(--spacing-2)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)', background: 'var(--color-background-subtle)', color: 'var(--color-foreground)', fontFamily: 'var(--font-mono)', fontSize: 'var(--text-xs)' }}
          />
          <Button variant="secondary" size="sm" iconLeft={<ClipboardCopy size={14} strokeWidth={1.5} />} onClick={() => void copy()} disabled={!enabled}>
            {copied ? 'Copied' : 'Copy'}
          </Button>
        </div>
      </div>
    </Dialog>
  );
}

export default ShareModal;
