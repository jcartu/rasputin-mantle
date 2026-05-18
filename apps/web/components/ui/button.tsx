import * as React from 'react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'destructive' | 'link';
  size?: 'xs' | 'sm' | 'md' | 'lg';
  iconLeft?: React.ReactNode;
  iconRight?: React.ReactNode;
  iconOnly?: React.ReactNode;
  loading?: boolean;
}

const Spinner = ({ size = 16 }: { size?: number }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    style={{ animation: 'spin 1s linear infinite' }}
  >
    <path d="M21 12a9 9 0 1 1-6.219-8.56" />
    <style>{`
      @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
    `}</style>
  </svg>
);

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      iconLeft,
      iconRight,
      iconOnly,
      loading = false,
      disabled,
      children,
      style,
      ...props
    },
    ref
  ) => {
    const isDisabled = disabled || loading;

    const getVariantStyles = (): React.CSSProperties => {
      switch (variant) {
        case 'primary':
          return {
            backgroundColor: 'var(--color-accent)',
            color: 'var(--color-background)',
            border: 'none',
          };
        case 'secondary':
          return {
            backgroundColor: 'var(--color-background-subtle)',
            color: 'var(--color-foreground)',
            border: '1px solid var(--color-border)',
          };
        case 'ghost':
          return {
            backgroundColor: 'transparent',
            color: 'var(--color-foreground-muted)',
            border: 'none',
          };
        case 'destructive':
          return {
            backgroundColor: 'var(--color-destructive)',
            color: 'white',
            border: 'none',
          };
        case 'link':
          return {
            backgroundColor: 'transparent',
            color: 'var(--color-accent)',
            border: 'none',
            textDecoration: 'none',
          };
        default:
          return {};
      }
    };

    const getSizeStyles = (): React.CSSProperties => {
      if (iconOnly) {
        switch (size) {
          case 'xs': return { width: '24px', height: '24px', padding: 0 };
          case 'sm': return { width: '28px', height: '28px', padding: 0 };
          case 'md': return { width: '32px', height: '32px', padding: 0 };
          case 'lg': return { width: '40px', height: '40px', padding: 0 };
        }
      }

      switch (size) {
        case 'xs':
          return { height: '24px', padding: '0 8px', fontSize: 'var(--text-xs)' };
        case 'sm':
          return { height: '28px', padding: '0 10px', fontSize: 'var(--text-sm)' };
        case 'md':
          return { height: '32px', padding: '0 14px', fontSize: 'var(--text-sm)' };
        case 'lg':
          return { height: '40px', padding: '0 20px', fontSize: 'var(--text-base)' };
        default:
          return {};
      }
    };

    const getIconSize = () => {
      switch (size) {
        case 'xs':
        case 'sm':
          return 14;
        case 'md':
        case 'lg':
        default:
          return 16;
      }
    };

    const baseStyles: React.CSSProperties = {
      display: 'inline-flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: 'var(--spacing-1)',
      borderRadius: 'var(--radius-md)',
      fontWeight: 'var(--font-weight-semibold)',
      transition: 'all var(--duration-default) var(--ease-default)',
      cursor: isDisabled ? 'not-allowed' : 'pointer',
      opacity: isDisabled ? 0.5 : 1,
      pointerEvents: isDisabled ? 'none' : 'auto',
      minWidth: iconOnly ? undefined : '32px',
      minHeight: '32px', // Min touch target
      boxSizing: 'border-box',
      outline: 'none',
      fontFamily: 'var(--font-sans)',
      ...getVariantStyles(),
      ...getSizeStyles(),
      ...style,
    };

    return (
      <button
        ref={ref}
        disabled={isDisabled}
        style={baseStyles}
        data-variant={variant}
        {...props}
      >
        <style>{`
          button[data-variant="primary"]:hover {
            background-color: var(--color-accent-hover) !important;
          }
          button[data-variant="primary"]:active {
            transform: scale(0.98);
          }
          button[data-variant="secondary"]:hover {
            background-color: var(--color-muted) !important;
            border-color: var(--color-border-strong) !important;
          }
          button[data-variant="secondary"]:active {
            transform: scale(0.98);
          }
          button[data-variant="ghost"]:hover {
            background-color: var(--color-background-subtle) !important;
            color: var(--color-foreground) !important;
          }
          button[data-variant="ghost"]:active {
            transform: scale(0.98);
          }
          button[data-variant="destructive"]:hover {
            filter: brightness(0.9);
          }
          button[data-variant="destructive"]:active {
            transform: scale(0.98);
          }
          button[data-variant="link"]:hover {
            text-decoration: underline !important;
            color: var(--color-accent-hover) !important;
          }
          button[data-variant="link"]:active {
            transform: scale(0.98);
          }
          button:focus-visible {
            box-shadow: 0 0 0 2px var(--color-background), 0 0 0 4px var(--color-accent);
          }
        `}</style>
        {loading ? (
          <Spinner size={getIconSize()} />
        ) : iconOnly ? (
          iconOnly
        ) : (
          <>
            {iconLeft && <span style={{ display: 'flex' }}>{iconLeft}</span>}
            {children}
            {iconRight && <span style={{ display: 'flex' }}>{iconRight}</span>}
          </>
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';

export default Button;
