'use client';

import * as React from 'react';
import { Maximize2, Minimize2 } from 'lucide-react';
import { Switch } from '../ui/switch';
import { Button } from '../ui/button';

export interface ComputerPaneProps extends React.HTMLAttributes<HTMLElement> {
  userInControl?: boolean;
  defaultUserInControl?: boolean;
  onUserInControlChange?: (value: boolean) => void;
  fullscreen?: boolean;
  onFullscreenToggle?: (value: boolean) => void;
  children?: React.ReactNode;
}

export const ComputerPane = React.forwardRef<HTMLElement, ComputerPaneProps>(
  (
    {
      userInControl,
      defaultUserInControl = false,
      onUserInControlChange,
      fullscreen = false,
      onFullscreenToggle,
      children,
      style,
      className,
      ...props
    },
    ref,
  ) => {
    const isControlled = userInControl !== undefined;
    const [uncontrolled, setUncontrolled] = React.useState<boolean>(defaultUserInControl);
    const value = isControlled ? userInControl : uncontrolled;

    const handleChange = (next: boolean) => {
      if (!isControlled) {
        setUncontrolled(next);
      }
      onUserInControlChange?.(next);
    };

    const handleFullscreen = () => {
      onFullscreenToggle?.(!fullscreen);
    };

    return (
      <section
        ref={ref as React.Ref<HTMLElement>}
        aria-label="Computer view"
        style={{
          flex: 1,
          minWidth: '400px',
          height: '100%',
          backgroundColor: 'var(--color-background)',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          boxSizing: 'border-box',
          ...style,
        }}
        className={className}
        {...props}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: 'var(--spacing-2) var(--spacing-3)',
            borderBottom: '1px solid var(--color-border)',
            backgroundColor: 'var(--color-background-elevated)',
            flexShrink: 0,
            gap: 'var(--spacing-3)',
          }}
        >
          <label
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 'var(--spacing-2)',
              cursor: 'pointer',
              fontSize: 'var(--text-xs)',
              color: 'var(--color-foreground-muted)',
              userSelect: 'none',
            }}
          >
            <Switch
              size="sm"
              checked={value}
              onCheckedChange={handleChange}
              aria-label="Take control"
            />
            <span>Take control</span>
          </label>

          <Button
            variant="ghost"
            size="sm"
            iconOnly={
              fullscreen ? (
                <Minimize2 size={14} strokeWidth={1.5} />
              ) : (
                <Maximize2 size={14} strokeWidth={1.5} />
              )
            }
            aria-label={fullscreen ? 'Exit fullscreen' : 'Enter fullscreen'}
            aria-pressed={fullscreen}
            onClick={handleFullscreen}
          />
        </div>

        <div
          style={{
            flex: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            overflow: 'hidden',
            position: 'relative',
            backgroundColor: 'var(--color-background)',
          }}
        >
          {children ?? (
            <p
              style={{
                fontSize: 'var(--text-sm)',
                color: 'var(--color-foreground-muted)',
                textAlign: 'center',
                margin: 0,
                padding: 'var(--spacing-6)',
              }}
            >
              Computer view will appear here
            </p>
          )}
        </div>
      </section>
    );
  },
);

ComputerPane.displayName = 'ComputerPane';

export default ComputerPane;
