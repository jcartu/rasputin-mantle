'use client';

import * as React from 'react';

export interface BottomBarProps extends React.HTMLAttributes<HTMLDivElement> {
  steps: number;
  cost: string;
  eta: string;
}

const NUMERIC_STYLE: React.CSSProperties = {
  fontFamily: 'var(--font-mono)',
  fontSize: 'var(--text-xs)',
  color: 'var(--color-foreground-muted)',
  fontVariantNumeric: 'tabular-nums',
  letterSpacing: 0,
  lineHeight: 1,
  whiteSpace: 'nowrap',
};

const LABEL_STYLE: React.CSSProperties = {
  fontFamily: 'var(--font-mono)',
  fontSize: 'var(--text-xs)',
  color: 'var(--color-foreground-faint)',
  fontVariantNumeric: 'tabular-nums',
  textTransform: 'uppercase',
  letterSpacing: '0.04em',
  lineHeight: 1,
  whiteSpace: 'nowrap',
};

export const BottomBar = React.forwardRef<HTMLDivElement, BottomBarProps>(
  ({ steps, cost, eta, style, className, ...props }, ref) => {
    return (
      <footer
        ref={ref}
        role="contentinfo"
        style={{
          height: '40px',
          display: 'grid',
          gridTemplateColumns: '1fr 1fr 1fr',
          alignItems: 'center',
          padding: '0 var(--spacing-4)',
          backgroundColor: 'var(--color-background-elevated)',
          borderTop: '1px solid var(--color-border)',
          boxSizing: 'border-box',
          flexShrink: 0,
          ...style,
        }}
        className={className}
        {...props}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--spacing-2)',
            justifyContent: 'flex-start',
          }}
        >
          <span style={LABEL_STYLE}>Step</span>
          <span style={NUMERIC_STYLE} aria-label="Step counter">
            {steps}
          </span>
        </div>

        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--spacing-2)',
            justifyContent: 'center',
          }}
        >
          <span style={LABEL_STYLE}>Cost</span>
          <span style={NUMERIC_STYLE} aria-label="Running cost">
            {cost}
          </span>
        </div>

        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--spacing-2)',
            justifyContent: 'flex-end',
          }}
        >
          <span style={LABEL_STYLE}>ETA</span>
          <span style={NUMERIC_STYLE} aria-label="Estimated time remaining">
            {eta}
          </span>
        </div>
      </footer>
    );
  },
);

BottomBar.displayName = 'BottomBar';

export default BottomBar;
