'use client';

import * as React from 'react';

export interface AppShellProps {
  /** Top bar content (60px tall). */
  topBar?: React.ReactNode;
  /** Bottom bar content (40px tall). */
  bottomBar?: React.ReactNode;
  /** Left pane (Chat) — 340px when expanded. */
  chat?: React.ReactNode;
  /** Center pane (Computer) — flexes to fill remaining width. */
  computer?: React.ReactNode;
  /** Right pane (Files) — 320px when expanded. */
  files?: React.ReactNode;
  /** When true, collapses the chat (left) pane to 0px. */
  chatCollapsed?: boolean;
  /** When true, collapses the files (right) pane to 0px. */
  filesCollapsed?: boolean;
  /** Optional toggle handler for the chat pane (⌘\). */
  onToggleChat?: () => void;
  /** Optional toggle handler for the files pane (⌘B). */
  onToggleFiles?: () => void;
  /** Optional className for the outer grid. */
  className?: string;
}

const TOP_BAR_HEIGHT = 60;
const BOTTOM_BAR_HEIGHT = 40;
const CHAT_PANE_WIDTH = 340;
const FILES_PANE_WIDTH = 320;

/**
 * Three-pane application shell using CSS grid.
 *
 * Desktop layout:
 *   ┌────────────────────────────────────────────────────────┐
 *   │                    TopBar (60px)                       │
 *   ├──────────┬─────────────────────────────────┬───────────┤
 *   │  Chat    │           Computer              │   Files   │
 *   │  340px   │            (flex)               │   320px   │
 *   ├──────────┴─────────────────────────────────┴───────────┤
 *   │                  BottomBar (40px)                      │
 *   └────────────────────────────────────────────────────────┘
 *
 * Collapsing a pane sets its grid column width to 0px (no framer-motion
 * here — Group C wires the motion / keyboard shortcuts).
 */
export function AppShell({
  topBar,
  bottomBar,
  chat,
  computer,
  files,
  chatCollapsed = false,
  filesCollapsed = false,
  onToggleChat,
  onToggleFiles,
  className,
}: AppShellProps): React.ReactElement {
  const gridTemplateColumns = [
    chatCollapsed ? '0px' : `${CHAT_PANE_WIDTH}px`,
    '1fr',
    filesCollapsed ? '0px' : `${FILES_PANE_WIDTH}px`,
  ].join(' ');

  const shellStyle: React.CSSProperties = {
    display: 'grid',
    gridTemplateRows: `${TOP_BAR_HEIGHT}px 1fr ${BOTTOM_BAR_HEIGHT}px`,
    height: '100vh',
    width: '100vw',
    backgroundColor: 'var(--color-background)',
    color: 'var(--color-foreground)',
    overflow: 'hidden',
  };

  const topBarStyle: React.CSSProperties = {
    gridRow: '1',
    gridColumn: '1 / -1',
    height: `${TOP_BAR_HEIGHT}px`,
    borderBottom: '1px solid var(--color-border)',
    backgroundColor: 'var(--color-background)',
    display: 'flex',
    alignItems: 'center',
  };

  const bodyStyle: React.CSSProperties = {
    gridRow: '2',
    gridColumn: '1 / -1',
    display: 'grid',
    gridTemplateColumns,
    minHeight: 0,
    overflow: 'hidden',
  };

  const chatPaneStyle: React.CSSProperties = {
    backgroundColor: 'var(--color-background-elevated)',
    borderRight: chatCollapsed ? 'none' : '1px solid var(--color-border)',
    overflow: 'hidden',
    minWidth: 0,
  };

  const computerPaneStyle: React.CSSProperties = {
    backgroundColor: 'var(--color-background)',
    overflow: 'hidden',
    minWidth: 0,
  };

  const filesPaneStyle: React.CSSProperties = {
    backgroundColor: 'var(--color-background-elevated)',
    borderLeft: filesCollapsed ? 'none' : '1px solid var(--color-border)',
    overflow: 'hidden',
    minWidth: 0,
  };

  const bottomBarStyle: React.CSSProperties = {
    gridRow: '3',
    gridColumn: '1 / -1',
    height: `${BOTTOM_BAR_HEIGHT}px`,
    borderTop: '1px solid var(--color-border)',
    backgroundColor: 'var(--color-background)',
    display: 'flex',
    alignItems: 'center',
  };

  return (
    <div
      className={className}
      style={shellStyle}
      data-app-shell=""
      data-chat-collapsed={chatCollapsed ? 'true' : 'false'}
      data-files-collapsed={filesCollapsed ? 'true' : 'false'}
    >
      <div style={topBarStyle} data-slot="top-bar">
        {topBar}
      </div>
      <div style={bodyStyle} data-slot="body">
        <section
          style={chatPaneStyle}
          data-slot="chat"
          onDoubleClick={onToggleChat}
          data-collapsed={chatCollapsed ? '' : undefined}
          aria-hidden={chatCollapsed || undefined}
        >
          {chat}
        </section>
        <section style={computerPaneStyle} data-slot="computer">
          {computer}
        </section>
        <section
          style={filesPaneStyle}
          data-slot="files"
          onDoubleClick={onToggleFiles}
          data-collapsed={filesCollapsed ? '' : undefined}
          aria-hidden={filesCollapsed || undefined}
        >
          {files}
        </section>
      </div>
      <div style={bottomBarStyle} data-slot="bottom-bar">
        {bottomBar}
      </div>
    </div>
  );
}

export default AppShell;
