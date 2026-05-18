'use client';

import * as React from 'react';
import { ChatStream } from '@/components/session/chat-stream';
import { ComputerView } from '@/components/session/computer-view';
import { FileTree, type SandboxFileEntry } from '@/components/session/file-tree';
import { TimelineScrubber, type ReplayStep } from '@/components/session/timeline-scrubber';

export interface ReplaySessionViewProps {
  sessionId: string;
  steps: ReplayStep[];
  initialStep?: number;
  loading?: boolean;
  banner?: React.ReactNode;
}

const CHAT_PANE_WIDTH = 340;
const FILES_PANE_WIDTH = 320;

function payloadData(step: ReplayStep): Record<string, unknown> {
  const data = step.payload.data;
  return typeof data === 'object' && data !== null ? data as Record<string, unknown> : {};
}

function pickString(record: Record<string, unknown>, keys: string[]): string | null {
  for (const key of keys) {
    const value = record[key];
    if (typeof value === 'string' && value.length > 0) return value;
  }
  return null;
}

function currentScreenshot(steps: ReplayStep[], currentStep: number): string | null {
  for (let index = currentStep; index >= 0; index -= 1) {
    const step = steps[index];
    if (!step) continue;
    const data = payloadData(step);
    const screenshot = pickString(data, ['src', 'screenshot', 'screenshot_url', 'url']);
    if (screenshot) return screenshot;
  }
  return null;
}

function toFileEntry(value: unknown): SandboxFileEntry | null {
  if (typeof value !== 'object' || value === null) return null;
  const record = value as Record<string, unknown>;
  const path = typeof record.path === 'string' ? record.path : null;
  if (!path) return null;
  const name = typeof record.name === 'string' ? record.name : path.split('/').filter(Boolean).at(-1) ?? path;
  const kind = record.kind === 'dir' || record.type === 'directory' ? 'dir' : 'file';
  return {
    path,
    name,
    kind,
    size: typeof record.size === 'number' ? record.size : undefined,
    mime: typeof record.mime === 'string' ? record.mime : undefined,
    thumbnail: typeof record.thumbnail === 'string' ? record.thumbnail : undefined,
  };
}

function currentFiles(steps: ReplayStep[], currentStep: number): SandboxFileEntry[] {
  for (let index = currentStep; index >= 0; index -= 1) {
    const data = payloadData(steps[index]);
    const files = data.files;
    if (Array.isArray(files)) return files.map(toFileEntry).filter((entry): entry is SandboxFileEntry => entry !== null);
  }
  return [];
}

export function ReplaySessionView({
  sessionId,
  steps,
  initialStep = 0,
  loading = false,
  banner,
}: ReplaySessionViewProps): React.ReactElement {
  const [currentStep, setCurrentStep] = React.useState(Math.min(Math.max(initialStep, 0), Math.max(steps.length - 1, 0)));
  const screenshotUrl = currentScreenshot(steps, currentStep);
  const files = currentFiles(steps, currentStep);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', width: '100%', background: 'var(--color-background)' }}>
      {banner}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: `${CHAT_PANE_WIDTH}px 1fr ${FILES_PANE_WIDTH}px`,
          minHeight: 0,
          flex: 1,
          overflow: 'hidden',
        }}
      >
        <section aria-label="Replay chat" style={{ minWidth: 0, borderRight: '1px solid var(--color-border)', overflow: 'hidden' }}>
          <ChatStream sessionId={sessionId} replaySteps={steps} replayStep={currentStep} />
        </section>
        <section aria-label="Replay computer" style={{ minWidth: 0, overflow: 'hidden' }}>
          <ComputerView sessionId={sessionId} screenshotUrl={screenshotUrl} isControlTaken={false} readOnly />
        </section>
        <section aria-label="Replay files" style={{ minWidth: 0, borderLeft: '1px solid var(--color-border)', overflow: 'hidden' }}>
          <FileTree sessionId={sessionId} entries={files} />
        </section>
      </div>
      <TimelineScrubber steps={steps} currentStep={currentStep} onStepChange={setCurrentStep} loading={loading} />
    </div>
  );
}

export default ReplaySessionView;
