'use client';

import { Folder, MessageSquare, Monitor } from 'lucide-react';

export type MobileTab = 'chat' | 'computer' | 'files';

export interface MobileTabsProps {
  active: MobileTab;
  onChange: (tab: MobileTab) => void;
}

interface TabDef {
  id: MobileTab;
  label: string;
  Icon: typeof MessageSquare;
}

const TABS: readonly TabDef[] = [
  { id: 'chat', label: 'Chat', Icon: MessageSquare },
  { id: 'computer', label: 'Computer', Icon: Monitor },
  { id: 'files', label: 'Files', Icon: Folder },
];

export function MobileTabs({ active, onChange }: MobileTabsProps): React.ReactElement {
  return (
    <nav
      aria-label="Mobile navigation"
      className="mantle-mobile-tabs"
      style={{
        position: 'fixed',
        left: 0,
        right: 0,
        bottom: 0,
        height: '48px',
        display: 'flex',
        alignItems: 'stretch',
        justifyContent: 'space-around',
        background: 'var(--color-background-elevated)',
        borderTop: '1px solid var(--color-border)',
        zIndex: 40,
      }}
    >
      {TABS.map(({ id, label, Icon }) => {
        const isActive = id === active;
        return (
          <button
            key={id}
            type="button"
            onClick={() => onChange(id)}
            aria-label={label}
            aria-current={isActive ? 'page' : undefined}
            style={{
              position: 'relative',
              flex: 1,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 'var(--spacing-1)',
              background: 'transparent',
              border: 'none',
              padding: 0,
              cursor: 'pointer',
              color: isActive ? 'var(--color-accent)' : 'var(--color-foreground-muted)',
              fontFamily: 'var(--font-sans)',
              fontSize: 'var(--text-xs)',
            }}
          >
            {isActive && (
              <span
                aria-hidden="true"
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 'var(--spacing-4)',
                  right: 'var(--spacing-4)',
                  background: 'var(--color-accent)',
                  borderRadius: 'var(--radius-full)',
                }}
              />
            )}
            <Icon size={20} aria-hidden="true" />
            <span>{label}</span>
          </button>
        );
      })}
    </nav>
  );
}

export default MobileTabs;
