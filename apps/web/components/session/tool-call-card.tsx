'use client';

import * as React from 'react';
import {
  Wrench,
  ChevronDown,
  ChevronRight,
  FileText,
  Image as ImageIcon,
  AlertCircle,
  CheckCircle2,
  Brain,
  X,
} from 'lucide-react';
import { Card, CardBody } from '@/components/ui/card';

export type ToolCallEventType =
  | 'tool_call'
  | 'reasoning'
  | 'file_touch'
  | 'screenshot'
  | 'error'
  | 'completion';

export interface ToolCallEventTokens {
  input: number;
  output: number;
}

export interface ToolCallEventData {
  // tool_call
  tool?: string;
  target?: string;
  args?: Record<string, unknown>;
  result?: unknown;
  // reasoning
  text?: string;
  // file_touch
  path?: string;
  added?: number;
  removed?: number;
  // screenshot
  src?: string;
  alt?: string;
  // error
  message?: string;
  stack?: string;
  // completion
  answer?: string;
  totalCost?: number;
}

export interface ToolCallEvent {
  type: ToolCallEventType;
  data: ToolCallEventData;
  timestamp: string;
  cost?: number;
  tokens?: ToolCallEventTokens;
}

export interface ToolCallCardProps {
  event: ToolCallEvent;
}

const formatTimestamp = (ts: string): string => {
  const d = new Date(ts);
  if (Number.isNaN(d.getTime())) return ts;
  return d.toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
};

const formatCost = (cost: number): string => {
  if (cost < 0.01) return `$${cost.toFixed(4)}`;
  return `$${cost.toFixed(3)}`;
};

const accentBarStyle = (color: string): React.CSSProperties => ({
  position: 'absolute',
  left: 0,
  top: 0,
  bottom: 0,
  width: '3px',
  backgroundColor: color,
});

const metaRowStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 'var(--spacing-2)',
  fontSize: 'var(--text-xs)',
  color: 'var(--color-foreground-faint)',
  fontVariantNumeric: 'tabular-nums',
};

const expanderButtonStyle: React.CSSProperties = {
  display: 'inline-flex',
  alignItems: 'center',
  gap: 'var(--spacing-1)',
  background: 'transparent',
  border: 'none',
  color: 'var(--color-foreground-muted)',
  fontSize: 'var(--text-xs)',
  fontFamily: 'var(--font-sans)',
  cursor: 'pointer',
  padding: 0,
  marginTop: 'var(--spacing-2)',
  transition: 'color var(--duration-fast) var(--ease-default)',
};

const preStyle: React.CSSProperties = {
  margin: 0,
  marginTop: 'var(--spacing-2)',
  padding: 'var(--spacing-3)',
  fontFamily: 'var(--font-mono)',
  fontSize: 'var(--text-xs)',
  lineHeight: 1.5,
  color: 'var(--color-foreground)',
  backgroundColor: 'var(--color-background-subtle)',
  borderRadius: 'var(--radius-sm)',
  border: '1px solid var(--color-border)',
  whiteSpace: 'pre-wrap',
  wordBreak: 'break-word',
  overflowX: 'auto',
};

function CostMeta({ event }: { event: ToolCallEvent }) {
  return (
    <div style={metaRowStyle}>
      <span>{formatTimestamp(event.timestamp)}</span>
      {typeof event.cost === 'number' && (
        <>
          <span aria-hidden>·</span>
          <span>{formatCost(event.cost)}</span>
        </>
      )}
      {event.tokens && (
        <>
          <span aria-hidden>·</span>
          <span>
            {event.tokens.input}↑ {event.tokens.output}↓
          </span>
        </>
      )}
    </div>
  );
}

