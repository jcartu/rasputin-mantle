'use client';

import { FileText, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { KBFileInfo } from '@/lib/api';

interface KBFileListProps {
  files: KBFileInfo[];
  onDelete?: (fileId: number) => void;
}

export function KBFileList({ files, onDelete }: KBFileListProps) {
  if (files.length === 0) {
    return <p style={{ color: 'var(--color-foreground-muted)' }}>No knowledge files uploaded yet.</p>;
  }

  return (
    <div style={{ border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', overflow: 'hidden' }}>
      {files.map((file) => (
        <div
          key={file.id}
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr 120px 180px auto',
            gap: 'var(--spacing-3)',
            alignItems: 'center',
            padding: '12px 14px',
            borderBottom: '1px solid var(--color-border)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-2)', minWidth: 0 }}>
            <FileText size={16} />
            <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{file.filename}</span>
          </div>
          <span style={{ color: 'var(--color-foreground-muted)', fontSize: 'var(--text-sm)' }}>{formatBytes(file.size_bytes)}</span>
          <span style={{ color: 'var(--color-foreground-muted)', fontSize: 'var(--text-sm)' }}>
            {new Date(file.uploaded_at).toLocaleString()}
          </span>
          {onDelete ? (
            <Button variant="ghost" size="sm" onClick={() => onDelete(file.id)} aria-label={`Delete ${file.filename}`}>
              <Trash2 size={14} />
            </Button>
          ) : null}
        </div>
      ))}
    </div>
  );
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
