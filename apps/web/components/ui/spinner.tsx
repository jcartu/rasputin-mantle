import * as React from 'react';

export interface SpinnerProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'indeterminate' | 'determinate';
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  progress?: number; // 0-100 for determinate
}

const sizeMap = {
  xs: 16,
  sm: 20,
  md: 24,
  lg: 32,
  xl: 40,
};

export const Spinner = React.forwardRef<HTMLDivElement, SpinnerProps>(
  (
    {
      variant = 'indeterminate',
      size = 'md',
      progress = 0,
      style,
      className,
      ...props
    },
    ref
  ) => {
    const pxSize = sizeMap[size];
    const strokeWidth = 2;
    const radius = (pxSize - strokeWidth) / 2;
    const circumference = radius * 2 * Math.PI;
    
    const clampedProgress = Math.min(100, Math.max(0, progress));
    const offset = circumference - (clampedProgress / 100) * circumference;

    return (
      <div
        ref={ref}
        className={`spinner-container ${className || ''}`.trim()}
        style={{
          display: 'inline-flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 'var(--spacing-2)',
          ...style,
        }}
        {...props}
      >
        <style>{`
          @keyframes spin-accent {
            to { transform: rotate(360deg); }
          }
          .spinner-svg-indeterminate {
            animation: spin-accent 0.8s linear infinite;
          }
          @media (prefers-reduced-motion: reduce) {
            .spinner-svg-indeterminate {
              animation: none !important;
            }
          }
        `}</style>
        <svg
          width={pxSize}
          height={pxSize}
          viewBox={`0 0 ${pxSize} ${pxSize}`}
          className={variant === 'indeterminate' ? 'spinner-svg-indeterminate' : ''}
          style={{
            transform: variant === 'determinate' ? 'rotate(-90deg)' : undefined,
          }}
        >
          {/* Track */}
          <circle
            cx={pxSize / 2}
            cy={pxSize / 2}
            r={radius}
            fill="none"
            stroke="var(--color-muted)"
            strokeWidth={strokeWidth}
          />
          {/* Progress / Accent */}
          <circle
            cx={pxSize / 2}
            cy={pxSize / 2}
            r={radius}
            fill="none"
            stroke="var(--color-accent)"
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={variant === 'determinate' ? circumference : `${circumference * 0.75} ${circumference * 0.25}`}
            strokeDashoffset={variant === 'determinate' ? offset : 0}
            style={{
              transition: variant === 'determinate' ? 'stroke-dashoffset 0.2s ease-in-out' : undefined,
            }}
          />
        </svg>
        {variant === 'determinate' && (
          <span
            style={{
              fontSize: 'var(--text-xs)',
              color: 'var(--color-foreground-muted)',
              lineHeight: 1,
            }}
          >
            {Math.round(clampedProgress)}%
          </span>
        )}
      </div>
    );
  }
);

Spinner.displayName = 'Spinner';

export default Spinner;
