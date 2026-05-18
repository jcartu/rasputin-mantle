'use client';

import * as React from 'react';
import { Maximize2, Minimize2, Camera, Plus, X, WifiOff } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Skeleton } from '@/components/ui/skeleton';

export interface BrowserTab {
  id: string;
  title: string;
  url?: string;
}

export interface ComputerViewProps {
  sessionId: string;
  nekoUrl?: string;
  screenshotUrl?: string | null;
  readOnly?: boolean;
  onTakeControl?: (taken: boolean) => void;
  isControlTaken: boolean;
  tabs?: BrowserTab[];
  activeTabId?: string;
  onTabSelect?: (tabId: string) => void;
  onTabClose?: (tabId: string) => void;
  onTabNew?: () => void;
  onScreenshot?: () => void;
}

const HOVER_REVEAL_MS = 120;

export function ComputerView({
  sessionId,
  nekoUrl,
  screenshotUrl,
  readOnly = false,
  onTakeControl,
  isControlTaken,
  tabs,
  activeTabId,
  onTabSelect,
  onTabClose,
  onTabNew,
  onScreenshot,
}: ComputerViewProps): React.ReactElement {
  const resolvedUrl =
    nekoUrl ?? (typeof process !== 'undefined' ? process.env.NEXT_PUBLIC_NEKO_URL : undefined);
  const containerRef = React.useRef<HTMLDivElement>(null);
  const iframeRef = React.useRef<HTMLIFrameElement>(null);
  const [isFullscreen, setIsFullscreen] = React.useState(false);
  const [isDisconnected, setIsDisconnected] = React.useState(false);
  const [hovering, setHovering] = React.useState(false);
  const [iframeKey, setIframeKey] = React.useState(0);
  const hoverTimer = React.useRef<ReturnType<typeof setTimeout> | null>(null);

  React.useEffect(() => {
    const onFs = () => {
      setIsFullscreen(Boolean(document.fullscreenElement));
    };
    document.addEventListener('fullscreenchange', onFs);
    return () => document.removeEventListener('fullscreenchange', onFs);
  }, []);

  // Watch for disconnection via window message channel from neko (best-effort).
  React.useEffect(() => {
    if (!resolvedUrl) return;
    const handler = (ev: MessageEvent) => {
      if (typeof ev.data !== 'object' || ev.data === null) return;
      const data = ev.data as { type?: string; sessionId?: string };
      if (data.sessionId && data.sessionId !== sessionId) return;
      if (data.type === 'neko:disconnect') setIsDisconnected(true);
      if (data.type === 'neko:connect') setIsDisconnected(false);
    };
    window.addEventListener('message', handler);
    return () => window.removeEventListener('message', handler);
  }, [resolvedUrl, sessionId]);

  const handleFullscreen = React.useCallback(async () => {
    const el = containerRef.current;
    if (!el) return;
    if (document.fullscreenElement) {
      await document.exitFullscreen();
    } else {
      await el.requestFullscreen();
    }
  }, []);

  const handleReconnect = React.useCallback(() => {
    setIsDisconnected(false);
    setIframeKey((k) => k + 1);
  }, []);

  const handleMouseEnter = () => {
    if (hoverTimer.current) clearTimeout(hoverTimer.current);
    hoverTimer.current = setTimeout(() => setHovering(true), HOVER_REVEAL_MS);
  };
  const handleMouseLeave = () => {
    if (hoverTimer.current) clearTimeout(hoverTimer.current);
    setHovering(false);
  };

  const overlayBaseStyle: React.CSSProperties = {
    position: 'absolute',
    display: 'inline-flex',
    alignItems: 'center',
    gap: 'var(--spacing-2)',
    padding: 'var(--spacing-2) var(--spacing-3)',
    backgroundColor: 'var(--color-background-elevated)',
    border: '1px solid var(--color-border)',
    borderRadius: 'var(--radius-md)',
    boxShadow: 'var(--shadow-sm)',
    fontSize: 'var(--text-xs)',
    color: 'var(--color-foreground-muted)',
    transition: 'opacity var(--duration-default) var(--ease-default)',
    opacity: hovering ? 1 : 0.85,
    zIndex: 2,
  };

  const renderEmpty = (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 'var(--spacing-4)',
        padding: 'var(--spacing-6)',
        backgroundColor: 'var(--color-background)',
      }}
    >
      <Skeleton variant="block" style={{ width: '60%', maxWidth: 480, height: 280 }} />
      <div
        style={{
          fontSize: 'var(--text-sm)',
          color: 'var(--color-foreground-muted)',
          letterSpacing: '0.02em',
        }}
      >
        Sandbox initializing…
      </div>
      <div
        style={{
          fontSize: 'var(--text-xs)',
          color: 'var(--color-foreground-faint)',
          fontFamily: 'var(--font-mono)',
        }}
      >
        session: {sessionId}
      </div>
    </div>
  );

  const renderDisconnected = (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 'var(--spacing-3)',
        backgroundColor: 'color-mix(in oklch, var(--color-background) 88%, transparent)',
        backdropFilter: 'none',
        zIndex: 4,
      }}
    >
      <WifiOff size={24} strokeWidth={1.5} color="var(--color-destructive)" />
      <div
        style={{
          fontSize: 'var(--text-base)',
          color: 'var(--color-foreground)',
          fontWeight: 'var(--font-weight-medium)',
        }}
      >
        Connection lost
      </div>
      <div
        style={{
          fontSize: 'var(--text-xs)',
          color: 'var(--color-foreground-muted)',
          maxWidth: 320,
          textAlign: 'center',
        }}
      >
        The sandbox stream dropped. Reconnect to resume the live view.
      </div>
      <Button variant="primary" size="sm" onClick={handleReconnect}>
        Reconnect
      </Button>
    </div>
  );

  return (
    <div
      ref={containerRef}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      data-session-id={sessionId}
      style={{
        position: 'relative',
        width: '100%',
        height: '100%',
        backgroundColor: 'var(--color-background)',
        overflow: 'hidden',
      }}
    >
      {screenshotUrl ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={screenshotUrl}
          alt="Replay screenshot"
          style={{
            position: 'absolute',
            inset: 0,
            width: '100%',
            height: '100%',
            objectFit: 'contain',
            backgroundColor: 'var(--color-background)',
          }}
        />
      ) : resolvedUrl ? (
        <iframe
          key={iframeKey}
          ref={iframeRef}
          title="Sandbox computer view"
          src={resolvedUrl}
          allow="clipboard-read; clipboard-write; fullscreen; autoplay; microphone; camera"
          style={{
            position: 'absolute',
            inset: 0,
            width: '100%',
            height: '100%',
            border: 'none',
            backgroundColor: 'var(--color-background)',
          }}
        />
      ) : (
        renderEmpty
      )}

      {/* Top-right chrome */}
      {resolvedUrl && !readOnly && !screenshotUrl ? (
        <div
          style={{
            ...overlayBaseStyle,
            top: 'var(--spacing-3)',
            right: 'var(--spacing-3)',
          }}
        >
          <label
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 'var(--spacing-2)',
              cursor: 'pointer',
              userSelect: 'none',
              color: 'var(--color-foreground)',
            }}
          >
            <Switch
              size="sm"
              checked={isControlTaken}
              onCheckedChange={(v) => onTakeControl?.(v)}
              aria-label="Take control of sandbox"
            />
            <span>{isControlTaken ? 'You have control' : 'Take control'}</span>
          </label>
          <span
            aria-hidden
            style={{
              width: 1,
              height: 16,
              backgroundColor: 'var(--color-border)',
              display: 'inline-block',
            }}
          />
          <Button
            variant="ghost"
            size="sm"
            iconOnly={
              isFullscreen ? (
                <Minimize2 size={14} strokeWidth={1.5} />
              ) : (
                <Maximize2 size={14} strokeWidth={1.5} />
              )
            }
            aria-label={isFullscreen ? 'Exit fullscreen' : 'Enter fullscreen'}
            aria-pressed={isFullscreen}
            onClick={handleFullscreen}
          />
          <Button
            variant="ghost"
            size="sm"
            iconOnly={<Camera size={14} strokeWidth={1.5} />}
            aria-label="Capture screenshot"
            onClick={() => onScreenshot?.()}
          />
        </div>
      ) : null}

      {/* Bottom-center tab strip (reveals on hover) */}
      {resolvedUrl && tabs && tabs.length > 0 ? (
        <div
          style={{
            position: 'absolute',
            bottom: 'var(--spacing-3)',
            left: '50%',
            transform: `translateX(-50%) translateY(${hovering ? 0 : 8}px)`,
            opacity: hovering ? 1 : 0,
            pointerEvents: hovering ? 'auto' : 'none',
            transition: 'all var(--duration-default) var(--ease-default)',
            display: 'inline-flex',
            alignItems: 'center',
            gap: 'var(--spacing-1)',
            padding: 'var(--spacing-1)',
            backgroundColor: 'var(--color-background-elevated)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-md)',
            boxShadow: 'var(--shadow-sm)',
            maxWidth: '80%',
            overflow: 'hidden',
            zIndex: 3,
          }}
          role="tablist"
          aria-label="Browser tabs"
        >
          {tabs.map((tab) => {
            const active = tab.id === activeTabId;
            return (
              <div
                key={tab.id}
                role="tab"
                aria-selected={active}
                onClick={() => onTabSelect?.(tab.id)}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 'var(--spacing-1)',
                  padding: 'var(--spacing-1) var(--spacing-2)',
                  backgroundColor: active
                    ? 'var(--color-background-subtle)'
                    : 'transparent',
                  color: active
                    ? 'var(--color-foreground)'
                    : 'var(--color-foreground-muted)',
                  border: active
                    ? '1px solid var(--color-border-strong)'
                    : '1px solid transparent',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: 'var(--text-xs)',
                  cursor: 'pointer',
                  maxWidth: 180,
                  transition: 'all var(--duration-fast) var(--ease-default)',
                }}
              >
                <span
                  style={{
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                  }}
                >
                  {tab.title}
                </span>
                {onTabClose ? (
                  <button
                    type="button"
                    aria-label={`Close ${tab.title}`}
                    onClick={(e) => {
                      e.stopPropagation();
                      onTabClose(tab.id);
                    }}
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      width: 16,
                      height: 16,
                      padding: 0,
                      background: 'transparent',
                      border: 'none',
                      borderRadius: 'var(--radius-sm)',
                      color: 'currentColor',
                      cursor: 'pointer',
                    }}
                  >
                    <X size={12} strokeWidth={1.5} />
                  </button>
                ) : null}
              </div>
            );
          })}
          {onTabNew ? (
            <Button
              variant="ghost"
              size="xs"
              iconOnly={<Plus size={12} strokeWidth={1.5} />}
              aria-label="New browser tab"
              onClick={onTabNew}
            />
          ) : null}
        </div>
      ) : null}

      {isDisconnected && resolvedUrl ? renderDisconnected : null}
    </div>
  );
}

export default ComputerView;
