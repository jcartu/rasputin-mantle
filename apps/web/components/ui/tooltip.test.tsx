import * as React from 'react';
import { render, fireEvent, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { Tooltip } from './tooltip';

describe('Tooltip', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('renders children correctly', () => {
    const { getByText } = render(
      <Tooltip content="Tooltip content">
        <button>Hover me</button>
      </Tooltip>
    );
    expect(getByText('Hover me')).toBeInTheDocument();
  });

  it('shows tooltip on mouse enter after delay', async () => {
    const { getByText, queryByRole } = render(
      <Tooltip content="Tooltip content" delay={250}>
        <button>Hover me</button>
      </Tooltip>
    );

    expect(queryByRole('tooltip')).not.toBeInTheDocument();

    fireEvent.mouseEnter(getByText('Hover me'));
    
    // Fast-forward time
    act(() => {
      vi.advanceTimersByTime(250);
    });

    expect(queryByRole('tooltip')).toBeInTheDocument();
    expect(getByText('Tooltip content')).toBeInTheDocument();
  });

  it('hides tooltip on mouse leave immediately', () => {
    const { getByText, queryByRole } = render(
      <Tooltip content="Tooltip content" delay={250}>
        <button>Hover me</button>
      </Tooltip>
    );

    fireEvent.mouseEnter(getByText('Hover me'));
    act(() => {
      vi.advanceTimersByTime(250);
    });
    expect(queryByRole('tooltip')).toBeInTheDocument();

    fireEvent.mouseLeave(getByText('Hover me'));
    expect(queryByRole('tooltip')).not.toBeInTheDocument();
  });

  it('shows tooltip on focus', () => {
    const { getByText, queryByRole } = render(
      <Tooltip content="Tooltip content" delay={250}>
        <button>Hover me</button>
      </Tooltip>
    );

    fireEvent.focus(getByText('Hover me'));
    act(() => {
      vi.advanceTimersByTime(250);
    });

    expect(queryByRole('tooltip')).toBeInTheDocument();
  });

  it('renders shortcuts if provided', () => {
    const { getByText } = render(
      <Tooltip content="Save" shortcuts={['Ctrl', 'S']} delay={0}>
        <button>Save</button>
      </Tooltip>
    );

    fireEvent.mouseEnter(getByText('Save'));
    act(() => {
      vi.advanceTimersByTime(0);
    });

    expect(getByText('Ctrl')).toBeInTheDocument();
    expect(getByText('S')).toBeInTheDocument();
    expect(getByText('+')).toBeInTheDocument();
  });
});
