'use client';

import { AnimatePresence, motion } from 'framer-motion';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

export interface CommandItem {
  id: string;
  label: string;
  shortcut?: string;
  onSelect: () => void;
}

export interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  commands?: CommandItem[];
}

/**
 * Build the default command list. Callbacks for the toggle/open actions
 * are provided by the caller, which keeps the palette decoupled from the
 * shell state.
 */
export function buildDefaultCommands(handlers: {
  onNewTask: () => void;
  onToggleTheme: () => void;
  onToggleChat: () => void;
  onToggleFiles: () => void;
  onOpenDocs: () => void;
  onSignOut: () => void;
}): CommandItem[] {
  return [
    { id: 'new-task', label: 'New task', shortcut: '⌘N', onSelect: handlers.onNewTask },
    { id: 'toggle-theme', label: 'Toggle theme', shortcut: '⌘T', onSelect: handlers.onToggleTheme },
    { id: 'toggle-chat', label: 'Toggle chat', shortcut: '⌘\\', onSelect: handlers.onToggleChat },
    { id: 'toggle-files', label: 'Toggle files', shortcut: '⌘B', onSelect: handlers.onToggleFiles },
    { id: 'open-docs', label: 'Open docs', onSelect: handlers.onOpenDocs },
    { id: 'sign-out', label: 'Sign out', onSelect: handlers.onSignOut },
  ];
}

export function CommandPalette({
  isOpen,
  onClose,
  commands = [],
}: CommandPaletteProps): React.ReactElement {
  const [query, setQuery] = useState('');
  const [activeIndex, setActiveIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return commands;
    return commands.filter((c) => c.label.toLowerCase().includes(q));
  }, [commands, query]);

  // Reset state on open, focus input.
  useEffect(() => {
    if (isOpen) {
      setQuery('');
      setActiveIndex(0);
      // Allow framer-motion mount before focusing.
      const id = window.setTimeout(() => {
        inputRef.current?.focus();
      }, 50);
      return () => window.clearTimeout(id);
    }
    return undefined;
  }, [isOpen]);

  // Clamp active index when filter changes.
  useEffect(() => {
    if (activeIndex >= filtered.length) {
      setActiveIndex(filtered.length > 0 ? filtered.length - 1 : 0);
    }
  }, [filtered.length, activeIndex]);

  const handleSelect = useCallback(
    (cmd: CommandItem) => {
      cmd.onSelect();
      onClose();
    },
    [onClose],
  );

  const handleKeyDown = useCallback(
    (event: React.KeyboardEvent<HTMLDivElement>): void => {
      if (event.key === 'Escape') {
        event.preventDefault();
        onClose();
        return;
      }
      if (event.key === 'ArrowDown') {
        event.preventDefault();
        setActiveIndex((i) => (filtered.length === 0 ? 0 : (i + 1) % filtered.length));
        return;
      }
      if (event.key === 'ArrowUp') {
        event.preventDefault();
        setActiveIndex((i) =>
          filtered.length === 0 ? 0 : (i - 1 + filtered.length) % filtered.length,
        );
        return;
      }
      if (event.key === 'Enter') {
        event.preventDefault();
        const cmd = filtered[activeIndex];
        if (cmd) handleSelect(cmd);
      }
    },
    [filtered, activeIndex, handleSelect, onClose],
  );

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          key="command-palette-backdrop"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
          onClick={onClose}
          role="presentation"
          style={{
            position: 'fixed',
            inset: 0,
            zIndex: 60,
            background: 'rgb(0 0 0 / 0.5)',
            display: 'flex',
            alignItems: 'flex-start',
            justifyContent: 'center',
            paddingTop: '15vh',
          }}
        >
          <motion.div
            key="command-palette"
            initial={{ opacity: 0, scale: 0.96, y: -8 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.98, y: -4 }}
            transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
            onClick={(e) => e.stopPropagation()}
            onKeyDown={handleKeyDown}
            role="dialog"
            aria-modal="true"
            aria-label="Command palette"
            style={{
              width: '100%',
              maxWidth: '480px',
              margin: '0 var(--spacing-4)',
              background: 'var(--color-background-elevated)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-lg)',
              boxShadow: 'var(--shadow-xl)',
              overflow: 'hidden',
              display: 'flex',
              flexDirection: 'column',
            }}
          >
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                setActiveIndex(0);
              }}
              placeholder="Type a command or search…"
              aria-label="Search commands"
              style={{
                width: '100%',
                padding: 'var(--spacing-4)',
                background: 'transparent',
                color: 'var(--color-foreground)',
                border: 'none',
                borderBottom: '1px solid var(--color-border)',
                outline: 'none',
                fontFamily: 'var(--font-sans)',
                fontSize: 'var(--text-base)',
              }}
            />
            <ul
              role="listbox"
              aria-label="Commands"
              style={{
                listStyle: 'none',
                margin: 0,
                padding: 'var(--spacing-1)',
                maxHeight: '320px',
                overflowY: 'auto',
              }}
            >
              {filtered.length === 0 ? (
                <li
                  style={{
                    padding: 'var(--spacing-3) var(--spacing-4)',
                    color: 'var(--color-foreground-muted)',
                    fontSize: 'var(--text-sm)',
                  }}
                >
                  No commands found.
                </li>
              ) : (
                filtered.map((cmd, i) => {
                  const isActive = i === activeIndex;
                  return (
                    <li
                      key={cmd.id}
                      role="option"
                      aria-selected={isActive}
                      onClick={() => handleSelect(cmd)}
                      onMouseEnter={() => setActiveIndex(i)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        gap: 'var(--spacing-3)',
                        padding: 'var(--spacing-2) var(--spacing-3)',
                        borderRadius: 'var(--radius-md)',
                        cursor: 'pointer',
                        background: isActive ? 'var(--color-muted)' : 'transparent',
                        color: 'var(--color-foreground)',
                        fontSize: 'var(--text-sm)',
                      }}
                    >
                      <span>{cmd.label}</span>
                      {cmd.shortcut && (
                        <kbd
                          style={{
                            fontFamily: 'var(--font-mono)',
                            fontSize: 'var(--text-xs)',
                            color: 'var(--color-foreground-muted)',
                            background: 'var(--color-background-subtle)',
                            border: '1px solid var(--color-border)',
                            borderRadius: 'var(--radius-sm)',
                            padding: '2px 6px',
                          }}
                        >
                          {cmd.shortcut}
                        </kbd>
                      )}
                    </li>
                  );
                })
              )}
            </ul>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

export default CommandPalette;
