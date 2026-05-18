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

export const CardContent = CardBody;

export interface CardTitleProps extends React.HTMLAttributes<HTMLHeadingElement> {}

export const CardTitle = React.forwardRef<HTMLHeadingElement, CardTitleProps>(
  ({ className, style, ...props }, ref) => (
    <h3
      ref={ref}
      style={{
        margin: 0,
        fontSize: 'var(--text-lg)',
        fontWeight: 'var(--font-weight-semibold)',
        color: 'var(--color-foreground)',
        ...style,
      }}
      className={className}
      {...props}
    />
  )
);
CardTitle.displayName = 'CardTitle';

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
