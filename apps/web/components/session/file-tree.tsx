'use client';

import * as React from 'react';
import {
  ChevronRight,
  Folder,
  FolderOpen,
  FileText,
  Image as ImageIcon,
  FileJson,
  FileCode,
  FileSpreadsheet,
  FileType2,
  File as FileIcon,
  Download,
  ClipboardCopy,
  Eye,
  Loader2,
  AlertCircle,
} from 'lucide-react';

export interface SandboxFileEntry {
  /** Absolute path inside the sandbox. */
  path: string;
  /** Last path segment. */
  name: string;
  /** "file" or "dir". */
  kind: 'file' | 'dir';
  /** Size in bytes (files only). */
  size?: number;
  /** MIME type if known. */
  mime?: string;
  /** Pre-fetched thumbnail data URL for images. */
  thumbnail?: string;
}

export interface FileTreeProps {
  sessionId: string;
  /** Called when the user activates a file (click / Enter / "Open in viewer"). */
  onFileOpen?: (file: SandboxFileEntry) => void;
  /** Override fetcher — defaults to `/api/sandbox/{sessionId}/files`. */
  fetchEntries?: (sessionId: string, path: string) => Promise<SandboxFileEntry[]>;
  /** Replay snapshot entries; when provided no sandbox fetches are made. */
  entries?: SandboxFileEntry[];
}

interface NodeState {
  expanded: boolean;
  loading: boolean;
  error: string | null;
  children: SandboxFileEntry[] | null;
}

interface ContextMenuState {
  x: number;
  y: number;
  file: SandboxFileEntry;
}

const ROOT_PATH = '/';

const defaultFetcher = async (
  sessionId: string,
  path: string,
): Promise<SandboxFileEntry[]> => {
  const search = new URLSearchParams({ path });
  const res = await fetch(
    `/api/sandbox/${encodeURIComponent(sessionId)}/files?${search.toString()}`,
    { headers: { accept: 'application/json' } },
  );
  if (!res.ok) {
    throw new Error(`Failed to list ${path} (${res.status})`);
  }
  const body = (await res.json()) as { entries?: SandboxFileEntry[] };
  return body.entries ?? [];
};

function iconForFile(entry: SandboxFileEntry): React.ReactElement {
  const size = 14;
  const stroke = 1.5;
  const name = entry.name.toLowerCase();
  const ext = name.includes('.') ? name.slice(name.lastIndexOf('.') + 1) : '';
  const mime = entry.mime ?? '';

  if (mime.startsWith('image/') || /^(png|jpe?g|gif|webp|svg|avif|bmp|ico)$/.test(ext)) {
    return <ImageIcon size={size} strokeWidth={stroke} />;
  }
  if (mime.includes('json') || ext === 'json') {
    return <FileJson size={size} strokeWidth={stroke} />;
  }
  if (
    /^(ts|tsx|js|jsx|mjs|cjs|py|rs|go|java|c|cpp|h|hpp|rb|php|swift|kt|sh|bash|zsh|sql|css|scss|html?)$/.test(
      ext,
    )
  ) {
    return <FileCode size={size} strokeWidth={stroke} />;
  }
  if (/^(csv|tsv|xlsx?)$/.test(ext)) {
    return <FileSpreadsheet size={size} strokeWidth={stroke} />;
  }
  if (ext === 'pdf') {
    return <FileType2 size={size} strokeWidth={stroke} />;
  }
  if (/^(md|mdx|txt|log|rst|toml|yaml|yml|ini|conf|env)$/.test(ext)) {
    return <FileText size={size} strokeWidth={stroke} />;
  }
  return <FileIcon size={size} strokeWidth={stroke} />;
}

interface TreeRowProps {
  entry: SandboxFileEntry;
  depth: number;
  state: NodeState | undefined;
  onToggle: (entry: SandboxFileEntry) => void;
  onSelect: (entry: SandboxFileEntry) => void;
  onContext: (entry: SandboxFileEntry, x: number, y: number) => void;
  isSelected: boolean;
}

