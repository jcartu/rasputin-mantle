'use client';

import * as React from 'react';
import {
  X,
  Download,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  AlertCircle,
  Loader2,
} from 'lucide-react';
import { Button } from '@/components/ui/button';

export interface ArtifactViewerProps {
  sessionId: string;
  filePath: string | null;
  closeAction: () => void;
}

interface FileMeta {
  path: string;
  name: string;
  size: number;
  mime: string;
  lastModified?: string;
}

type ViewerState =
  | { kind: 'idle' }
  | { kind: 'loading' }
  | { kind: 'error'; message: string }
  | { kind: 'ready'; meta: FileMeta; body: ArtifactBody };

type ArtifactBody =
  | { type: 'text'; content: string }
  | { type: 'markdown'; content: string }
  | { type: 'json'; content: string; parsed: unknown }
  | { type: 'csv'; rows: string[][] }
  | { type: 'image'; url: string }
  | { type: 'pdf'; url: string }
  | { type: 'pptx'; title: string; text: string[] }
  | { type: 'xlsx'; sheetName: string; rows: string[][] }
  | { type: 'docx'; text: string }
  | { type: 'binary' };

const MAX_TEXT_BYTES = 1_000_000; // 1 MiB safety cap

function basename(p: string): string {
  const idx = p.lastIndexOf('/');
  return idx === -1 ? p : p.slice(idx + 1);
}

function rawUrl(sessionId: string, path: string): string {
  return `/api/sandbox/${encodeURIComponent(sessionId)}/files/raw?path=${encodeURIComponent(path)}`;
}

function metaUrl(sessionId: string, path: string): string {
  return `/api/sandbox/${encodeURIComponent(sessionId)}/files/meta?path=${encodeURIComponent(path)}`;
}

function inferKind(mime: string, name: string): ArtifactBody['type'] | 'unknown' {
  const ext = name.includes('.') ? name.slice(name.lastIndexOf('.') + 1).toLowerCase() : '';
  if (mime.startsWith('image/') || /^(png|jpe?g|gif|webp|svg|avif|bmp|ico)$/.test(ext)) {
    return 'image';
  }
  if (mime === 'application/pdf' || ext === 'pdf') {
    return 'pdf';
  }
  if (ext === 'pptx' || mime === 'application/vnd.openxmlformats-officedocument.presentationml.presentation') {
    return 'pptx';
  }
  if (ext === 'xlsx' || mime === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') {
    return 'xlsx';
  }
  if (ext === 'docx' || mime === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
    return 'docx';
  }
  if (mime.includes('json') || ext === 'json') {
    return 'json';
  }
  if (mime === 'text/csv' || ext === 'csv' || ext === 'tsv') {
    return 'csv';
  }
  if (mime === 'text/markdown' || ext === 'md' || ext === 'mdx') {
    return 'markdown';
  }
  if (mime.startsWith('text/') || mime.includes('javascript') || mime.includes('xml')) {
    return 'text';
  }
  if (
    /^(ts|tsx|js|jsx|mjs|cjs|py|rs|go|java|c|cpp|h|hpp|rb|php|swift|kt|sh|bash|zsh|sql|css|scss|html?|toml|yaml|yml|ini|conf|env|txt|log|rst)$/.test(
      ext,
    )
  ) {
    return 'text';
  }
  return 'unknown';
}

/* ─── Markdown sanitiser ─────────────────────────────────────────────── */

/**
 * Minimal markdown→HTML renderer with strict sanitisation. We intentionally
 * avoid pulling in a markdown library to keep the bundle small. The output is
 * HTML-encoded first, then a curated set of inline tokens is re-introduced.
 *
 * Supports: headings (#–######), bold (**…**), italic (*…* / _…_), inline
 * code, fenced code blocks, links [text](url) with http(s) only, ordered &
 * unordered lists, blockquotes, paragraphs, line breaks.
 */