function ToolCallBody({ event }: { event: ToolCallEvent }) {
  const [open, setOpen] = React.useState(false);
  const tool = event.data.tool ?? 'tool';
  const target = event.data.target ?? '';
  const hasDetails =
    event.data.args !== undefined || event.data.result !== undefined;

  return (
    <>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--spacing-2)',
        }}
      >
        <Wrench
          size={16}
          strokeWidth={1.5}
          style={{ color: 'var(--color-accent)', flexShrink: 0 }}
        />
        <span
          style={{
            fontFamily: 'var(--font-mono)',
            fontSize: 'var(--text-sm)',
            color: 'var(--color-foreground)',
            fontWeight: 'var(--font-weight-medium)',
          }}
        >
          {tool}
        </span>
        {target && (
          <span
            style={{
              fontSize: 'var(--text-sm)',
              color: 'var(--color-foreground-muted)',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}
          >
            {target}
          </span>
        )}
      </div>
      <CostMeta event={event} />
      {hasDetails && (
        <button
          type="button"
          style={expanderButtonStyle}
          aria-expanded={open}
          onClick={() => setOpen((p) => !p)}
        >
          {open ? (
            <ChevronDown size={14} strokeWidth={1.5} />
          ) : (
            <ChevronRight size={14} strokeWidth={1.5} />
          )}
          <span>{open ? 'hide details' : 'show details'}</span>
        </button>
      )}
      {open && hasDetails && (
        <div>
          {event.data.args !== undefined && (
            <pre style={preStyle}>
              <span style={{ color: 'var(--color-foreground-muted)' }}>
                args:{'\n'}
              </span>
              {JSON.stringify(event.data.args, null, 2)}
            </pre>
          )}
          {event.data.result !== undefined && (
            <pre style={preStyle}>
              <span style={{ color: 'var(--color-foreground-muted)' }}>
                result:{'\n'}
              </span>
              {typeof event.data.result === 'string'
                ? event.data.result
                : JSON.stringify(event.data.result, null, 2)}
            </pre>
          )}
        </div>
      )}
    </>
  );
}

function ReasoningBody({ event }: { event: ToolCallEvent }) {
  return (
    <>
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-start',
          gap: 'var(--spacing-2)',
        }}
      >
        <Brain
          size={16}
          strokeWidth={1.5}
          style={{
            color: 'var(--color-foreground-faint)',
            flexShrink: 0,
            marginTop: '2px',
          }}
        />
        <p
          style={{
            margin: 0,
            fontSize: 'var(--text-sm)',
            lineHeight: 1.55,
            color: 'var(--color-foreground-muted)',
            fontStyle: 'italic',
          }}
        >
          {event.data.text ?? ''}
        </p>
      </div>
      <CostMeta event={event} />
    </>
  );
}

function FileTouchBody({ event }: { event: ToolCallEvent }) {
  const added = event.data.added ?? 0;
  const removed = event.data.removed ?? 0;
  return (
    <>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--spacing-2)',
        }}
      >
        <FileText
          size={16}
          strokeWidth={1.5}
          style={{ color: 'var(--color-foreground-muted)', flexShrink: 0 }}
        />
        <span
          style={{
            fontFamily: 'var(--font-mono)',
            fontSize: 'var(--text-sm)',
            color: 'var(--color-foreground)',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
            flex: 1,
            minWidth: 0,
          }}
        >
          {event.data.path ?? 'unknown file'}
        </span>
        <span
          style={{
            fontSize: 'var(--text-xs)',
            fontFamily: 'var(--font-mono)',
            fontVariantNumeric: 'tabular-nums',
            color: 'var(--color-foreground-muted)',
            flexShrink: 0,
          }}
        >
          <span style={{ color: 'var(--color-success)' }}>+{added}</span>{' '}
          <span style={{ color: 'var(--color-destructive)' }}>-{removed}</span>{' '}
          <span>lines</span>
        </span>
      </div>
      <CostMeta event={event} />
    </>
  );
}

function ScreenshotBody({ event }: { event: ToolCallEvent }) {
  const [zoom, setZoom] = React.useState(false);
  const src = event.data.src ?? '';
  const alt = event.data.alt ?? 'screenshot';

  return (
    <>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--spacing-2)',
          marginBottom: 'var(--spacing-2)',
        }}
      >
        <ImageIcon
          size={16}
          strokeWidth={1.5}
          style={{ color: 'var(--color-foreground-muted)', flexShrink: 0 }}
        />
        <span
          style={{
            fontSize: 'var(--text-sm)',
            color: 'var(--color-foreground-muted)',
          }}
        >
          {alt}
        </span>
      </div>
      {src && (
        <button
          type="button"
          onClick={() => setZoom(true)}
          style={{
            display: 'block',
            padding: 0,
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-sm)',
            overflow: 'hidden',
            backgroundColor: 'transparent',
            cursor: 'zoom-in',
            maxWidth: '320px',
            width: '100%',
          }}
          aria-label="Zoom screenshot"
        >
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={src}
            alt={alt}
            style={{
              display: 'block',
              width: '100%',
              height: 'auto',
              maxHeight: '180px',
              objectFit: 'cover',
            }}
          />
        </button>
      )}
      <CostMeta event={event} />
      {zoom && src && (
        <div
          role="dialog"
          aria-modal="true"
          aria-label="Zoomed screenshot"
          onClick={() => setZoom(false)}
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgb(0 0 0 / 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 100,
            padding: 'var(--spacing-6)',
            cursor: 'zoom-out',
          }}
        >
          <button
            type="button"
            onClick={() => setZoom(false)}
            aria-label="Close"
            style={{
              position: 'absolute',
              top: 'var(--spacing-4)',
              right: 'var(--spacing-4)',
              background: 'transparent',
              border: 'none',
              color: 'var(--color-foreground)',
              cursor: 'pointer',
              padding: 'var(--spacing-2)',
            }}
          >
            <X size={20} strokeWidth={1.5} />
          </button>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={src}
            alt={alt}
            onClick={(e) => e.stopPropagation()}
            style={{
              maxWidth: '90vw',
              maxHeight: '90vh',
              borderRadius: 'var(--radius-md)',
              boxShadow: 'var(--shadow-xl)',
            }}
          />
        </div>
      )}
    </>
  );
}