function TreeRow({
  entry,
  depth,
  state,
  onToggle,
  onSelect,
  onContext,
  isSelected,
}: TreeRowProps): React.ReactElement {
  const isDir = entry.kind === 'dir';
  const expanded = state?.expanded ?? false;
  const loading = state?.loading ?? false;
  const error = state?.error ?? null;

  const handleClick = () => {
    if (isDir) onToggle(entry);
    else onSelect(entry);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleClick();
    }
  };

  return (
    <>
      <div
        role="treeitem"
        aria-level={depth + 1}
        aria-expanded={isDir ? expanded : undefined}
        aria-selected={isSelected}
        tabIndex={0}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        onContextMenu={(e) => {
          e.preventDefault();
          onContext(entry, e.clientX, e.clientY);
        }}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--spacing-1)',
          padding: 'var(--spacing-1) var(--spacing-2)',
          paddingLeft: `calc(var(--spacing-2) + ${depth * 12}px)`,
          fontSize: 'var(--text-sm)',
          color: isSelected
            ? 'var(--color-foreground)'
            : 'var(--color-foreground)',
          backgroundColor: isSelected
            ? 'var(--color-background-subtle)'
            : 'transparent',
          borderRadius: 'var(--radius-sm)',
          cursor: 'pointer',
          userSelect: 'none',
          transition: 'background-color var(--duration-fast) var(--ease-default)',
          outline: 'none',
        }}
        onMouseEnter={(e) => {
          if (!isSelected) {
            e.currentTarget.style.backgroundColor = 'var(--color-background-subtle)';
          }
        }}
        onMouseLeave={(e) => {
          if (!isSelected) {
            e.currentTarget.style.backgroundColor = 'transparent';
          }
        }}
      >
        <span
          aria-hidden
          style={{
            display: 'inline-flex',
            width: 12,
            height: 12,
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--color-foreground-muted)',
            transform: isDir && expanded ? 'rotate(90deg)' : 'rotate(0deg)',
            transition: 'transform var(--duration-fast) var(--ease-default)',
          }}
        >
          {isDir ? <ChevronRight size={12} strokeWidth={1.5} /> : null}
        </span>
        <span
          aria-hidden
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            color: 'var(--color-foreground-muted)',
            width: 16,
            height: 16,
            justifyContent: 'center',
          }}
        >
          {isDir ? (
            expanded ? (
              <FolderOpen size={14} strokeWidth={1.5} />
            ) : (
              <Folder size={14} strokeWidth={1.5} />
            )
          ) : entry.thumbnail ? (
            // Image thumbnail.
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={entry.thumbnail}
              alt=""
              width={14}
              height={14}
              style={{
                width: 14,
                height: 14,
                objectFit: 'cover',
                borderRadius: 'var(--radius-sm)',
              }}
            />
          ) : (
            iconForFile(entry)
          )}
        </span>
        <span
          style={{
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
            flex: 1,
          }}
        >
          {entry.name}
        </span>
        {loading ? (
          <Loader2
            size={12}
            strokeWidth={1.5}
            style={{
              color: 'var(--color-foreground-muted)',
              animation: 'spin 0.8s linear infinite',
            }}
          />
        ) : null}
      </div>
      {isDir && expanded ? (
        error ? (
          <div
            role="alert"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 'var(--spacing-1)',
              padding: 'var(--spacing-1) var(--spacing-2)',
              paddingLeft: `calc(var(--spacing-2) + ${(depth + 1) * 12}px)`,
              fontSize: 'var(--text-xs)',
              color: 'var(--color-destructive)',
            }}
          >
            <AlertCircle size={12} strokeWidth={1.5} />
            <span>{error}</span>
          </div>
        ) : state?.children ? (
          state.children.length === 0 ? (
            <div
              style={{
                paddingLeft: `calc(var(--spacing-2) + ${(depth + 1) * 12}px)`,
                padding: 'var(--spacing-1) var(--spacing-2)',
                fontSize: 'var(--text-xs)',
                color: 'var(--color-foreground-faint)',
                fontStyle: 'italic',
              }}
            >
              empty
            </div>
          ) : null
        ) : null
      ) : null}
    </>
  );
}