function escapeHtml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function renderInline(raw: string): string {
  let s = escapeHtml(raw);
  // Inline code first to protect its contents.
  s = s.replace(/`([^`]+)`/g, (_m, code: string) => `<code>${code}</code>`);
  // Bold.
  s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  // Italic.
  s = s.replace(/(^|[^*])\*([^*\n]+)\*/g, '$1<em>$2</em>');
  s = s.replace(/(^|[^_])_([^_\n]+)_/g, '$1<em>$2</em>');
  // Links [text](url) — only http/https.
  s = s.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (_m, text: string, url: string) => {
    if (!/^https?:\/\//i.test(url)) return text;
    return `<a href="${url}" target="_blank" rel="noreferrer noopener">${text}</a>`;
  });
  return s;
}

function renderMarkdown(src: string): string {
  const lines = src.split('\n');
  const out: string[] = [];
  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    // Fenced code.
    if (/^```/.test(line)) {
      const lang = line.replace(/^```/, '').trim();
      const buf: string[] = [];
      i += 1;
      while (i < lines.length && !/^```/.test(lines[i])) {
        buf.push(lines[i]);
        i += 1;
      }
      const langAttr = lang ? ` data-lang="${escapeHtml(lang)}"` : '';
      out.push(`<pre${langAttr}><code>${escapeHtml(buf.join('\n'))}</code></pre>`);
      i += 1;
      continue;
    }
    // Heading.
    const h = /^(#{1,6})\s+(.+)$/.exec(line);
    if (h) {
      const level = h[1].length;
      out.push(`<h${level}>${renderInline(h[2])}</h${level}>`);
      i += 1;
      continue;
    }
    // Unordered list.
    if (/^\s*[-*]\s+/.test(line)) {
      const items: string[] = [];
      while (i < lines.length && /^\s*[-*]\s+/.test(lines[i])) {
        items.push(`<li>${renderInline(lines[i].replace(/^\s*[-*]\s+/, ''))}</li>`);
        i += 1;
      }
      out.push(`<ul>${items.join('')}</ul>`);
      continue;
    }
    // Ordered list.
    if (/^\s*\d+\.\s+/.test(line)) {
      const items: string[] = [];
      while (i < lines.length && /^\s*\d+\.\s+/.test(lines[i])) {
        items.push(`<li>${renderInline(lines[i].replace(/^\s*\d+\.\s+/, ''))}</li>`);
        i += 1;
      }
      out.push(`<ol>${items.join('')}</ol>`);
      continue;
    }
    // Blockquote.
    if (/^>\s?/.test(line)) {
      const buf: string[] = [];
      while (i < lines.length && /^>\s?/.test(lines[i])) {
        buf.push(lines[i].replace(/^>\s?/, ''));
        i += 1;
      }
      out.push(`<blockquote>${renderInline(buf.join('\n'))}</blockquote>`);
      continue;
    }
    // Blank line.
    if (/^\s*$/.test(line)) {
      i += 1;
      continue;
    }
    // Paragraph (greedy).
    const buf: string[] = [];
    while (i < lines.length && !/^\s*$/.test(lines[i]) && !/^(#|```|>|\s*[-*]\s|\s*\d+\.\s)/.test(lines[i])) {
      buf.push(lines[i]);
      i += 1;
    }
    out.push(`<p>${renderInline(buf.join(' '))}</p>`);
  }
  return out.join('\n');
}

/* ─── CSV parser ─────────────────────────────────────────────────────── */

function parseCsv(src: string, delimiter = ','): string[][] {
  const rows: string[][] = [];
  let row: string[] = [];
  let cell = '';
  let inQuote = false;
  for (let i = 0; i < src.length; i += 1) {
    const ch = src[i];
    if (inQuote) {
      if (ch === '"' && src[i + 1] === '"') {
        cell += '"';
        i += 1;
      } else if (ch === '"') {
        inQuote = false;
      } else {
        cell += ch;
      }
    } else if (ch === '"') {
      inQuote = true;
    } else if (ch === delimiter) {
      row.push(cell);
      cell = '';
    } else if (ch === '\n' || ch === '\r') {
      if (ch === '\r' && src[i + 1] === '\n') i += 1;
      row.push(cell);
      cell = '';
      rows.push(row);
      row = [];
    } else {
      cell += ch;
    }
  }
  if (cell.length > 0 || row.length > 0) {
    row.push(cell);
    rows.push(row);
  }
  return rows;
}

/* ─── Lazy Office preview parsers ────────────────────────────────────── */

function decodeXmlText(xml: string): string {
  return xml
    .replace(/<[^>]+>/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/\s+/g, ' ')
    .trim();
}

async function parsePptxPreview(buffer: ArrayBuffer): Promise<{ title: string; text: string[] }> {
  const { default: JSZip } = await import('jszip');
  const zip = await JSZip.loadAsync(buffer);
  const slideXml = await zip.file('ppt/slides/slide1.xml')?.async('string');
  if (!slideXml) return { title: 'First slide', text: ['No slide XML found.'] };
  const matches = Array.from(slideXml.matchAll(/<a:t>(.*?)<\/a:t>/g), (match) => decodeXmlText(match[1]));
  const text = matches.filter(Boolean).slice(0, 12);
  return { title: text[0] || 'First slide', text: text.slice(1) };
}

