'use client';

import * as React from 'react';
import { use } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ComputerView, type BrowserTab } from '@/components/session/computer-view';
import { FileTree, type SandboxFileEntry } from '@/components/session/file-tree';
import { ArtifactViewer } from '@/components/session/artifact-viewer';

interface PageParams {
  id: string;
}

interface SessionPageProps {
  params: Promise<PageParams>;
}

const CHAT_PANE_WIDTH = 340;
const FILES_PANE_WIDTH = 320;

/**
 * The chat stream component is built in parallel under P3 Frontend A. We
 * dynamically resolve it at runtime to keep this page decoupled from that
 * branch's exact export surface; if the module is unavailable a typed
 * fallback renders so the route still mounts cleanly.
 */
interface ChatStreamProps {
  sessionId: string;
}

function ChatStreamFallback({ sessionId }: ChatStreamProps): React.ReactElement {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--spacing-2)',
        padding: 'var(--spacing-4)',
        height: '100%',
        color: 'var(--color-foreground-muted)',
        fontSize: 'var(--text-sm)',
      }}
    >
      <div
        style={{
          fontSize: 'var(--text-xs)',
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
          color: 'var(--color-foreground-faint)',
          fontWeight: 'var(--font-weight-medium)',
        }}
      >
        Session
      </div>
      <div style={{ fontFamily: 'var(--font-mono)', color: 'var(--color-foreground)' }}>
        {sessionId}
      </div>
      <p style={{ margin: 0, lineHeight: 1.6 }}>
        Chat stream not yet wired into this build. Once the chat module ships
        this surface will render the live agent conversation.
      </p>
    </div>
  );
}

const ChatStream = React.lazy(async () => {
  try {
    const mod: { ChatStream?: React.ComponentType<ChatStreamProps>; default?: React.ComponentType<ChatStreamProps> } =
      await import('@/components/session/chat-stream');
    const Component = mod.ChatStream ?? mod.default;
    if (Component) return { default: Component };
  } catch {
    /* Module not yet available — fall through to fallback. */
  }
  return { default: ChatStreamFallback };
});

