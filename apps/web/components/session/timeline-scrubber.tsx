'use client';

import * as React from 'react';
import { Pause, Play } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';

export interface ReplayStep {
  index: number;
  seq: number;
  timestamp: string | null;
  event_type: string;
  payload: Record<string, unknown>;
}

export interface TimelineScrubberProps {
  steps: ReplayStep[];
  currentStep: number;
  onStepChange: (step: number) => void;
  loading?: boolean;
}

const PLAY_INTERVAL_MS = 500;

function clampStep(value: number, max: number): number {
  if (max <= 0) return 0;
  return Math.min(Math.max(value, 0), max);
}

export function TimelineScrubber({
  steps,
  currentStep,
  onStepChange,
  loading = false,
}: TimelineScrubberProps): React.ReactElement {
  const trackRef = React.useRef<HTMLDivElement>(null);
  const [playing, setPlaying] = React.useState(false);
  const maxStep = Math.max(steps.length - 1, 0);
  const safeStep = clampStep(currentStep, maxStep);
  const progress = maxStep === 0 ? 0 : (safeStep / maxStep) * 100;

  React.useEffect(() => {
    if (!playing) return;
    const timer = window.setInterval(() => {
      onStepChange(clampStep(safeStep + 1, maxStep));
      if (safeStep >= maxStep) setPlaying(false);
    }, PLAY_INTERVAL_MS);
    return () => window.clearInterval(timer);
  }, [maxStep, onStepChange, playing, safeStep]);

  React.useEffect(() => {
    if (safeStep >= maxStep) setPlaying(false);
  }, [maxStep, safeStep]);

  const updateFromClientX = React.useCallback(
    (clientX: number) => {
      const track = trackRef.current;
      if (!track) return;
      const rect = track.getBoundingClientRect();
      const ratio = rect.width === 0 ? 0 : (clientX - rect.left) / rect.width;
      onStepChange(clampStep(Math.round(ratio * maxStep), maxStep));
    },
    [maxStep, onStepChange],
  );

  const handlePointerDown = React.useCallback(
    (event: React.PointerEvent<HTMLDivElement>) => {
      event.preventDefault();
      setPlaying(false);
      updateFromClientX(event.clientX);
      const handleMove = (moveEvent: PointerEvent) => updateFromClientX(moveEvent.clientX);
      const handleUp = () => {
        window.removeEventListener('pointermove', handleMove);
        window.removeEventListener('pointerup', handleUp);
      };
      window.addEventListener('pointermove', handleMove);
      window.addEventListener('pointerup', handleUp);
    },
    [updateFromClientX],
  );

  const handleKeyDown = React.useCallback(
    (event: React.KeyboardEvent<HTMLDivElement>) => {
      const delta = event.shiftKey ? 10 : 1;
      if (event.key === 'ArrowLeft') {
        event.preventDefault();
        setPlaying(false);
        onStepChange(clampStep(safeStep - delta, maxStep));
      } else if (event.key === 'ArrowRight') {
        event.preventDefault();
        setPlaying(false);
        onStepChange(clampStep(safeStep + delta, maxStep));
      } else if (event.key === 'Home') {
        event.preventDefault();
        setPlaying(false);
        onStepChange(0);
      } else if (event.key === 'End') {
        event.preventDefault();
        setPlaying(false);
        onStepChange(maxStep);
      }
    },
    [maxStep, onStepChange, safeStep],
  );

  if (loading) {
    return (
      <div
        aria-label="Loading replay timeline"
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--spacing-3)',
          padding: 'var(--spacing-3)',
          borderTop: '1px solid var(--color-border)',
          backgroundColor: 'var(--color-background-elevated)',
        }}
      >
        <Skeleton variant="circle" size={32} />
        <Skeleton variant="block" height={12} style={{ flex: 1 }} />
        <Skeleton variant="block" height={16} style={{ width: 80 }} />
      </div>
    );
  }

  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'auto 1fr auto',
        alignItems: 'center',
        gap: 'var(--spacing-3)',
        padding: 'var(--spacing-3)',
        borderTop: '1px solid var(--color-border)',
        backgroundColor: 'var(--color-background-elevated)',
      }}
    >
      <Button
        variant="secondary"
        size="sm"
        iconLeft={playing ? <Pause size={14} strokeWidth={1.5} /> : <Play size={14} strokeWidth={1.5} />}
        onClick={() => setPlaying((value) => !value)}
        disabled={steps.length <= 1}
      >
        {playing ? 'Pause' : 'Play'}
      </Button>

      <div
        ref={trackRef}
        role="slider"
        tabIndex={0}
        aria-label="Replay timeline"
        aria-valuemin={0}
        aria-valuemax={maxStep}
        aria-valuenow={safeStep}
        aria-valuetext={`Step ${safeStep + 1} of ${Math.max(steps.length, 1)}`}
        onPointerDown={handlePointerDown}
        onKeyDown={handleKeyDown}
        style={{
          position: 'relative',
          height: 24,
          display: 'flex',
          alignItems: 'center',
          cursor: steps.length > 1 ? 'grab' : 'default',
          outline: 'none',
        }}
      >
        <div
          aria-hidden
          style={{
            position: 'absolute',
            left: 0,
            right: 0,
            height: 6,
            borderRadius: 'var(--radius-full)',
            backgroundColor: 'var(--color-background-subtle)',
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              width: `${progress}%`,
              height: '100%',
              backgroundColor: 'var(--color-accent)',
              transition: playing ? `width ${PLAY_INTERVAL_MS}ms linear` : 'none',
            }}
          />
        </div>
        <div
          aria-hidden
          style={{
            position: 'absolute',
            left: `calc(${progress}% - 8px)`,
            width: 16,
            height: 16,
            borderRadius: 'var(--radius-full)',
            backgroundColor: 'var(--color-accent)',
            border: '2px solid var(--color-background-elevated)',
            boxShadow: 'var(--shadow-sm)',
          }}
        />
      </div>

      <div
        style={{
          fontFamily: 'var(--font-mono)',
          fontSize: 'var(--text-xs)',
          color: 'var(--color-foreground-muted)',
          whiteSpace: 'nowrap',
        }}
      >
        {safeStep + 1}/{Math.max(steps.length, 1)}
      </div>
    </div>
  );
}

export default TimelineScrubber;