async function parseDocxPreview(buffer: ArrayBuffer): Promise<string> {
  const { default: JSZip } = await import('jszip');
  const zip = await JSZip.loadAsync(buffer);
  const documentXml = await zip.file('word/document.xml')?.async('string');
  if (!documentXml) return 'No document text found.';
  return decodeXmlText(documentXml).slice(0, 2400);
}

async function parseXlsxPreview(buffer: ArrayBuffer): Promise<{ sheetName: string; rows: string[][] }> {
  const XLSX = await import('xlsx');
  const workbook = XLSX.read(buffer, { type: 'array' });
  const sheetName = workbook.SheetNames[0] || 'Sheet1';
  const sheet = workbook.Sheets[sheetName];
  if (!sheet) return { sheetName, rows: [] };
  const rows = XLSX.utils.sheet_to_json<string[]>(sheet, { header: 1, blankrows: false }).slice(0, 20);
  return { sheetName, rows: rows.map((row) => row.slice(0, 10).map((cell) => String(cell ?? ''))) };
}

/* ─── Image zoom/pan ─────────────────────────────────────────────────── */

interface ImageViewerProps {
  url: string;
  alt: string;
}

function ImageViewer({ url, alt }: ImageViewerProps): React.ReactElement {
  const [zoom, setZoom] = React.useState(1);
  const [pan, setPan] = React.useState({ x: 0, y: 0 });
  const dragRef = React.useRef<{ x: number; y: number; panX: number; panY: number } | null>(null);

  const reset = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  const onPointerDown = (e: React.PointerEvent<HTMLDivElement>) => {
    if (zoom <= 1) return;
    e.currentTarget.setPointerCapture(e.pointerId);
    dragRef.current = { x: e.clientX, y: e.clientY, panX: pan.x, panY: pan.y };
  };
  const onPointerMove = (e: React.PointerEvent<HTMLDivElement>) => {
    if (!dragRef.current) return;
    setPan({
      x: dragRef.current.panX + (e.clientX - dragRef.current.x),
      y: dragRef.current.panY + (e.clientY - dragRef.current.y),
    });
  };
  const onPointerUp = (e: React.PointerEvent<HTMLDivElement>) => {
    dragRef.current = null;
    try {
      e.currentTarget.releasePointerCapture(e.pointerId);
    } catch {
      /* noop */
    }
  };

  return (
    <div
      style={{
        position: 'relative',
        flex: 1,
        minHeight: 0,
        backgroundColor: 'var(--color-background)',
        overflow: 'hidden',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <div
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        onPointerCancel={onPointerUp}
        style={{
          width: '100%',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: zoom > 1 ? (dragRef.current ? 'grabbing' : 'grab') : 'default',
          touchAction: 'none',
        }}
      >
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={url}
          alt={alt}
          draggable={false}
          style={{
            maxWidth: '100%',
            maxHeight: '100%',
            transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
            transformOrigin: 'center center',
            transition: dragRef.current
              ? 'none'
              : 'transform var(--duration-default) var(--ease-default)',
            userSelect: 'none',
            pointerEvents: 'none',
          }}
        />
      </div>
      <div
        style={{
          position: 'absolute',
          bottom: 'var(--spacing-3)',
          left: '50%',
          transform: 'translateX(-50%)',
          display: 'inline-flex',
          alignItems: 'center',
          gap: 'var(--spacing-1)',
          padding: 'var(--spacing-1)',
          backgroundColor: 'var(--color-background-elevated)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-md)',
          boxShadow: 'var(--shadow-sm)',
        }}
      >
        <Button
          variant="ghost"
          size="xs"
          iconOnly={<ZoomOut size={14} strokeWidth={1.5} />}
          aria-label="Zoom out"
          onClick={() => setZoom((z) => Math.max(0.25, +(z - 0.25).toFixed(2)))}
        />
        <span
          style={{
            minWidth: 48,
            textAlign: 'center',
            fontSize: 'var(--text-xs)',
            color: 'var(--color-foreground-muted)',
            fontFamily: 'var(--font-mono)',
          }}
        >
          {Math.round(zoom * 100)}%
        </span>
        <Button
          variant="ghost"
          size="xs"
          iconOnly={<ZoomIn size={14} strokeWidth={1.5} />}
          aria-label="Zoom in"
          onClick={() => setZoom((z) => Math.min(8, +(z + 0.25).toFixed(2)))}
        />
        <Button
          variant="ghost"
          size="xs"
          iconOnly={<RotateCcw size={14} strokeWidth={1.5} />}
          aria-label="Reset zoom and pan"
          onClick={reset}
        />
      </div>
    </div>
  );
}

/* ─── JSON tree (collapsible) ────────────────────────────────────────── */

interface JsonNodeProps {
  value: unknown;
  name?: string;
  depth: number;
}

function JsonNode({ value, name, depth }: JsonNodeProps): React.ReactElement {
  const [open, setOpen] = React.useState(depth < 2);
  const indent = depth * 12;

  if (value === null) {
    return (
      <div style={{ paddingLeft: indent, fontFamily: 'var(--font-mono)', fontSize: 'var(--text-xs)' }}>
        {name !== undefined ? (
          <span style={{ color: 'var(--color-accent)' }}>&quot;{name}&quot;: </span>
        ) : null}
        <span style={{ color: 'var(--color-foreground-faint)' }}>null</span>
      </div>
    );
  }
  if (typeof value !== 'object') {
    let color = 'var(--color-foreground)';
    let display: string;
    if (typeof value === 'string') {
      color = 'var(--color-success)';
      display = `"${value}"`;
    } else if (typeof value === 'number') {
      color = 'var(--color-warning)';
      display = String(value);
    } else if (typeof value === 'boolean') {
      color = 'var(--color-accent)';
      display = String(value);
    } else {
      display = String(value);
    }
    return (
      <div style={{ paddingLeft: indent, fontFamily: 'var(--font-mono)', fontSize: 'var(--text-xs)' }}>
        {name !== undefined ? (
          <span style={{ color: 'var(--color-accent)' }}>&quot;{name}&quot;: </span>
        ) : null}
        <span style={{ color, wordBreak: 'break-all' }}>{display}</span>
      </div>
    );
  }

  const isArray = Array.isArray(value);
  const entries: [string, unknown][] = isArray
    ? (value as unknown[]).map((v, idx) => [String(idx), v])
    : Object.entries(value as Record<string, unknown>);
  const openBrace = isArray ? '[' : '{';
  const closeBrace = isArray ? ']' : '}';

  return (
    <div style={{ paddingLeft: indent, fontFamily: 'var(--font-mono)', fontSize: 'var(--text-xs)' }}>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        style={{
          background: 'transparent',
          border: 'none',
          padding: 0,
          color: 'var(--color-foreground)',
          cursor: 'pointer',
          fontFamily: 'inherit',
          fontSize: 'inherit',
        }}
      >
        <span style={{ color: 'var(--color-foreground-muted)' }}>{open ? '▾' : '▸'} </span>
        {name !== undefined ? (
          <span style={{ color: 'var(--color-accent)' }}>&quot;{name}&quot;: </span>
        ) : null}
        <span>{openBrace}</span>
        {open ? null : (
          <span style={{ color: 'var(--color-foreground-muted)' }}>
            {' '}
            {entries.length} {isArray ? 'items' : 'keys'} {closeBrace}
          </span>
        )}
      </button>
      {open ? (
        <>
          {entries.map(([k, v]) => (
            <JsonNode key={k} name={isArray ? undefined : k} value={v} depth={depth + 1} />
          ))}
          <div style={{ paddingLeft: 0 }}>{closeBrace}</div>
        </>
      ) : null}
    </div>
  );
}

/* ─── Main viewer ────────────────────────────────────────────────────── */

export function ArtifactViewer({
  sessionId,
  filePath,
  closeAction,
}: ArtifactViewerProps): React.ReactElement | null {
  const [state, setState] = React.useState<ViewerState>({ kind: 'idle' });

  React.useEffect(() => {
    if (!filePath) {
      setState({ kind: 'idle' });
      return;
    }
    let cancelled = false;
    setState({ kind: 'loading' });

    const load = async () => {
      try {
        const metaRes = await fetch(metaUrl(sessionId, filePath), {
          headers: { accept: 'application/json' },
        });
        if (!metaRes.ok) throw new Error(`Metadata failed (${metaRes.status})`);
        const meta = (await metaRes.json()) as FileMeta;
        if (cancelled) return;

        const kind = inferKind(meta.mime, meta.name);
        const url = rawUrl(sessionId, filePath);

        if (kind === 'image') {
          setState({ kind: 'ready', meta, body: { type: 'image', url } });
          return;
        }
        if (kind === 'pdf') {
          setState({ kind: 'ready', meta, body: { type: 'pdf', url } });
          return;
        }
        if (kind === 'pptx' || kind === 'xlsx' || kind === 'docx') {
          const rawRes = await fetch(url);
          if (!rawRes.ok) throw new Error(`Content failed (${rawRes.status})`);
          const buffer = await rawRes.arrayBuffer();
          if (cancelled) return;
          if (kind === 'pptx') {
            const preview = await parsePptxPreview(buffer);
            if (!cancelled) setState({ kind: 'ready', meta, body: { type: 'pptx', ...preview } });
            return;
          }
          if (kind === 'xlsx') {
            const preview = await parseXlsxPreview(buffer);
            if (!cancelled) setState({ kind: 'ready', meta, body: { type: 'xlsx', ...preview } });
            return;
          }
          const text = await parseDocxPreview(buffer);
          if (!cancelled) setState({ kind: 'ready', meta, body: { type: 'docx', text } });
          return;
        }
        if (kind === 'unknown' || meta.size > MAX_TEXT_BYTES) {
          setState({ kind: 'ready', meta, body: { type: 'binary' } });
          return;
        }

        const rawRes = await fetch(url);
        if (!rawRes.ok) throw new Error(`Content failed (${rawRes.status})`);
        const text = await rawRes.text();
        if (cancelled) return;

        if (kind === 'json') {
          try {
            const parsed = JSON.parse(text) as unknown;
            setState({
              kind: 'ready',
              meta,
              body: { type: 'json', content: JSON.stringify(parsed, null, 2), parsed },
            });
          } catch {
            setState({ kind: 'ready', meta, body: { type: 'text', content: text } });
          }
          return;
        }
        if (kind === 'csv') {
          const delim = meta.name.toLowerCase().endsWith('.tsv') ? '\t' : ',';
          const rows = parseCsv(text, delim);
          setState({ kind: 'ready', meta, body: { type: 'csv', rows } });
          return;
        }
        if (kind === 'markdown') {
          setState({ kind: 'ready', meta, body: { type: 'markdown', content: text } });
          return;
        }
        setState({ kind: 'ready', meta, body: { type: 'text', content: text } });
      } catch (err) {
        if (cancelled) return;
        const message = err instanceof Error ? err.message : 'Failed to load file';
        setState({ kind: 'error', message });
      }
    };

    void load();
    return () => {
      cancelled = true;
    };
  }, [filePath, sessionId]);

  // Esc to close.
  React.useEffect(() => {
    if (!filePath) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') closeAction();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [filePath, closeAction]);

  if (!filePath) return null;

  const downloadUrl = rawUrl(sessionId, filePath);
  const displayName = basename(filePath);

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label={`Artifact viewer: ${displayName}`}
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 100,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 'var(--spacing-6)',
        backgroundColor: 'rgb(0 0 0 / 0.5)',
      }}
      onClick={(e) => {
        if (e.target === e.currentTarget) closeAction();
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: 960,
          height: '100%',
          maxHeight: '90vh',
          display: 'flex',
          flexDirection: 'column',
          backgroundColor: 'var(--color-background-elevated)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-lg)',
          boxShadow: 'var(--shadow-lg)',
          overflow: 'hidden',
          color: 'var(--color-foreground)',
        }}
      >
        <header
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--spacing-3)',
            padding: 'var(--spacing-3) var(--spacing-4)',
            borderBottom: '1px solid var(--color-border)',
            flexShrink: 0,
          }}
        >
          <div style={{ flex: 1, minWidth: 0 }}>
            <div
              style={{
                fontSize: 'var(--text-sm)',
                fontWeight: 'var(--font-weight-medium)',
                color: 'var(--color-foreground)',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}
            >
              {displayName}
            </div>
            <div
              style={{
                fontSize: 'var(--text-xs)',
                color: 'var(--color-foreground-muted)',
                fontFamily: 'var(--font-mono)',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}
            >
              {filePath}
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            iconLeft={<Download size={14} strokeWidth={1.5} />}
            onClick={() => {
              const a = document.createElement('a');
              a.href = downloadUrl;
              a.download = displayName;
              document.body.appendChild(a);
              a.click();
              a.remove();
            }}
          >
            Download
          </Button>
          <Button
            variant="ghost"
            size="sm"
            iconOnly={<X size={16} strokeWidth={1.5} />}
            aria-label="Close artifact viewer"
            onClick={closeAction}
          />
        </header>

        <div
          style={{
            flex: 1,
            minHeight: 0,
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
          }}
        >
          {state.kind === 'loading' ? (
            <div
              style={{
                display: 'flex',
                flex: 1,
                alignItems: 'center',
                justifyContent: 'center',
                gap: 'var(--spacing-2)',
                color: 'var(--color-foreground-muted)',
                fontSize: 'var(--text-sm)',
              }}
            >
              <Loader2
                size={16}
                strokeWidth={1.5}
                style={{ animation: 'spin 0.8s linear infinite' }}
              />
              Loading…
            </div>
          ) : state.kind === 'error' ? (
            <div
              role="alert"
              style={{
                display: 'flex',
                flex: 1,
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 'var(--spacing-2)',
                color: 'var(--color-destructive)',
                fontSize: 'var(--text-sm)',
                padding: 'var(--spacing-6)',
                textAlign: 'center',
              }}
            >
              <AlertCircle size={20} strokeWidth={1.5} />
              <div>{state.message}</div>
              <a
                href={downloadUrl}
                download={displayName}
                style={{ color: 'var(--color-accent)', fontSize: 'var(--text-xs)' }}
              >
                Download instead
              </a>
            </div>
          ) : state.kind === 'ready' ? (
            <ArtifactBody body={state.body} meta={state.meta} downloadUrl={downloadUrl} />
          ) : null}
        </div>

        <style>{`
          @keyframes spin { to { transform: rotate(360deg); } }
          @media (prefers-reduced-motion: reduce) {
            @keyframes spin { to { transform: rotate(0deg); } }
          }
          .mantle-md h1, .mantle-md h2, .mantle-md h3, .mantle-md h4, .mantle-md h5, .mantle-md h6 {
            color: var(--color-foreground);
            font-weight: var(--font-weight-semibold);
            margin-top: var(--spacing-4);
            margin-bottom: var(--spacing-2);
          }
          .mantle-md h1 { font-size: var(--text-2xl); }
          .mantle-md h2 { font-size: var(--text-xl); }
          .mantle-md h3 { font-size: var(--text-lg); }
          .mantle-md h4, .mantle-md h5, .mantle-md h6 { font-size: var(--text-base); }
          .mantle-md p { margin: 0 0 var(--spacing-3); line-height: 1.6; }
          .mantle-md a { color: var(--color-accent); text-decoration: none; }
          .mantle-md a:hover { text-decoration: underline; }
          .mantle-md ul, .mantle-md ol { margin: 0 0 var(--spacing-3); padding-left: var(--spacing-6); }
          .mantle-md li { margin-bottom: var(--spacing-1); }
          .mantle-md blockquote {
            margin: 0 0 var(--spacing-3);
            padding: var(--spacing-2) var(--spacing-3);
            border-left: 3px solid var(--color-accent);
            background-color: var(--color-background-subtle);
            color: var(--color-foreground-muted);
          }
          .mantle-md code {
            font-family: var(--font-mono);
            font-size: 0.92em;
            color: var(--color-accent);
            background-color: var(--color-background-subtle);
            padding: 1px 4px;
            border-radius: var(--radius-sm);
          }
          .mantle-md pre {
            background-color: var(--color-background);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-md);
            padding: var(--spacing-3);
            overflow-x: auto;
            margin: 0 0 var(--spacing-3);
          }
          .mantle-md pre code {
            color: var(--color-foreground);
            background: transparent;
            padding: 0;
            font-size: var(--text-sm);
          }
          .mantle-code {
            font-family: var(--font-mono);
            font-size: var(--text-sm);
            color: var(--color-foreground);
            background-color: var(--color-background);
            white-space: pre;
            tab-size: 2;
          }
          .mantle-code .kw { color: var(--color-accent); }
          .mantle-code .str { color: var(--color-success); }
          .mantle-code .num { color: var(--color-warning); }
          .mantle-code .cmt { color: var(--color-foreground-faint); font-style: italic; }
        `}</style>
      </div>
    </div>
  );
}

