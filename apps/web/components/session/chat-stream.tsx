'use client';

import * as React from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import {
  ToolCallCard,
  type ToolCallEvent,
  type ToolCallEventType,
  type ToolCallEventData,
  type ToolCallEventTokens,
} from '@/components/session/tool-call-card';
import {
  CostGutter,
  type CostGutterEvent,
} from '@/components/session/cost-gutter';

export interface StreamEvent extends ToolCallEvent {
  id?: string;
  model?: string;
}

export interface ChatStreamProps {
  sessionId: string;
}

type ConnectionStatus = 'connecting' | 'connected' | 'error';

const VALID_EVENT_TYPES: ReadonlyArray<ToolCallEventType> = [
  'tool_call',
  'reasoning',
  'file_touch',
  'screenshot',
  'error',
  'completion',
];

const isToolCallEventType = (value: unknown): value is ToolCallEventType =>
  typeof value === 'string' &&
  (VALID_EVENT_TYPES as ReadonlyArray<string>).includes(value);

const parseStreamEvent = (raw: string): StreamEvent | null => {
  try {
    const parsed: unknown = JSON.parse(raw);
    if (typeof parsed !== 'object' || parsed === null) return null;
    const obj = parsed as Record<string, unknown>;
    if (!isToolCallEventType(obj.type)) return null;
    const data =
      typeof obj.data === 'object' && obj.data !== null
        ? (obj.data as ToolCallEventData)
        : ({} as ToolCallEventData);
    const timestamp =
      typeof obj.timestamp === 'string'
        ? obj.timestamp
        : new Date().toISOString();
    const cost = typeof obj.cost === 'number' ? obj.cost : undefined;
    const tokensRaw =
      typeof obj.tokens === 'object' && obj.tokens !== null
        ? (obj.tokens as Record<string, unknown>)
        : null;
    const tokens: ToolCallEventTokens | undefined =
      tokensRaw &&
      typeof tokensRaw.input === 'number' &&
      typeof tokensRaw.output === 'number'
        ? { input: tokensRaw.input, output: tokensRaw.output }
        : undefined;
    const id = typeof obj.id === 'string' ? obj.id : undefined;
    const model = typeof obj.model === 'string' ? obj.model : undefined;
    return { type: obj.type, data, timestamp, cost, tokens, id, model };
  } catch {
    return null;
  }
};

const entranceVariants = {
  hidden: { opacity: 0, y: 8 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.2, ease: [0, 0, 0.2, 1] as const },
  },
};

const SCROLL_THRESHOLD_PX = 64;

export function ChatStream({ sessionId }: ChatStreamProps) {
  const [events, setEvents] = React.useState<StreamEvent[]>([]);
  const [status, setStatus] = React.useState<ConnectionStatus>('connecting');
  const [retryNonce, setRetryNonce] = React.useState(0);
  const scrollRef = React.useRef<HTMLDivElement>(null);
  const stickToBottomRef = React.useRef(true);

  React.useEffect(() => {
    if (typeof window === 'undefined') return;
    setStatus('connecting');

    const source = new EventSource(`/api/sessions/${sessionId}/stream`);

    source.onopen = () => {
      setStatus('connected');
    };

    source.onmessage = (e: MessageEvent<string>) => {
      const parsed = parseStreamEvent(e.data);
      if (parsed) {
        setEvents((prev) => [...prev, parsed]);
      }
    };

    source.onerror = () => {
      setStatus('error');
      source.close();
    };

    return () => {
      source.close();
    };
  }, [sessionId, retryNonce]);

  const handleScroll = React.useCallback(() => {
    const el = scrollRef.current;
    if (!el) return;
    const distanceFromBottom =
      el.scrollHeight - el.scrollTop - el.clientHeight;
    stickToBottomRef.current = distanceFromBottom <= SCROLL_THRESHOLD_PX;
  }, []);

  React.useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    if (stickToBottomRef.current) {
      el.scrollTop = el.scrollHeight;
    }
  }, [events]);

  const handleRetry = React.useCallback(() => {
    setRetryNonce((n) => n + 1);
  }, []);

  const gutterEvents = React.useMemo<CostGutterEvent[]>(
    () => events.map((e) => ({ ...e, model: e.model })),
    [events]
  );

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        minHeight: 0,
        backgroundColor: 'var(--color-background)',
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: 'var(--spacing-2) var(--spacing-4)',
          borderBottom: '1px solid var(--color-border)',
          fontSize: 'var(--text-xs)',
          color: 'var(--color-foreground-muted)',
          flexShrink: 0,
        }}
      >
        <span style={{ fontFamily: 'var(--font-mono)' }}>
          session {sessionId}
        </span>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--spacing-2)',
          }}
        >
          <span
            aria-hidden
            style={{
              width: '8px',
              height: '8px',
              borderRadius: 'var(--radius-full)',
              backgroundColor:
                status === 'connected'
                  ? 'var(--color-success)'
                  : status === 'connecting'
                    ? 'var(--color-warning)'
                    : 'var(--color-destructive)',
            }}
          />
          <span style={{ textTransform: 'capitalize' }}>{status}</span>
        </div>
      </div>

      <div
        ref={scrollRef}
        onScroll={handleScroll}
        style={{
          flex: 1,
          minHeight: 0,
          overflowY: 'auto',
          padding: 'var(--spacing-4)',
        }}
      >
        {status === 'connecting' && events.length === 0 && (
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              gap: 'var(--spacing-2)',
            }}
            aria-label="Loading event stream"
          >
            <Skeleton variant="block" height={64} />
            <Skeleton variant="block" height={48} />
            <Skeleton variant="block" height={80} />
          </div>
        )}

        {status === 'error' && events.length === 0 && (
          <div
            role="alert"
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 'var(--spacing-3)',
              padding: 'var(--spacing-8)',
              color: 'var(--color-foreground-muted)',
            }}
          >
            <AlertCircle
              size={24}
              strokeWidth={1.5}
              style={{ color: 'var(--color-destructive)' }}
            />
            <p
              style={{
                margin: 0,
                fontSize: 'var(--text-sm)',
                color: 'var(--color-foreground)',
                textAlign: 'center',
              }}
            >
              Connection to event stream failed
            </p>
            <Button
              variant="secondary"
              size="sm"
              iconLeft={<RefreshCw size={14} strokeWidth={1.5} />}
              onClick={handleRetry}
            >
              Retry
            </Button>
          </div>
        )}

        {events.length > 0 && (
          <div
            style={{
              display: 'flex',
              alignItems: 'stretch',
              gap: 'var(--spacing-3)',
            }}
          >
            <CostGutter events={gutterEvents} />
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                gap: 'var(--spacing-2)',
                flex: 1,
                minWidth: 0,
              }}
            >
              <AnimatePresence initial={false}>
                {events.map((event, idx) => (
                  <motion.div
                    key={event.id ?? `${event.timestamp}-${idx}`}
                    variants={entranceVariants}
                    initial="hidden"
                    animate="visible"
                  >
                    <ToolCallCard event={event} />
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ChatStream;
