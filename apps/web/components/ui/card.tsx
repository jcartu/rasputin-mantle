import * as React from 'react';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {}

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, style, ...props }, ref) => {
    return (
      <div
        ref={ref}
        style={{
          backgroundColor: 'var(--color-background-elevated)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-md)',
          boxShadow: 'var(--shadow-sm)',
          overflow: 'hidden',
          transition: 'border-color var(--duration-fast) var(--ease-default)',
          ...style,
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.borderColor = 'var(--color-border-strong)';
          props.onMouseEnter?.(e);
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.borderColor = 'var(--color-border)';
          props.onMouseLeave?.(e);
        }}
        className={className}
        {...props}
      />
    );
  }
);
Card.displayName = 'Card';

export interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  withBorder?: boolean;
}

export const CardHeader = React.forwardRef<HTMLDivElement, CardHeaderProps>(
  ({ className, style, withBorder = false, ...props }, ref) => {
    return (
      <div
        ref={ref}
        style={{
          padding: '16px',
          borderBottom: withBorder ? '1px solid var(--color-border)' : 'none',
          ...style,
        }}
        className={className}
        {...props}
      />
    );
  }
);
CardHeader.displayName = 'CardHeader';

export interface CardBodyProps extends React.HTMLAttributes<HTMLDivElement> {}

export const CardBody = React.forwardRef<HTMLDivElement, CardBodyProps>(
  ({ className, style, ...props }, ref) => {
    return (
      <div
        ref={ref}
        style={{
          padding: '16px',
          ...style,
        }}
        className={className}
        {...props}
      />
    );
  }
);
CardBody.displayName = 'CardBody';

export interface CardFooterProps extends React.HTMLAttributes<HTMLDivElement> {
  withBorder?: boolean;
}

export const CardFooter = React.forwardRef<HTMLDivElement, CardFooterProps>(
  ({ className, style, withBorder = false, ...props }, ref) => {
    return (
      <div
        ref={ref}
        style={{
          padding: '16px',
          borderTop: withBorder ? '1px solid var(--color-border)' : 'none',
          ...style,
        }}
        className={className}
        {...props}
      />
    );
  }
);
CardFooter.displayName = 'CardFooter';
