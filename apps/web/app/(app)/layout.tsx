'use client';

import * as React from 'react';
import { AppShell } from '@/components/shell/app-shell';
import { MobileTabs, type MobileTab } from '@/components/shell/mobile-tabs';
import { useTheme } from '@/context/theme-context';
import { useKeyboardShortcuts } from '@/hooks/use-keyboard';

/**
 * Route group layout for the `(app)` segment. Wraps every page under
 * `app/(app)/*` in the three-pane shell.
 *
 * Desktop (>= 1025px): three-pane grid with resizable panes.
 * Tablet (769–1024px): two-pane + files drawer.
 * Mobile (<= 768px): single-pane stack with bottom tab bar.
 */
export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}): React.ReactElement {
  const { theme } = useTheme();

  // Pane collapse state (persisted to localStorage)
  const [chatCollapsed, setChatCollapsed] = React.useState<boolean>(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('mantle-chat-collapsed') === 'true';
    }
    return false;
  });
  const [filesCollapsed, setFilesCollapsed] = React.useState<boolean>(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('mantle-files-collapsed') === 'true';
    }
    return false;
  });

  // Pane widths (persisted to localStorage, clamped by AppShell)
  const [chatWidth, setChatWidth] = React.useState<number>(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('mantle-chat-width');
      if (stored) {
        const n = parseInt(stored, 10);
        if (n >= 280 && n <= 480) return n;
      }
    }
    return 340;
  });
  const [filesWidth, setFilesWidth] = React.useState<number>(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('mantle-files-width');
      if (stored) {
        const n = parseInt(stored, 10);
        if (n >= 240 && n <= 480) return n;
      }
    }
    return 320;
  });

  // Mobile active tab
  const [mobileTab, setMobileTab] = React.useState<MobileTab>('chat');

  // Persist collapse state
  React.useEffect(() => {
    localStorage.setItem('mantle-chat-collapsed', String(chatCollapsed));
  }, [chatCollapsed]);
  React.useEffect(() => {
    localStorage.setItem('mantle-files-collapsed', String(filesCollapsed));
  }, [filesCollapsed]);

  // Persist pane widths
  React.useEffect(() => {
    localStorage.setItem('mantle-chat-width', String(chatWidth));
  }, [chatWidth]);
  React.useEffect(() => {
    localStorage.setItem('mantle-files-width', String(filesWidth));
  }, [filesWidth]);

  const toggleChat = React.useCallback(() => {
    setChatCollapsed((prev) => !prev);
  }, []);

  const toggleFiles = React.useCallback(() => {
    setFilesCollapsed((prev) => !prev);
  }, []);

  // Keyboard shortcuts
  useKeyboardShortcuts({
    'mod+\\': toggleChat,
    'mod+b': toggleFiles,
    'mod+k': () => {
      // Command palette — will be wired in P3/P4
    },
  });

  // Surface current theme for consumers.
  React.useDebugValue({ theme });

  return (
    <>
      <AppShell
        chatCollapsed={chatCollapsed}
        filesCollapsed={filesCollapsed}
        chatWidth={chatWidth}
        filesWidth={filesWidth}
        onToggleChat={toggleChat}
        onToggleFiles={toggleFiles}
        onResizeChat={setChatWidth}
        onResizeFiles={setFilesWidth}
        computer={children}
      />
      <MobileTabs active={mobileTab} onChange={setMobileTab} />
    </>
  );
}
