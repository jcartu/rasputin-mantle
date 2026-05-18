import * as React from 'react';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'success' | 'warn' | 'error' | 'outline';
  size?: 'sm' | 'md';
}

export const Badge = React.forwardRef<HTMLSpanElement, BadgeProps>(
  ({ variant = 'default', size = 'md', className, style, ...props }, ref) => {
    let backgroundColor = 'var(--color-muted)';
    let color = 'var(--color-foreground-muted)';
    let border = 'none';

    switch (variant) {
      case 'success':
        backgroundColor = 'var(--color-success-subtle)';
        color = 'var(--color-success)';
        break;
      case 'warn':
        backgroundColor = 'var(--color-warning-subtle)';
        color = 'var(--color-warning)';
        break;
      case 'error':
        backgroundColor = 'var(--color-destructive-subtle)';
        color = 'var(--color-destructive)';
        break;
      case 'outline':
        backgroundColor = 'transparent';
        color = 'var(--color-foreground-muted)';
        border = '1px solid var(--color-border-strong)';
        break;
      case 'default':
      default:
        backgroundColor = 'var(--color-muted)';
        color = 'var(--color-foreground-muted)';
        break;
    }

    const height = size === 'sm' ? '18px' : '22px';
    const padding = size === 'sm' ? '2px 6px' : '2px 8px';

    return (
      <span
        ref={ref}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '4px',
          borderRadius: 'var(--radius-full)',
          fontSize: 'var(--text-xs)',
          fontWeight: 'var(--font-weight-semibold)',
          height,
          padding,
          backgroundColor,
          color,
          border,
          boxSizing: 'border-box',
          ...style,
        }}
        className={className}
        {...props}
      />
    );
  }
);
Badge.displayName = 'Badge';
