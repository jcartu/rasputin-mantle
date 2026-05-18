import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { TimelineScrubber, type ReplayStep } from './timeline-scrubber';

const steps: ReplayStep[] = Array.from({ length: 12 }, (_, index) => ({
  index,
  seq: index + 1,
  timestamp: '2026-05-19T00:00:00Z',
  event_type: 'reasoning',
  payload: { data: { text: `step ${index}` } },
}));

describe('TimelineScrubber', () => {
  it('renders a loading skeleton', () => {
    render(<TimelineScrubber steps={[]} currentStep={0} onStepChange={() => undefined} loading />);
    expect(screen.getByLabelText('Loading replay timeline')).toBeDefined();
  });

  it('handles keyboard step navigation', () => {
    const onStepChange = vi.fn();
    render(<TimelineScrubber steps={steps} currentStep={5} onStepChange={onStepChange} />);
    const slider = screen.getByRole('slider', { name: 'Replay timeline' });

    fireEvent.keyDown(slider, { key: 'ArrowLeft' });
    expect(onStepChange).toHaveBeenCalledWith(4);

    fireEvent.keyDown(slider, { key: 'ArrowRight', shiftKey: true });
    expect(onStepChange).toHaveBeenCalledWith(11);

    fireEvent.keyDown(slider, { key: 'Home' });
    expect(onStepChange).toHaveBeenCalledWith(0);

    fireEvent.keyDown(slider, { key: 'End' });
    expect(onStepChange).toHaveBeenCalledWith(11);
  });
});
