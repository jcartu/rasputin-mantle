'use client';

import * as React from 'react';
import { AppShell } from '@/components/shell/app-shell';
import { useTheme } from '@/context/theme-context';

/**
 * Route group layout for the `(app)` segment. Wraps every page under
 * `app/(app)/*` in the three-pane shell.
 *
 * Pane content is rendered by individual route components in Group B.
 * Keyboard shortcuts for pane collapse (⌘\, ⌘/, ⌘B) and the mobile
 * tab bar are wired in Group C.
 */
export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}): React.ReactElement {
  // `useTheme` is consumed here so the layout participates in the theme
  // context — Group C will read `theme` to flip the topbar icon.
  const { theme } = useTheme();

  const [chatCollapsed, setChatCollapsed] = React.useState<boolean>(false);
  const [filesCollapsed, setFilesCollapsed] = React.useState<boolean>(false);

  const toggleChat = React.useCallback(() => {
    setChatCollapsed((prev) => !prev);
  }, []);

  const toggleFiles = React.useCallback(() => {
    setFilesCollapsed((prev) => !prev);
  }, []);

  // Surface current theme for future Group C consumers (devtools).
  React.useDebugValue({ theme });

  return (
    <AppShell
      chatCollapsed={chatCollapsed}
      filesCollapsed={filesCollapsed}
      onToggleChat={toggleChat}
      onToggleFiles={toggleFiles}
      computer={children}
    />
  );
}