export default function SessionPage({ params }: SessionPageProps): React.ReactElement {
  const { id: sessionId } = use(params);

  const [chatCollapsed, setChatCollapsed] = React.useState(false);
  const [filesCollapsed, setFilesCollapsed] = React.useState(false);
  const [activeFile, setActiveFile] = React.useState<string | null>(null);
  const [isControlTaken, setIsControlTaken] = React.useState(false);
  const [tabs, setTabs] = React.useState<BrowserTab[]>([]);
  const [activeTabId, setActiveTabId] = React.useState<string | undefined>(undefined);

  // Restore collapse state from localStorage (session-scoped).
  React.useEffect(() => {
    if (typeof window === 'undefined') return;
    try {
      const stored = window.localStorage.getItem(`mantle:session:${sessionId}:panes`);
      if (stored) {
        const parsed = JSON.parse(stored) as { chat?: boolean; files?: boolean };
        if (typeof parsed.chat === 'boolean') setChatCollapsed(parsed.chat);
        if (typeof parsed.files === 'boolean') setFilesCollapsed(parsed.files);
      }
    } catch {
      /* ignore malformed storage */
    }
  }, [sessionId]);

  React.useEffect(() => {
    if (typeof window === 'undefined') return;
    try {
      window.localStorage.setItem(
        `mantle:session:${sessionId}:panes`,
        JSON.stringify({ chat: chatCollapsed, files: filesCollapsed }),
      );
    } catch {
      /* storage quota — ignore */
    }
  }, [chatCollapsed, filesCollapsed, sessionId]);

  // Keyboard shortcuts: ⌘\ chat, ⌘B files, Esc closes artifact.
  React.useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const mod = e.metaKey || e.ctrlKey;
      if (!mod) return;
      if (e.key === '\\') {
        e.preventDefault();
        setChatCollapsed((v) => !v);
      } else if (e.key.toLowerCase() === 'b') {
        e.preventDefault();
        setFilesCollapsed((v) => !v);
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  const handleFileOpen = React.useCallback((file: SandboxFileEntry) => {
    if (file.kind === 'file') {
      setActiveFile(file.path);
    }
  }, []);

  const handleArtifactClose = React.useCallback(() => {
    setActiveFile(null);
  }, []);

  const handleTakeControl = React.useCallback((value: boolean) => {
    setIsControlTaken(value);
  }, []);

  const handleScreenshot = React.useCallback(() => {
    // Defer to the gateway — it owns sandbox-side capture.
    void fetch(`/api/sandbox/${encodeURIComponent(sessionId)}/screenshot`, {
      method: 'POST',
    }).catch(() => {
      /* user-visible failures will be surfaced through toasts in P3 Frontend C */
    });
  }, [sessionId]);

  const handleTabNew = React.useCallback(() => {
    const id = `tab-${Date.now().toString(36)}`;
    const next: BrowserTab = { id, title: 'New tab' };
    setTabs((prev) => [...prev, next]);
    setActiveTabId(id);
  }, []);

  const handleTabClose = React.useCallback(
    (tabId: string) => {
      setTabs((prev) => prev.filter((t) => t.id !== tabId));
      if (activeTabId === tabId) {
        setActiveTabId(undefined);
      }
    },
    [activeTabId],
  );

  const handleTabSelect = React.useCallback((tabId: string) => {
    setActiveTabId(tabId);
  }, []);

  const gridTemplateColumns = [
    chatCollapsed ? '0px' : `${CHAT_PANE_WIDTH}px`,
    '1fr',
    filesCollapsed ? '0px' : `${FILES_PANE_WIDTH}px`,
  ].join(' ');

  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns,
        height: '100%',
        width: '100%',
        backgroundColor: 'var(--color-background)',
        color: 'var(--color-foreground)',
        overflow: 'hidden',
        transition: 'grid-template-columns var(--duration-default) var(--ease-default)',
      }}
      data-session-id={sessionId}
    >
      {/* Left: Chat */}
      <section
        aria-label="Chat"
        aria-hidden={chatCollapsed || undefined}
        style={{
          position: 'relative',
          minWidth: 0,
          height: '100%',
          backgroundColor: 'var(--color-background-elevated)',
          borderRight: chatCollapsed ? 'none' : '1px solid var(--color-border)',
          overflow: 'hidden',
        }}
      >
        {!chatCollapsed ? (
          <div
            style={{
              position: 'relative',
              height: '100%',
              width: CHAT_PANE_WIDTH,
              minWidth: CHAT_PANE_WIDTH,
              display: 'flex',
              flexDirection: 'column',
            }}
          >
            <div
              style={{
                position: 'absolute',
                top: 'var(--spacing-2)',
                right: 'var(--spacing-2)',
                zIndex: 2,
              }}
            >
              <Button
                variant="ghost"
                size="sm"
                iconOnly={<ChevronLeft size={16} strokeWidth={1.5} />}
                aria-label="Collapse chat pane"
                onClick={() => setChatCollapsed(true)}
              />
            </div>
            <div
              style={{
                flex: 1,
                minHeight: 0,
                overflow: 'hidden',
              }}
            >
              <React.Suspense
                fallback={
                  <div
                    style={{
                      padding: 'var(--spacing-4)',
                      fontSize: 'var(--text-sm)',
                      color: 'var(--color-foreground-muted)',
                    }}
                  >
                    Loading chat…
                  </div>
                }
              >
                <ChatStream sessionId={sessionId} />
              </React.Suspense>
            </div>
          </div>
        ) : null}
      </section>

      {/* Center: Computer */}
      <section
        aria-label="Computer view"
        style={{
          position: 'relative',
          minWidth: 0,
          height: '100%',
          backgroundColor: 'var(--color-background)',
          overflow: 'hidden',
        }}
      >
        {chatCollapsed ? (
          <div
            style={{
              position: 'absolute',
              top: 'var(--spacing-2)',
              left: 'var(--spacing-2)',
              zIndex: 5,
            }}
          >
            <Button
              variant="secondary"
              size="sm"
              iconOnly={<ChevronRight size={14} strokeWidth={1.5} />}
              aria-label="Expand chat pane"
              onClick={() => setChatCollapsed(false)}
            />
          </div>
        ) : null}
        {filesCollapsed ? (
          <div
            style={{
              position: 'absolute',
              top: 'var(--spacing-2)',
              right: 'var(--spacing-2)',
              zIndex: 5,
            }}
          >
            <Button
              variant="secondary"
              size="sm"
              iconOnly={<ChevronLeft size={14} strokeWidth={1.5} />}
              aria-label="Expand files pane"
              onClick={() => setFilesCollapsed(false)}
            />
          </div>
        ) : null}
        <ComputerView
          sessionId={sessionId}
          isControlTaken={isControlTaken}
          onTakeControl={handleTakeControl}
          onScreenshot={handleScreenshot}
          tabs={tabs}
          activeTabId={activeTabId}
          onTabSelect={handleTabSelect}
          onTabClose={handleTabClose}
          onTabNew={handleTabNew}
        />
      </section>

      {/* Right: Files */}
      <section
        aria-label="Files"
        aria-hidden={filesCollapsed || undefined}
        style={{
          position: 'relative',
          minWidth: 0,
          height: '100%',
          backgroundColor: 'var(--color-background-elevated)',
          borderLeft: filesCollapsed ? 'none' : '1px solid var(--color-border)',
          overflow: 'hidden',
        }}
      >
        {!filesCollapsed ? (
          <div
            style={{
              position: 'relative',
              height: '100%',
              width: FILES_PANE_WIDTH,
              minWidth: FILES_PANE_WIDTH,
              display: 'flex',
              flexDirection: 'column',
            }}
          >
            <div
              style={{
                position: 'absolute',
                top: 'var(--spacing-2)',
                right: 'var(--spacing-2)',
                zIndex: 2,
              }}
            >
              <Button
                variant="ghost"
                size="sm"
                iconOnly={<ChevronRight size={16} strokeWidth={1.5} />}
                aria-label="Collapse files pane"
                onClick={() => setFilesCollapsed(true)}
              />
            </div>
            <FileTree sessionId={sessionId} onFileOpen={handleFileOpen} />
          </div>
        ) : null}
      </section>

      <ArtifactViewer
        sessionId={sessionId}
        filePath={activeFile}
        onClose={handleArtifactClose}
      />
    </div>
  );
}
