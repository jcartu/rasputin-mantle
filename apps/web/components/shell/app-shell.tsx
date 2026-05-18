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
  /** Chat pane width (px). Clamped 280–480. */
  chatWidth?: number;
  /** Files pane width (px). Clamped 240–480. */
  filesWidth?: number;
  /** Optional toggle handler for the chat pane (⌘\). */
  onToggleChat?: () => void;
  /** Optional toggle handler for the files pane (⌘B). */
  onToggleFiles?: () => void;
  /** Optional resize handler for chat pane. */
  onResizeChat?: (width: number) => void;
  /** Optional resize handler for files pane. */
  onResizeFiles?: (width: number) => void;
  /** Optional className for the outer grid. */
  className?: string;
}

const TOP_BAR_HEIGHT = 60;
const BOTTOM_BAR_HEIGHT = 40;
const DEFAULT_CHAT_WIDTH = 340;
const DEFAULT_FILES_WIDTH = 320;
const CHAT_MIN = 280;
const CHAT_MAX = 480;
const FILES_MIN = 240;
const FILES_MAX = 480;

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
 * Resizable panes: 4px drag handles between panes.
 * Handles show --color-border default, --color-accent on hover.
 */
export function AppShell({
  topBar,
  bottomBar,
  chat,
  computer,
  files,
  chatCollapsed = false,
  filesCollapsed = false,
  chatWidth = DEFAULT_CHAT_WIDTH,
  filesWidth = DEFAULT_FILES_WIDTH,
  onToggleChat,
  onToggleFiles,
  onResizeChat,
  onResizeFiles,
  className,
}: AppShellProps): React.ReactElement {
  const clampedChat = Math.min(Math.max(chatWidth, CHAT_MIN), CHAT_MAX);
  const clampedFiles = Math.min(Math.max(filesWidth, FILES_MIN), FILES_MAX);

  const chatCol = chatCollapsed ? '0px' : `${clampedChat}px`;
  const filesCol = filesCollapsed ? '0px' : `${clampedFiles}px`;

  const gridTemplateColumns = `${chatCol} 1fr ${filesCol}`;

  const shellStyle: React.CSSProperties = {
    display: 'grid',
    gridTemplateRows: `${TOP_BAR_HEIGHT}px 1fr ${BOTTOM_BAR_HEIGHT}px`,
    height: '100vh',
    width: '100vw',
    backgroundColor: 'var(--color-background)',
    color: 'var(--color-foreground)',
    overflow: 'hidden',
    '--chat-pane-width': `${clampedChat}px`,
    '--files-pane-width': `${clampedFiles}px`,
  } as React.CSSProperties;

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

  // ── Resize handle ──────────────────────────────────────────
  const handleStyle: React.CSSProperties = {
    width: '4px',
    cursor: 'col-resize',
    backgroundColor: 'var(--color-border)',
    transition: 'background-color var(--duration-default) var(--ease-default)',
    gridRow: '2',
    zIndex: 10,
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

        {/* Chat resize handle */}
        {!chatCollapsed && onResizeChat && (
          <ResizeHandle
            style={{ ...handleStyle, gridColumn: '2' }}
            onResize={onResizeChat}
            min={CHAT_MIN}
            max={CHAT_MAX}
            defaultWidth={clampedChat}
          />
        )}

        <section style={computerPaneStyle} data-slot="computer">
          {computer}
        </section>

        {/* Files resize handle */}
        {!filesCollapsed && onResizeFiles && (
          <ResizeHandle
            style={{ ...handleStyle, gridColumn: '3' }}
            onResize={onResizeFiles}
            min={FILES_MIN}
            max={FILES_MAX}
            defaultWidth={clampedFiles}
          />
        )}

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

// ── Resize Handle Component ──────────────────────────────────

interface ResizeHandleProps {
  style: React.CSSProperties;
  onResize: (width: number) => void;
  min: number;
  max: number;
  defaultWidth: number;
}

function ResizeHandle({ style, onResize, min, max, defaultWidth }: ResizeHandleProps) {
  const isDragging = React.useRef(false);
  const startX = React.useRef(0);
  const startWidth = React.useRef(0);

  const handleMouseDown = React.useCallback(
    (e: React.MouseEvent) => {
      isDragging.current = true;
      startX.current = e.clientX;
      startWidth.current = defaultWidth;
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
      e.preventDefault();
    },
    [defaultWidth],
  );

  const handleMouseMove = React.useCallback(
    (e: MouseEvent) => {
      if (!isDragging.current) return;
      const delta = e.clientX - startX.current;
      const newWidth = Math.min(Math.max(startWidth.current + delta, min), max);
      onResize(newWidth);
    },
    [onResize, min, max],
  );

  const handleMouseUp = React.useCallback(() => {
    isDragging.current = false;
    document.body.style.cursor = '';
    document.body.style.userSelect = '';
    window.removeEventListener('mousemove', handleMouseMove);
    window.removeEventListener('mouseup', handleMouseUp);
  }, [handleMouseMove]);

  return (
    <div
      role="separator"
      aria-orientation="vertical"
      tabIndex={0}
      onMouseDown={handleMouseDown}
      onMouseEnter={(e) => {
        e.currentTarget.style.backgroundColor = 'var(--color-accent)';
      }}
      onMouseLeave={(e) => {
        if (!isDragging.current) {
          e.currentTarget.style.backgroundColor = 'var(--color-border)';
        }
      }}
      style={style}
    />
  );
}
