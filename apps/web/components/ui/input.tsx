"use client";

import * as React from 'react';

export interface InputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'> {
  label?: string;
  hint?: string;
  error?: string;
  leadingIcon?: React.ReactNode;
  trailingIcon?: React.ReactNode;
  inputSize?: 'sm' | 'md' | 'lg';
}

const AlertCircleIcon = ({ size = 14 }: { size?: number }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <circle cx="12" cy="12" r="10" />
    <line x1="12" y1="8" x2="12" y2="12" />
    <line x1="12" y1="16" x2="12.01" y2="16" />
  </svg>
);

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  (
    {
      label,
      hint,
      error,
      leadingIcon,
      trailingIcon,
      inputSize = 'md',
      disabled,
      style,
      className,
      ...props
    },
    ref
  ) => {
    const [isFocused, setIsFocused] = React.useState(false);
    const [isHovered, setIsHovered] = React.useState(false);

    const getHeight = () => {
      switch (inputSize) {
        case 'sm': return '28px';
        case 'lg': return '40px';
        case 'md':
        default: return '32px';
      }
    };

    const getBorderColor = () => {
      if (disabled) return 'var(--color-border)';
      if (error) return 'var(--color-destructive)';
      if (isFocused) return 'var(--color-accent)';
      if (isHovered) return 'var(--color-border-strong)';
      return 'var(--color-border)';
    };

    const getBorderWidth = () => {
      if (isFocused && !disabled) return '2px';
      return '1px';
    };

    const containerStyles: React.CSSProperties = {
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--spacing-1)',
      width: '100%',
      fontFamily: 'var(--font-sans)',
    };

    const labelStyles: React.CSSProperties = {
      fontSize: 'var(--text-sm)',
      fontWeight: 'var(--font-weight-regular)',
      color: 'var(--color-foreground-muted)',
    };

    const inputWrapperStyles: React.CSSProperties = {
      position: 'relative',
      display: 'flex',
      alignItems: 'center',
      width: '100%',
      height: getHeight(),
      backgroundColor: disabled ? 'var(--color-muted)' : 'var(--color-background)',
      borderStyle: 'solid',
      borderColor: getBorderColor(),
      borderWidth: getBorderWidth(),
      borderRadius: 'var(--radius-md)',
      boxSizing: 'border-box',
      transition: 'border-color var(--duration-fast) var(--ease-default), border-width var(--duration-fast) var(--ease-default)',
      cursor: disabled ? 'not-allowed' : 'text',
      overflow: 'hidden',
    };

    const inputStyles: React.CSSProperties = {
      flex: 1,
      height: '100%',
      width: '100%',
      backgroundColor: 'transparent',
      border: 'none',
      outline: 'none',
      paddingTop: 0,
      paddingBottom: 0,
      paddingLeft: leadingIcon ? 'var(--spacing-2)' : 'var(--spacing-2)',
      paddingRight: trailingIcon ? 'var(--spacing-2)' : 'var(--spacing-2)',
      fontSize: 'var(--text-sm)',
      fontWeight: 'var(--font-weight-regular)',
      color: disabled ? 'var(--color-foreground-faint)' : 'var(--color-foreground)',
      cursor: disabled ? 'not-allowed' : 'text',
      boxSizing: 'border-box',
    };

    const iconStyles: React.CSSProperties = {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      color: 'var(--color-foreground-muted)',
      width: '16px',
      height: '16px',
      flexShrink: 0,
    };

    const hintStyles: React.CSSProperties = {
      fontSize: 'var(--text-xs)',
      fontWeight: 'var(--font-weight-regular)',
      color: 'var(--color-foreground-faint)',
    };

    const errorStyles: React.CSSProperties = {
      display: 'flex',
      alignItems: 'center',
      gap: 'var(--spacing-1)',
      fontSize: 'var(--text-xs)',
      fontWeight: 'var(--font-weight-regular)',
      color: 'var(--color-destructive)',
    };

    return (
      <div style={containerStyles}>
        {label && <label style={labelStyles}>{label}</label>}
        
        <div 
          style={inputWrapperStyles}
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
        >
          {leadingIcon && (
            <div style={{ ...iconStyles, marginLeft: 'var(--spacing-2)' }}>
              {leadingIcon}
            </div>
          )}
          
          <input
            ref={ref}
            disabled={disabled}
            style={inputStyles}
            onFocus={(e) => {
              setIsFocused(true);
              props.onFocus?.(e);
            }}
            onBlur={(e) => {
              setIsFocused(false);
              props.onBlur?.(e);
            }}
            {...props}
          />
          
          {trailingIcon && (
            <div style={{ ...iconStyles, marginRight: 'var(--spacing-2)' }}>
              {trailingIcon}
            </div>
          )}
        </div>

        {error ? (
          <div style={errorStyles}>
            <AlertCircleIcon />
            <span>{error}</span>
          </div>
        ) : hint ? (
          <div style={hintStyles}>{hint}</div>
        ) : null}
        
        <style>{`
          input::placeholder {
            color: var(--color-foreground-faint);
          }
        `}</style>
      </div>
    );
  }
);

Input.displayName = 'Input';

export default Input;
