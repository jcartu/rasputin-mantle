'use client';

import * as React from 'react';
import { Tooltip } from '@/components/ui/tooltip';
import type { ToolCallEvent } from '@/components/session/tool-call-card';

export interface CostGutterEvent extends ToolCallEvent {
  model?: string;
}

export interface CostGutterProps {
  events: CostGutterEvent[];
  /** Height of each row in pixels — must align with chat card heights */
  rowHeight?: number;
}

const formatCost = (cost: number | undefined): string => {
  if (typeof cost !== 'number') return '—';
  if (cost === 0) return '$0.000';
  if (cost < 0.001) return `$${cost.toFixed(4)}`;
  return `$${cost.toFixed(3)}`;
};

const rowBaseStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'flex-end',
  justifyContent: 'flex-start',
  paddingTop: 'var(--spacing-4)',
  paddingRight: 'var(--spacing-3)',
  fontVariantNumeric: 'tabular-nums',
  fontFamily: 'var(--font-mono)',
  cursor: 'default',
  lineHeight: 1.3,
};

const stepStyle: React.CSSProperties = {
  fontSize: 'var(--text-xs)',
  color: 'var(--color-foreground-faint)',
};

const costStyle: React.CSSProperties = {
  fontSize: 'var(--text-xs)',
  color: 'var(--color-foreground-muted)',
  marginTop: '2px',
};

function CostBreakdown({ event }: { event: CostGutterEvent }) {
  const input = event.tokens?.input ?? 0;
  const output = event.tokens?.output ?? 0;
  const model = event.model ?? 'unknown';

  return (
    <span
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '2px',
        fontFamily: 'var(--font-mono)',
      }}
    >
      <span>model: {model}</span>
      <span>input: {input} tok</span>
      <span>output: {output} tok</span>
      <span>cost: {formatCost(event.cost)}</span>
    </span>
  );
}

export const CostGutter = React.forwardRef<HTMLDivElement, CostGutterProps>(
  ({ events, rowHeight }, ref) => {
    return (
      <div
        ref={ref}
        aria-label="Per-step cost"
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: 'var(--spacing-2)',
          width: '64px',
          flexShrink: 0,
          userSelect: 'none',
        }}
      >
        {events.map((event, idx) => {
          const row = (
            <div
              style={{
                ...rowBaseStyle,
                ...(rowHeight ? { minHeight: `${rowHeight}px` } : null),
              }}
            >
              <span style={stepStyle}>{String(idx + 1).padStart(2, '0')}</span>
              <span style={costStyle}>{formatCost(event.cost)}</span>
            </div>
          );

          return (
            <Tooltip
              key={`${event.timestamp}-${idx}`}
              content={<CostBreakdown event={event} />}
            >
              {row}
            </Tooltip>
          );
        })}
      </div>
    );
  }
);

CostGutter.displayName = 'CostGutter';

export default CostGutter;
