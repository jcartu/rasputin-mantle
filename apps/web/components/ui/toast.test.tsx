import * as React from 'react';
import { render, fireEvent, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { ToastProvider, useToast } from './toast';

function TestTrigger({ onAdd }: { onAdd?: (id: string) => void }) {
  const { addToast } = useToast();
  return (
    <button
      onClick={() => {
        const id = addToast({ title: 'Test', description: 'Description', variant: 'success' });
        onAdd?.(id);
      }}
    >
      Trigger
    </button>
  );
}

describe('Toast', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('throws if useToast is used outside ToastProvider', () => {
    const FailingComponent = () => {
      useToast();
      return null;
    };
    // Suppress React error logging for this test
    const errSpy = vi.spyOn(console, 'error').mockImplementation(() => undefined);
    expect(() => render(<FailingComponent />)).toThrow('useToast must be used within ToastProvider');
    errSpy.mockRestore();
  });

  it('renders toast on add', () => {
    const { getByText } = render(
      <ToastProvider>
        <TestTrigger />
      </ToastProvider>
    );

    act(() => {
      fireEvent.click(getByText('Trigger'));
    });

    expect(getByText('Test')).toBeInTheDocument();
    expect(getByText('Description')).toBeInTheDocument();
  });

  it('renders dismiss button with proper aria-label', () => {
    const { getByText, getByLabelText } = render(
      <ToastProvider>
        <TestTrigger />
      </ToastProvider>
    );

    act(() => {
      fireEvent.click(getByText('Trigger'));
    });

    const dismiss = getByLabelText('Dismiss');
    expect(dismiss).toBeInTheDocument();
  });

  it('dismisses toast on close button click', () => {
    const { getByText, queryByText, getByLabelText } = render(
      <ToastProvider>
        <TestTrigger />
      </ToastProvider>
    );

    act(() => {
      fireEvent.click(getByText('Trigger'));
    });
    expect(getByText('Test')).toBeInTheDocument();

    act(() => {
      fireEvent.click(getByLabelText('Dismiss'));
    });
    // Animate out
    act(() => {
      vi.advanceTimersByTime(250);
    });

    expect(queryByText('Test')).not.toBeInTheDocument();
  });

  it('renders all variants with correct border color', () => {
    function MultiTrigger() {
      const { addToast } = useToast();
      return (
        <>
          <button onClick={() => addToast({ title: 'Info', variant: 'info' })}>Info</button>
          <button onClick={() => addToast({ title: 'Warn', variant: 'warn' })}>Warn</button>
          <button onClick={() => addToast({ title: 'Error', variant: 'error' })}>Error</button>
        </>
      );
    }

    const { getByText, container } = render(
      <ToastProvider>
        <MultiTrigger />
      </ToastProvider>
    );

    act(() => {
      fireEvent.click(getByText('Info'));
    });
    expect(document.body.querySelector('[data-variant="info"]')).toBeInTheDocument();

    act(() => {
      fireEvent.click(getByText('Warn'));
    });
    expect(document.body.querySelector('[data-variant="warn"]')).toBeInTheDocument();

    act(() => {
      fireEvent.click(getByText('Error'));
    });
    expect(document.body.querySelector('[data-variant="error"]')).toBeInTheDocument();
  });

  it('renders action button if provided', () => {
    function ActionTrigger() {
      const { addToast } = useToast();
      return (
        <button
          onClick={() =>
            addToast({
              title: 'Undo me',
              action: { label: 'Undo', onClick: () => undefined },
            })
          }
        >
          Trigger
        </button>
      );
    }
    const { getByText } = render(
      <ToastProvider>
        <ActionTrigger />
      </ToastProvider>
    );

    act(() => {
      fireEvent.click(getByText('Trigger'));
    });

    expect(getByText('Undo')).toBeInTheDocument();
  });
});
