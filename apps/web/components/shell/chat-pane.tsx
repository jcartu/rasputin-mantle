'use client';

import * as React from 'react';
import { AnimatePresence, motion, type Variants } from 'framer-motion';

const STORAGE_KEY = 'mantle-chat-collapsed';
const DEFAULT_WIDTH = 340;
const MIN_WIDTH = 280;
const MAX_WIDTH = 480;

export interface ChatPaneProps extends React.HTMLAttributes<HTMLElement> {
  collapsed?: boolean;
  defaultCollapsed?: boolean;
  onCollapsedChange?: (collapsed: boolean) => void;
  width?: number;
  children?: React.ReactNode;
}

export const panelCollapseVariants: Variants = {
  collapsed: {
    width: 0,
    opacity: 0,
    transition: { duration: 0.2, ease: [0.16, 1, 0.3, 1] },
  },
  expanded: {
    width: 'var(--panel-width)',
    opacity: 1,
    transition: { duration: 0.2, ease: [0, 0, 0.2, 1] },
  },
};

function readStoredCollapsed(): boolean | undefined {
  if (typeof window === 'undefined') return undefined;
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (raw === null) return undefined;
    return raw === 'true';
  } catch {
    return undefined;
  }
}

function writeStoredCollapsed(value: boolean): void {
  if (typeof window === 'undefined') return;
  try {
    window.localStorage.setItem(STORAGE_KEY, value ? 'true' : 'false');
  } catch {
    /* localStorage unavailable; ignore */
  }
}

export const ChatPane = React.forwardRef<HTMLElement, ChatPaneProps>(
  (
    {
      collapsed,
      defaultCollapsed = false,
      onCollapsedChange,
      width = DEFAULT_WIDTH,
      children,
      style,
      className,
      ...props
    },
    ref,
  ) => {
    const isControlled = collapsed !== undefined;
    const [uncontrolled, setUncontrolled] = React.useState<boolean>(defaultCollapsed);
    const [hydrated, setHydrated] = React.useState(false);

    React.useEffect(() => {
      const stored = readStoredCollapsed();
      if (stored !== undefined && !isControlled) {
        setUncontrolled(stored);
      }
      setHydrated(true);
    }, [isControlled]);

    const isCollapsed = isControlled ? collapsed : uncontrolled;

    React.useEffect(() => {
      if (!hydrated) return;
      if (!isControlled) {
        writeStoredCollapsed(uncontrolled);
      }
    }, [uncontrolled, isControlled, hydrated]);

    React.useEffect(() => {
      if (!hydrated) return;
      if (isControlled && collapsed !== undefined) {
        writeStoredCollapsed(collapsed);
      }
    }, [collapsed, isControlled, hydrated]);

    React.useEffect(() => {
      onCollapsedChange?.(Boolean(isCollapsed));
    }, [isCollapsed, onCollapsedChange]);

    const clampedWidth = Math.min(Math.max(width, MIN_WIDTH), MAX_WIDTH);

    return (
      <AnimatePresence initial={false}>
        {!isCollapsed && (
          <motion.aside
            ref={ref as React.Ref<HTMLElement>}
            key="chat-pane"
            role="complementary"
            aria-label="Chat"
            initial="collapsed"
            animate="expanded"
            exit="collapsed"
            variants={panelCollapseVariants}
            style={{
              ['--panel-width' as string]: `${clampedWidth}px`,
              minWidth: 0,
              maxWidth: `${MAX_WIDTH}px`,
              height: '100%',
              backgroundColor: 'var(--color-background-elevated)',
              borderRight: '1px solid var(--color-border)',
              boxSizing: 'border-box',
              overflow: 'hidden',
              display: 'flex',
              flexDirection: 'column',
              flexShrink: 0,
              ...style,
            }}
            className={className}
            {...(props as Record<string, unknown>)}
          >
            <div
              style={{
                width: `${clampedWidth}px`,
                minWidth: `${MIN_WIDTH}px`,
                maxWidth: `${MAX_WIDTH}px`,
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                overflow: 'hidden',
              }}
            >
              <div
                style={{
                  flex: 1,
                  overflowY: 'auto',
                  overflowX: 'hidden',
                  padding: 'var(--spacing-3) var(--spacing-2)',
                  color: 'var(--color-foreground)',
                }}
              >
                {children}
              </div>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>
    );
  },
);

ChatPane.displayName = 'ChatPane';

export default ChatPane;
