"use client";

import * as React from 'react';

export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  hint?: string;
  error?: string;
  characterCount?: number;
  maxLength?: number;
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

export const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  (
    {
      label,
      hint,
      error,
      characterCount,
      maxLength,
      disabled,
      style,
      onChange,
      value,
      defaultValue,
      ...props
    },
    ref
  ) => {
    const [isFocused, setIsFocused] = React.useState(false);
    const [isHovered, setIsHovered] = React.useState(false);
    const [currentLength, setCurrentLength] = React.useState(
      value ? String(value).length : defaultValue ? String(defaultValue).length : 0
    );
    
    const internalRef = React.useRef<HTMLTextAreaElement>(null);
    
    // Merge refs
    const setRefs = React.useCallback(
      (node: HTMLTextAreaElement) => {
        internalRef.current = node;
        if (typeof ref === 'function') {
          ref(node);
        } else if (ref) {
          ref.current = node;
        }
      },
      [ref]
    );

    const adjustHeight = React.useCallback(() => {
      const textarea = internalRef.current;
      if (!textarea) return;
      
      // Reset height to auto to get the correct scrollHeight
      textarea.style.height = 'auto';
      
      const scrollHeight = textarea.scrollHeight;
      const newHeight = Math.min(Math.max(scrollHeight, 80), 240);
      
      textarea.style.height = `${newHeight}px`;
      textarea.style.overflowY = scrollHeight > 240 ? 'auto' : 'hidden';
    }, []);

    React.useEffect(() => {
      adjustHeight();
    }, [value, adjustHeight]);

    const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      setCurrentLength(e.target.value.length);
      adjustHeight();
      onChange?.(e);
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

    const textareaWrapperStyles: React.CSSProperties = {
      position: 'relative',
      display: 'flex',
      width: '100%',
      backgroundColor: disabled ? 'var(--color-muted)' : 'var(--color-background)',
      borderStyle: 'solid',
      borderColor: getBorderColor(),
      borderWidth: getBorderWidth(),
      borderRadius: 'var(--radius-md)',
      boxSizing: 'border-box',
      transition: 'border-color var(--duration-fast) var(--ease-default), border-width var(--duration-fast) var(--ease-default)',
      cursor: disabled ? 'not-allowed' : 'text',
    };

    const textareaStyles: React.CSSProperties = {
      width: '100%',
      minHeight: '80px',
      maxHeight: '240px',
      backgroundColor: 'transparent',
      border: 'none',
      outline: 'none',
      padding: 'var(--spacing-2)',
      fontSize: 'var(--text-sm)',
      fontWeight: 'var(--font-weight-regular)',
      color: disabled ? 'var(--color-foreground-faint)' : 'var(--color-foreground)',
      cursor: disabled ? 'not-allowed' : 'text',
      boxSizing: 'border-box',
      resize: 'vertical',
      fontFamily: 'var(--font-sans)',
      ...style,
    };

    const bottomRowStyles: React.CSSProperties = {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'flex-start',
      width: '100%',
    };

    const hintStyles: React.CSSProperties = {
      fontSize: 'var(--text-xs)',
      fontWeight: 'var(--font-weight-regular)',
      color: 'var(--color-foreground-faint)',
      flex: 1,
    };

    const errorStyles: React.CSSProperties = {
      display: 'flex',
      alignItems: 'center',
      gap: 'var(--spacing-1)',
      fontSize: 'var(--text-xs)',
      fontWeight: 'var(--font-weight-regular)',
      color: 'var(--color-destructive)',
      flex: 1,
    };

    const charCountStyles: React.CSSProperties = {
      fontSize: 'var(--text-xs)',
      fontWeight: 'var(--font-weight-regular)',
      color: 'var(--color-foreground-faint)',
      marginLeft: 'auto',
      paddingLeft: 'var(--spacing-2)',
    };

    const showCharCount = characterCount !== undefined || maxLength !== undefined;
    const displayCount = characterCount !== undefined ? characterCount : currentLength;

    return (
      <div style={containerStyles}>
        {label && <label style={labelStyles}>{label}</label>}
        
        <div 
          style={textareaWrapperStyles}
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
        >
          <textarea
            ref={setRefs}
            disabled={disabled}
            style={textareaStyles}
            onChange={handleChange}
            value={value}
            defaultValue={defaultValue}
            maxLength={maxLength}
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
        </div>

        {(error || hint || showCharCount) && (
          <div style={bottomRowStyles}>
            {error ? (
              <div style={errorStyles}>
                <AlertCircleIcon />
                <span>{error}</span>
              </div>
            ) : hint ? (
              <div style={hintStyles}>{hint}</div>
            ) : (
              <div style={{ flex: 1 }} />
            )}
            
            {showCharCount && (
              <div style={charCountStyles}>
                {displayCount}{maxLength ? `/${maxLength}` : ''}
              </div>
            )}
          </div>
        )}
        
        <style>{`
          textarea::placeholder {
            color: var(--color-foreground-faint);
          }
        `}</style>
      </div>
    );
  }
);

Textarea.displayName = 'Textarea';

export default Textarea;