function ErrorBody({ event }: { event: ToolCallEvent }) {
  const [open, setOpen] = React.useState(false);
  return (
    <>
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-start',
          gap: 'var(--spacing-2)',
        }}
      >
        <AlertCircle
          size={16}
          strokeWidth={1.5}
          style={{
            color: 'var(--color-destructive)',
            flexShrink: 0,
            marginTop: '2px',
          }}
        />
        <div style={{ flex: 1, minWidth: 0 }}>
          <p
            style={{
              margin: 0,
              fontSize: 'var(--text-sm)',
              color: 'var(--color-destructive)',
              fontWeight: 'var(--font-weight-medium)',
              wordBreak: 'break-word',
            }}
          >
            {event.data.message ?? 'An error occurred'}
          </p>
        </div>
      </div>
      <CostMeta event={event} />
      {event.data.stack && (
        <>
          <button
            type="button"
            style={expanderButtonStyle}
            aria-expanded={open}
            onClick={() => setOpen((p) => !p)}
          >
            {open ? (
              <ChevronDown size={14} strokeWidth={1.5} />
            ) : (
              <ChevronRight size={14} strokeWidth={1.5} />
            )}
            <span>{open ? 'hide stack trace' : 'show stack trace'}</span>
          </button>
          {open && <pre style={preStyle}>{event.data.stack}</pre>}
        </>
      )}
    </>
  );
}

function CompletionBody({ event }: { event: ToolCallEvent }) {
  const totalCost = event.data.totalCost ?? event.cost;
  return (
    <>
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-start',
          gap: 'var(--spacing-2)',
        }}
      >
        <CheckCircle2
          size={16}
          strokeWidth={1.5}
          style={{
            color: 'var(--color-success)',
            flexShrink: 0,
            marginTop: '2px',
          }}
        />
        <div style={{ flex: 1, minWidth: 0 }}>
          <p
            style={{
              margin: 0,
              fontSize: 'var(--text-sm)',
              color: 'var(--color-foreground)',
              fontWeight: 'var(--font-weight-medium)',
              marginBottom: 'var(--spacing-1)',
            }}
          >
            {event.data.answer ?? 'Task complete'}
          </p>
          {typeof totalCost === 'number' && (
            <p
              style={{
                margin: 0,
                fontSize: 'var(--text-xs)',
                color: 'var(--color-success)',
                fontVariantNumeric: 'tabular-nums',
              }}
            >
              total: {formatCost(totalCost)}
              {event.tokens &&
                ` · ${event.tokens.input + event.tokens.output} tokens`}
            </p>
          )}
        </div>
      </div>
      <CostMeta event={event} />
    </>
  );
}

export const ToolCallCard = React.forwardRef<HTMLDivElement, ToolCallCardProps>(
  ({ event }, ref) => {
    const renderAccentBar = () => {
      if (event.type === 'error') {
        return <span style={accentBarStyle('var(--color-destructive)')} />;
      }
      if (event.type === 'completion') {
        return <span style={accentBarStyle('var(--color-success)')} />;
      }
      return null;
    };

    const renderBody = () => {
      switch (event.type) {
        case 'tool_call':
          return <ToolCallBody event={event} />;
        case 'reasoning':
          return <ReasoningBody event={event} />;
        case 'file_touch':
          return <FileTouchBody event={event} />;
        case 'screenshot':
          return <ScreenshotBody event={event} />;
        case 'error':
          return <ErrorBody event={event} />;
        case 'completion':
          return <CompletionBody event={event} />;
        default:
          return null;
      }
    };

    return (
      <Card ref={ref} style={{ position: 'relative' }}>
        {renderAccentBar()}
        <CardBody
          style={{
            paddingLeft:
              event.type === 'error' || event.type === 'completion'
                ? 'calc(var(--spacing-4) + 3px)'
                : 'var(--spacing-4)',
          }}
        >
          {renderBody()}
        </CardBody>
      </Card>
    );
  }
);

ToolCallCard.displayName = 'ToolCallCard';

export default ToolCallCard;
