'use client';

import { useEffect, useRef } from 'react';

/**
 * Keyboard shortcut registration hook.
 *
 * Shortcut keys use the form "mod+<key>" where <key> is the lowercase key
 * (e.g. "mod+k", "mod+\\", "mod+/", "mod+b"). "mod" maps to Cmd on macOS
 * and Ctrl elsewhere. Callbacks are debounced (200ms) to prevent double-fire.
 *
 * @example
 *   useKeyboardShortcuts({
 *     'mod+k': () => openPalette(),
 *     'mod+\\': () => toggleChat(),
 *   });
 */
export function useKeyboardShortcuts(
  shortcuts: Record<string, () => void>,
): void {
  const shortcutsRef = useRef(shortcuts);
  const lastFireRef = useRef<Record<string, number>>({});

  // Keep latest callbacks without rebinding the listener.
  useEffect(() => {
    shortcutsRef.current = shortcuts;
  }, [shortcuts]);

  useEffect(() => {
    const DEBOUNCE_MS = 200;

    const handleKeyDown = (event: KeyboardEvent): void => {
      const mod = event.metaKey || event.ctrlKey;
      if (!mod) return;

      const key = event.key.toLowerCase();
      const id = `mod+${key}`;

      const handler = shortcutsRef.current[id];
      if (!handler) return;

      const now = Date.now();
      const last = lastFireRef.current[id] ?? 0;
      if (now - last < DEBOUNCE_MS) {
        event.preventDefault();
        return;
      }
      lastFireRef.current[id] = now;

      event.preventDefault();
      handler();
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, []);
}

export default useKeyboardShortcuts;
