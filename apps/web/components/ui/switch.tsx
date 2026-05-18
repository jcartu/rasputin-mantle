import * as React from 'react';

export interface SwitchProps extends Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, 'onChange'> {
  checked?: boolean;
  defaultChecked?: boolean;
  onCheckedChange?: (checked: boolean) => void;
  size?: 'sm' | 'md';
}

export const Switch = React.forwardRef<HTMLButtonElement, SwitchProps>(
  ({ checked, defaultChecked, onCheckedChange, size = 'md', disabled, className, style, ...props }, ref) => {
    const [uncontrolledChecked, setUncontrolledChecked] = React.useState(defaultChecked || false);
    const isControlled = checked !== undefined;
    const isChecked = isControlled ? checked : uncontrolledChecked;

    const [isHovered, setIsHovered] = React.useState(false);

    const toggle = () => {
      if (disabled) return;
      const newValue = !isChecked;
      if (!isControlled) {
        setUncontrolledChecked(newValue);
      }
      onCheckedChange?.(newValue);
    };

    const trackWidth = size === 'sm' ? '32px' : '40px';
    const trackHeight = size === 'sm' ? '18px' : '22px';
    const thumbSize = size === 'sm' ? '12px' : '16px';
    
    // 4px offset from left/right
    // For left: 4px
    // For right: trackWidth - thumbSize - 4px
    const offsetLeft = 4;
    const offsetRight = (size === 'sm' ? 32 : 40) - (size === 'sm' ? 12 : 16) - 4;

    return (
      <button
        type="button"
        role="switch"
        aria-checked={isChecked}
        disabled={disabled}
        ref={ref}
        onClick={toggle}
        onMouseEnter={(e) => {
          setIsHovered(true);
          props.onMouseEnter?.(e);
        }}
        onMouseLeave={(e) => {
          setIsHovered(false);
          props.onMouseLeave?.(e);
        }}
        style={{
          position: 'relative',
          display: 'inline-flex',
          alignItems: 'center',
          width: trackWidth,
          height: trackHeight,
          borderRadius: 'var(--radius-full)',
          backgroundColor: isChecked ? 'var(--color-accent)' : 'var(--color-muted)',
          border: 'none',
          outline: 'none',
          cursor: disabled ? 'not-allowed' : 'pointer',
          opacity: disabled ? 0.5 : 1,
          transition: 'background-color var(--duration-default) var(--ease-default), filter var(--duration-default) var(--ease-default)',
          filter: isHovered && !disabled ? 'brightness(1.08)' : 'none',
          padding: 0,
          ...style,
        }}
        className={className}
        {...props}
      >
        <span
          style={{
            display: 'block',
            width: thumbSize,
            height: thumbSize,
            backgroundColor: 'oklch(100% 0 0)', /* Thumb always white per spec */
            borderRadius: 'var(--radius-full)',
            boxShadow: 'var(--shadow-sm)',
            transition: 'transform var(--duration-default) var(--ease-default)',
            transform: `translateX(${isChecked ? offsetRight : offsetLeft}px)`,
          }}
        />
      </button>
    );
  }
);
Switch.displayName = 'Switch';
