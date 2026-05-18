'use client';

import * as React from 'react';
import { Upload } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface KBUploaderProps {
  onUploadAction: (file: File) => Promise<void>;
}

export function KBUploader({ onUploadAction }: KBUploaderProps) {
  const [isDragging, setIsDragging] = React.useState(false);
  const [isUploading, setIsUploading] = React.useState(false);
  const inputRef = React.useRef<HTMLInputElement>(null);

  const uploadFiles = React.useCallback(
    async (files: FileList | File[]) => {
      setIsUploading(true);
      try {
        for (const file of Array.from(files)) {
          await onUploadAction(file);
        }
      } finally {
        setIsUploading(false);
      }
    },
    [onUploadAction]
  );

  return (
    <div
      onDragOver={(event) => {
        event.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={(event) => {
        event.preventDefault();
        setIsDragging(false);
        void uploadFiles(event.dataTransfer.files);
      }}
      style={{
        border: `1px dashed ${isDragging ? 'var(--color-accent)' : 'var(--color-border)'}`,
        borderRadius: 'var(--radius-lg)',
        padding: '32px',
        textAlign: 'center',
        backgroundColor: isDragging ? 'var(--color-accent-subtle)' : 'var(--color-background-elevated)',
      }}
    >
      <Upload size={28} style={{ margin: '0 auto 12px', color: 'var(--color-accent)' }} />
      <p style={{ marginBottom: 8, fontWeight: 600 }}>Drop files into the project knowledge base</p>
      <p style={{ marginBottom: 16, color: 'var(--color-foreground-muted)', fontSize: 'var(--text-sm)' }}>
        Up to 50 files and 100MB total per project.
      </p>
      <input
        ref={inputRef}
        type="file"
        multiple
        hidden
        onChange={(event) => {
          if (event.target.files) void uploadFiles(event.target.files);
        }}
      />
      <Button onClick={() => inputRef.current?.click()} disabled={isUploading}>
        {isUploading ? 'Uploading…' : 'Choose files'}
      </Button>
    </div>
  );
}