/* ─── Body renderer ─────────────────────────────────────────────────── */

interface ArtifactBodyComponentProps {
  body: ArtifactBody;
  meta: FileMeta;
  downloadUrl: string;
}

function ArtifactBody({
  body,
  meta,
  downloadUrl,
}: ArtifactBodyComponentProps): React.ReactElement {
  if (body.type === 'image') {
    return <ImageViewer url={body.url} alt={meta.name} />;
  }
  if (body.type === 'pdf') {
    const viewerUrl = `/pdfjs/web/viewer.html?file=${encodeURIComponent(body.url)}`;
    return (
      <iframe
        title={`PDF.js preview for ${meta.name}`}
        src={viewerUrl}
        loading="lazy"
        style={{ flex: 1, width: '100%', minHeight: 0, border: 0, backgroundColor: 'var(--color-background)' }}
      >
        <div
          style={{
            display: 'flex',
            flex: 1,
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 'var(--spacing-3)',
            padding: 'var(--spacing-6)',
            color: 'var(--color-foreground-muted)',
            fontSize: 'var(--text-sm)',
          }}
        >
          <div>Your browser cannot display this PDF inline.</div>
          <a
            href={downloadUrl}
            download={meta.name}
            style={{ color: 'var(--color-accent)' }}
          >
            Download PDF
          </a>
        </div>
      </iframe>
    );
  }
  if (body.type === 'pptx') {
    return (
      <div
        data-testid="pptx-preview"
        style={{ flex: 1, overflow: 'auto', padding: 'var(--spacing-8)', backgroundColor: 'var(--color-background)' }}
      >
        <div
          style={{
            aspectRatio: '16 / 9',
            maxWidth: 760,
            margin: '0 auto var(--spacing-4)',
            padding: 'var(--spacing-8)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-lg)',
            background: 'linear-gradient(135deg, var(--color-background-elevated), var(--color-background-subtle))',
            boxShadow: 'var(--shadow-sm)',
          }}
        >
          <div style={{ fontSize: 'var(--text-2xl)', fontWeight: 'var(--font-weight-semibold)', marginBottom: 'var(--spacing-4)' }}>
            {body.title}
          </div>
          <ul style={{ margin: 0, paddingLeft: 'var(--spacing-6)', color: 'var(--color-foreground-muted)' }}>
            {body.text.map((line, index) => (
              <li key={`${line}-${index}`} style={{ marginBottom: 'var(--spacing-2)' }}>{line}</li>
            ))}
          </ul>
        </div>
        <a href={downloadUrl} download={meta.name} style={{ color: 'var(--color-accent)' }}>Download full PowerPoint</a>
      </div>
    );
  }
  if (body.type === 'xlsx') {
    const [header, ...rows] = body.rows;
    return (
      <div data-testid="xlsx-preview" style={{ flex: 1, overflow: 'auto', backgroundColor: 'var(--color-background)' }}>
        <div style={{ padding: 'var(--spacing-3) var(--spacing-4)', color: 'var(--color-foreground-muted)', fontSize: 'var(--text-xs)' }}>
          First sheet: {body.sheetName} (20 rows × 10 cols max)
        </div>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 'var(--text-sm)', fontFamily: 'var(--font-mono)' }}>
          <thead style={{ position: 'sticky', top: 0, backgroundColor: 'var(--color-background-elevated)' }}>
            <tr>{(header ?? []).map((cell, index) => <th key={index} style={{ textAlign: 'left', padding: 'var(--spacing-2)', borderBottom: '1px solid var(--color-border)' }}>{cell}</th>)}</tr>
          </thead>
          <tbody>
            {rows.map((row, rowIndex) => (
              <tr key={rowIndex}>{row.map((cell, cellIndex) => <td key={cellIndex} style={{ padding: 'var(--spacing-1) var(--spacing-2)', borderBottom: '1px solid var(--color-border)' }}>{cell}</td>)}</tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }
  if (body.type === 'docx') {
    return (
      <div
        data-testid="docx-preview"
        style={{ flex: 1, overflow: 'auto', padding: 'var(--spacing-8)', backgroundColor: 'var(--color-background)' }}
      >
        <article
          style={{
            maxWidth: 760,
            margin: '0 auto',
            padding: 'var(--spacing-8)',
            border: '1px solid var(--color-border)',
            backgroundColor: 'var(--color-background-elevated)',
            lineHeight: 1.7,
            whiteSpace: 'pre-wrap',
          }}
        >
          {body.text || 'No preview text found.'}
        </article>
      </div>
    );
  }
  if (body.type === 'markdown') {
    return (
      <div
        className="mantle-md"
        style={{
          flex: 1,
          overflow: 'auto',
          padding: 'var(--spacing-6) var(--spacing-8)',
          fontSize: 'var(--text-base)',
          color: 'var(--color-foreground)',
          backgroundColor: 'var(--color-background)',
        }}
        // eslint-disable-next-line react/no-danger
        dangerouslySetInnerHTML={{ __html: renderMarkdown(body.content) }}
      />
    );
  }
  if (body.type === 'json') {
    return (
      <div
        style={{
          flex: 1,
          overflow: 'auto',
          padding: 'var(--spacing-3) var(--spacing-4)',
          backgroundColor: 'var(--color-background)',
        }}
      >
        <JsonNode value={body.parsed} depth={0} />
      </div>
    );
  }
  if (body.type === 'csv') {
    const [header, ...rest] = body.rows;
    return (
      <div
        style={{
          flex: 1,
          overflow: 'auto',
          backgroundColor: 'var(--color-background)',
        }}
      >
        <table
          style={{
            width: '100%',
            borderCollapse: 'collapse',
            fontSize: 'var(--text-sm)',
            fontFamily: 'var(--font-mono)',
            color: 'var(--color-foreground)',
          }}
        >
          <thead
            style={{
              position: 'sticky',
              top: 0,
              backgroundColor: 'var(--color-background-elevated)',
              zIndex: 1,
            }}
          >
            <tr>
              {(header ?? []).map((cell, i) => (
                <th
                  key={i}
                  style={{
                    textAlign: 'left',
                    padding: 'var(--spacing-2) var(--spacing-3)',
                    fontWeight: 'var(--font-weight-semibold)',
                    color: 'var(--color-foreground)',
                    borderBottom: '1px solid var(--color-border)',
                    whiteSpace: 'nowrap',
                  }}
                >
                  {cell}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rest.map((row, ri) => (
              <tr key={ri}>
                {row.map((cell, ci) => (
                  <td
                    key={ci}
                    style={{
                      padding: 'var(--spacing-1) var(--spacing-3)',
                      borderBottom: '1px solid var(--color-border)',
                      whiteSpace: 'nowrap',
                      color: 'var(--color-foreground)',
                    }}
                  >
                    {cell}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }
  if (body.type === 'text') {
    return (
      <pre
        className="mantle-code"
        style={{
          flex: 1,
          margin: 0,
          overflow: 'auto',
          padding: 'var(--spacing-4)',
          backgroundColor: 'var(--color-background)',
          color: 'var(--color-foreground)',
          fontFamily: 'var(--font-mono)',
          fontSize: 'var(--text-sm)',
          lineHeight: 1.6,
        }}
      >
        <code>{body.content}</code>
      </pre>
    );
  }
  // Binary
  return (
    <div
      style={{
        display: 'flex',
        flex: 1,
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 'var(--spacing-3)',
        padding: 'var(--spacing-8)',
        color: 'var(--color-foreground-muted)',
        fontSize: 'var(--text-sm)',
        textAlign: 'center',
      }}
    >
      <div
        style={{
          fontSize: 'var(--text-base)',
          fontWeight: 'var(--font-weight-medium)',
          color: 'var(--color-foreground)',
        }}
      >
        Binary file
      </div>
      <dl
        style={{
          display: 'grid',
          gridTemplateColumns: 'auto 1fr',
          columnGap: 'var(--spacing-4)',
          rowGap: 'var(--spacing-1)',
          textAlign: 'left',
          fontFamily: 'var(--font-mono)',
          fontSize: 'var(--text-xs)',
          color: 'var(--color-foreground-muted)',
        }}
      >
        <dt>type</dt>
        <dd style={{ margin: 0, color: 'var(--color-foreground)' }}>{meta.mime || 'unknown'}</dd>
        <dt>size</dt>
        <dd style={{ margin: 0, color: 'var(--color-foreground)' }}>{formatBytes(meta.size)}</dd>
        {meta.lastModified ? (
          <>
            <dt>modified</dt>
            <dd style={{ margin: 0, color: 'var(--color-foreground)' }}>{meta.lastModified}</dd>
          </>
        ) : null}
      </dl>
      <Button
        variant="primary"
        size="sm"
        iconLeft={<Download size={14} strokeWidth={1.5} />}
        onClick={() => {
          const a = document.createElement('a');
          a.href = downloadUrl;
          a.download = meta.name;
          document.body.appendChild(a);
          a.click();
          a.remove();
        }}
      >
        Download {meta.name}
      </Button>
    </div>
  );
}

function formatBytes(bytes: number): string {
  if (!Number.isFinite(bytes) || bytes < 0) return '—';
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  let value = bytes;
  let unit = 0;
  while (value >= 1024 && unit < units.length - 1) {
    value /= 1024;
    unit += 1;
  }
  return `${value.toFixed(value < 10 && unit > 0 ? 1 : 0)} ${units[unit]}`;
}

export default ArtifactViewer;
