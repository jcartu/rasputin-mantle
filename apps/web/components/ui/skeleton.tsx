import * as React from 'react';

export interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'block' | 'circle' | 'text';
  size?: 32 | 40 | 48;
  height?: number | string;
  lines?: number;
}

const SHIMMER_KEYFRAMES = `
@keyframes shimmer-pulse {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.6; }
}
.skeleton-shimmer {
  animation: shimmer-pulse 1.5s linear infinite;
}
@media (prefers-reduced-motion: reduce) {
  .skeleton-shimmer {
    animation: none !important;
    opacity: 0.3 !important;
  }
}
`;

export const Skeleton = React.forwardRef<HTMLDivElement, SkeletonProps>(
  (
    {
      variant = 'block',
      size = 32,
      height = 48,
      lines = 1,
      style,
      className,
      ...props
    },
    ref
  ) => {
    const baseStyles: React.CSSProperties = {
      backgroundColor: 'var(--color-muted)',
    };

    const computedClassName = `skeleton-shimmer${className ? ` ${className}` : ''}`;

    if (variant === 'circle') {
      return (
        <>
          <style>{SHIMMER_KEYFRAMES}</style>
          <div
            ref={ref}
            className={computedClassName}
            style={{
              ...baseStyles,
              width: size,
              height: size,
              borderRadius: 'var(--radius-full)',
              ...style,
            }}
            {...props}
          />
        </>
      );
    }

    if (variant === 'text') {
      // Deterministic varied widths: index-based pattern
      const widths = ['100%', '85%', '70%', '95%', '80%'];
      return (
        <>
          <style>{SHIMMER_KEYFRAMES}</style>
          <div
            ref={ref}
            className={className}
            style={{
              display: 'flex',
              flexDirection: 'column',
              gap: 'var(--spacing-2)',
              width: '100%',
              ...style,
            }}
            {...props}
          >
            {Array.from({ length: lines }).map((_, i) => {
              const isLast = i === lines - 1 && lines > 1;
              const width = isLast ? '60%' : widths[i % widths.length];
              return (
                <div
                  key={i}
                  className="skeleton-shimmer"
                  style={{
                    ...baseStyles,
                    height: '12px',
                    width,
                    borderRadius: 'var(--radius-sm)',
                  }}
                />
              );
            })}
          </div>
        </>
      );
    }

    // Block variant
    return (
      <>
        <style>{SHIMMER_KEYFRAMES}</style>
        <div
          ref={ref}
          className={computedClassName}
          style={{
            ...baseStyles,
            width: '100%',
            height,
            borderRadius: 'var(--radius-sm)',
            ...style,
          }}
          {...props}
        />
      </>
    );
  }
);

Skeleton.displayName = 'Skeleton';

export default Skeleton;