export function FileTree({
  sessionId,
  onFileOpen,
  fetchEntries,
  entries,
}: FileTreeProps): React.ReactElement {
  const fetcher = fetchEntries ?? defaultFetcher;
  const [nodes, setNodes] = React.useState<Record<string, NodeState>>({});
  const [rootEntries, setRootEntries] = React.useState<SandboxFileEntry[] | null>(null);
  const [rootError, setRootError] = React.useState<string | null>(null);
  const [rootLoading, setRootLoading] = React.useState(true);
  const [selectedPath, setSelectedPath] = React.useState<string | null>(null);
  const [contextMenu, setContextMenu] = React.useState<ContextMenuState | null>(null);

  const loadDir = React.useCallback(
    async (path: string) => {
      setNodes((prev) => ({
        ...prev,
        [path]: {
          expanded: prev[path]?.expanded ?? true,
          loading: true,
          error: null,
          children: prev[path]?.children ?? null,
        },
      }));
      try {
        const entries = await fetcher(sessionId, path);
        setNodes((prev) => ({
          ...prev,
          [path]: {
            expanded: true,
            loading: false,
            error: null,
            children: entries,
          },
        }));
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to load';
        setNodes((prev) => ({
          ...prev,
          [path]: {
            expanded: true,
            loading: false,
            error: message,
            children: prev[path]?.children ?? null,
          },
        }));
      }
    },
    [fetcher, sessionId],
  );

  // Load root on mount.
  React.useEffect(() => {
    if (entries) {
      setRootEntries(entries);
      setRootLoading(false);
      setRootError(null);
      return;
    }
    let cancelled = false;
    setRootLoading(true);
    setRootError(null);
    fetcher(sessionId, ROOT_PATH)
      .then((entries) => {
        if (!cancelled) {
          setRootEntries(entries);
          setRootLoading(false);
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setRootError(err instanceof Error ? err.message : 'Failed to load');
          setRootLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [entries, fetcher, sessionId]);

  const handleToggle = React.useCallback(
    (entry: SandboxFileEntry) => {
      const existing = nodes[entry.path];
      if (existing?.expanded) {
        setNodes((prev) => ({
          ...prev,
          [entry.path]: {
            ...existing,
            expanded: false,
          },
        }));
        return;
      }
      if (existing?.children) {
        setNodes((prev) => ({
          ...prev,
          [entry.path]: {
            ...existing,
            expanded: true,
          },
        }));
        return;
      }
      void loadDir(entry.path);
    },
    [loadDir, nodes],
  );

  const handleSelect = React.useCallback(
    (entry: SandboxFileEntry) => {
      setSelectedPath(entry.path);
      onFileOpen?.(entry);
    },
    [onFileOpen],
  );

  const handleContext = React.useCallback(
    (entry: SandboxFileEntry, x: number, y: number) => {
      setContextMenu({ file: entry, x, y });
    },
    [],
  );

  // Dismiss context menu on outside click / Esc.
  React.useEffect(() => {
    if (!contextMenu) return;
    const close = () => setContextMenu(null);
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') close();
    };
    window.addEventListener('click', close);
    window.addEventListener('keydown', onKey);
    return () => {
      window.removeEventListener('click', close);
      window.removeEventListener('keydown', onKey);
    };
  }, [contextMenu]);

  const renderEntries = (entries: SandboxFileEntry[], depth: number): React.ReactNode =>
    entries.map((entry) => {
      const state = nodes[entry.path];
      return (
        <React.Fragment key={entry.path}>
          <TreeRow
            entry={entry}
            depth={depth}
            state={state}
            onToggle={handleToggle}
            onSelect={handleSelect}
            onContext={handleContext}
            isSelected={entry.path === selectedPath}
          />
          {entry.kind === 'dir' && state?.expanded && state.children
            ? renderEntries(state.children, depth + 1)
            : null}
        </React.Fragment>
      );
    });

  const handleCopyPath = async () => {
    if (!contextMenu) return;
    try {
      await navigator.clipboard.writeText(contextMenu.file.path);
    } catch {
      /* clipboard unavailable — silent */
    }
    setContextMenu(null);
  };

  const handleDownload = () => {
    if (!contextMenu) return;
    const url = `/api/sandbox/${encodeURIComponent(sessionId)}/files/raw?path=${encodeURIComponent(contextMenu.file.path)}`;
    const a = document.createElement('a');
    a.href = url;
    a.download = contextMenu.file.name;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setContextMenu(null);
  };

  const handleOpenInViewer = () => {
    if (!contextMenu) return;
    handleSelect(contextMenu.file);
    setContextMenu(null);
  };

  return (
    <div
      role="tree"
      aria-label="Sandbox file tree"
      style={{
        width: 320,
        minWidth: 320,
        height: '100%',
        backgroundColor: 'var(--color-background-elevated)',
        borderRight: '1px solid var(--color-border)',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        fontFamily: 'var(--font-sans)',
      }}
    >
      <div
        style={{
          padding: 'var(--spacing-3) var(--spacing-3)',
          borderBottom: '1px solid var(--color-border)',
          fontSize: 'var(--text-xs)',
          color: 'var(--color-foreground-muted)',
          letterSpacing: '0.05em',
          textTransform: 'uppercase',
          fontWeight: 'var(--font-weight-medium)',
          flexShrink: 0,
        }}
      >
        Sandbox files
      </div>
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          overflowX: 'hidden',
          padding: 'var(--spacing-2) var(--spacing-1)',
        }}
      >
        {rootLoading ? (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 'var(--spacing-2)',
              padding: 'var(--spacing-3)',
              fontSize: 'var(--text-sm)',
              color: 'var(--color-foreground-muted)',
            }}
          >
            <Loader2
              size={14}
              strokeWidth={1.5}
              style={{ animation: 'spin 0.8s linear infinite' }}
            />
            Loading files…
          </div>
        ) : rootError ? (
          <div
            role="alert"
            style={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: 'var(--spacing-2)',
              padding: 'var(--spacing-3)',
              fontSize: 'var(--text-xs)',
              color: 'var(--color-destructive)',
            }}
          >
            <AlertCircle size={14} strokeWidth={1.5} />
            <span>{rootError}</span>
          </div>
        ) : rootEntries && rootEntries.length > 0 ? (
          renderEntries(rootEntries, 0)
        ) : (
          <div
            style={{
              padding: 'var(--spacing-3)',
              fontSize: 'var(--text-xs)',
              color: 'var(--color-foreground-faint)',
              fontStyle: 'italic',
            }}
          >
            No files in sandbox
          </div>
        )}
      </div>

      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
        @media (prefers-reduced-motion: reduce) {
          @keyframes spin { to { transform: rotate(0deg); } }
        }
      `}</style>

      {contextMenu ? (
        <div
          role="menu"
          aria-label="File actions"
          style={{
            position: 'fixed',
            top: contextMenu.y,
            left: contextMenu.x,
            zIndex: 1000,
            minWidth: 180,
            backgroundColor: 'var(--color-background-elevated)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-md)',
            boxShadow: 'var(--shadow-md)',
            padding: 'var(--spacing-1)',
            fontSize: 'var(--text-sm)',
            color: 'var(--color-foreground)',
          }}
          onClick={(e) => e.stopPropagation()}
          onContextMenu={(e) => e.preventDefault()}
        >
          <ContextItem
            icon={<Eye size={14} strokeWidth={1.5} />}
            label="Open in viewer"
            onClick={handleOpenInViewer}
            disabled={contextMenu.file.kind === 'dir'}
          />
          <ContextItem
            icon={<Download size={14} strokeWidth={1.5} />}
            label="Download"
            onClick={handleDownload}
            disabled={contextMenu.file.kind === 'dir'}
          />
          <ContextItem
            icon={<ClipboardCopy size={14} strokeWidth={1.5} />}
            label="Copy path"
            onClick={handleCopyPath}
          />
        </div>
      ) : null}
    </div>
  );
}

interface ContextItemProps {
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
  disabled?: boolean;
}

function ContextItem({
  icon,
  label,
  onClick,
  disabled,
}: ContextItemProps): React.ReactElement {
  return (
    <button
      type="button"
      role="menuitem"
      disabled={disabled}
      onClick={onClick}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 'var(--spacing-2)',
        width: '100%',
        padding: 'var(--spacing-1) var(--spacing-2)',
        background: 'transparent',
        border: 'none',
        borderRadius: 'var(--radius-sm)',
        color: disabled
          ? 'var(--color-foreground-faint)'
          : 'var(--color-foreground)',
        fontSize: 'var(--text-sm)',
        textAlign: 'left',
        cursor: disabled ? 'not-allowed' : 'pointer',
        transition: 'background-color var(--duration-fast) var(--ease-default)',
      }}
      onMouseEnter={(e) => {
        if (!disabled) {
          e.currentTarget.style.backgroundColor = 'var(--color-background-subtle)';
        }
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.backgroundColor = 'transparent';
      }}
    >
      <span style={{ color: 'var(--color-foreground-muted)' }}>{icon}</span>
      <span>{label}</span>
    </button>
  );
}

export default FileTree;
