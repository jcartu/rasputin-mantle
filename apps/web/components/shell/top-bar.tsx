'use client';

import * as React from 'react';
import { Share2 } from 'lucide-react';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Avatar } from '../ui/avatar';

export type TopBarStatus = 'idle' | 'running' | 'waiting' | 'done' | 'error';

export interface TopBarProps extends React.HTMLAttributes<HTMLDivElement> {
  taskTitle?: string;
  status?: TopBarStatus;
  statusLabel?: string;
  userInitials?: string;
  userAvatarSrc?: string;
  userName?: string;
  onShare?: () => void;
  onUserMenu?: () => void;
}

type BadgeVariant = 'default' | 'success' | 'warn' | 'error' | 'outline';

interface StatusConfig {
  label: string;
  variant: BadgeVariant;
}

const STATUS_CONFIG: Record<TopBarStatus, StatusConfig> = {
  idle: { label: 'Idle', variant: 'default' },
  running: { label: 'Running', variant: 'default' },
  waiting: { label: 'Waiting', variant: 'warn' },
  done: { label: 'Done', variant: 'success' },
  error: { label: 'Error', variant: 'error' },
};

export const TopBar = React.forwardRef<HTMLDivElement, TopBarProps>(
  (
    {
      taskTitle,
      status = 'idle',
      statusLabel,
      userInitials,
      userAvatarSrc,
      userName,
      onShare,
      onUserMenu,
      style,
      className,
      ...props
    },
    ref,
  ) => {
    const config = STATUS_CONFIG[status];
    const displayLabel = statusLabel ?? config.label;

    return (
      <header
        ref={ref}
        role="banner"
        style={{
          height: '60px',
          display: 'grid',
          gridTemplateColumns: '1fr auto 1fr',
          alignItems: 'center',
          padding: '0 var(--spacing-4)',
          backgroundColor: 'var(--color-background-elevated)',
          borderBottom: '1px solid var(--color-border)',
          boxSizing: 'border-box',
          flexShrink: 0,
          ...style,
        }}
        className={className}
        {...props}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--spacing-3)',
            minWidth: 0,
          }}
        >
          <span
            style={{
              fontSize: 'var(--text-xl)',
              fontWeight: 'var(--font-weight-semibold)',
              color: 'var(--color-accent)',
              letterSpacing: '-0.01em',
              lineHeight: 1,
            }}
          >
            Mantle
          </span>
          {taskTitle ? (
            <>
              <span
                aria-hidden="true"
                style={{
                  width: '1px',
                  height: '16px',
                  backgroundColor: 'var(--color-border)',
                }}
              />
              <span
                style={{
                  fontSize: 'var(--text-sm)',
                  color: 'var(--color-foreground-muted)',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                  minWidth: 0,
                }}
                title={taskTitle}
              >
                {taskTitle}
              </span>
            </>
          ) : null}
        </div>

        <div style={{ display: 'flex', justifyContent: 'center' }}>
          <Badge
            variant={config.variant}
            size="md"
            aria-label={`Status: ${displayLabel}`}
            style={
              status === 'running'
                ? {
                    backgroundColor: 'var(--color-accent-subtle)',
                    color: 'var(--color-accent)',
                  }
                : undefined
            }
          >
            {status === 'running' ? (
              <span
                aria-hidden="true"
                style={{
                  width: '6px',
                  height: '6px',
                  borderRadius: 'var(--radius-full)',
                  backgroundColor: 'var(--color-accent)',
                  display: 'inline-block',
                }}
              />
            ) : null}
            {displayLabel}
          </Badge>
        </div>

        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'flex-end',
            gap: 'var(--spacing-2)',
          }}
        >
          <Button
            variant="ghost"
            size="md"
            iconOnly={<Share2 size={16} strokeWidth={1.5} />}
            aria-label="Share task"
            onClick={onShare}
          />
          <button
            type="button"
            aria-label={userName ? `User menu for ${userName}` : 'User menu'}
            onClick={onUserMenu}
            style={{
              background: 'transparent',
              border: 'none',
              padding: 0,
              cursor: 'pointer',
              borderRadius: 'var(--radius-full)',
              display: 'inline-flex',
            }}
          >
            <Avatar
              size="md"
              src={userAvatarSrc}
              initials={userInitials}
              alt={userName}
            />
          </button>
        </div>
      </header>
    );
  },
);

TopBar.displayName = 'TopBar';

export default TopBar;
