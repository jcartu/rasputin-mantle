import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import Sheet from './sheet';

describe('Sheet', () => {
  it('renders when isOpen is true', () => {
    render(
      <Sheet isOpen={true} onClose={() => {}}>
        <p>Sheet content</p>
      </Sheet>
    );
    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByText('Sheet content')).toBeInTheDocument();
  });

  it('does not render when isOpen is false', () => {
    render(
      <Sheet isOpen={false} onClose={() => {}}>
        <p>Sheet content</p>
      </Sheet>
    );
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('calls onClose when close button is clicked', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    render(
      <Sheet isOpen={true} onClose={onClose}>
        <p>Sheet content</p>
      </Sheet>
    );
    
    const closeBtn = screen.getByLabelText('Close sheet');
    await user.click(closeBtn);
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('calls onClose when overlay is clicked', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    render(
      <Sheet isOpen={true} onClose={onClose}>
        <p>Sheet content</p>
      </Sheet>
    );
    
    const overlay = document.querySelector('div[aria-hidden="true"]');
    if (overlay) {
      await user.click(overlay);
      expect(onClose).toHaveBeenCalledTimes(1);
    }
  });

  it('does not call onClose when overlay is clicked and closeOnOverlay is false', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    render(
      <Sheet isOpen={true} onClose={onClose} closeOnOverlay={false}>
        <p>Sheet content</p>
      </Sheet>
    );
    
    const overlay = document.querySelector('div[aria-hidden="true"]');
    if (overlay) {
      await user.click(overlay);
      expect(onClose).not.toHaveBeenCalled();
    }
  });

  it('calls onClose when Escape key is pressed', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    render(
      <Sheet isOpen={true} onClose={onClose}>
        <p>Sheet content</p>
      </Sheet>
    );
    
    await user.keyboard('{Escape}');
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('handles swipe to dismiss', () => {
    const onClose = vi.fn();
    render(
      <Sheet isOpen={true} onClose={onClose} side="right">
        <p>Sheet content</p>
      </Sheet>
    );
    
    const sheetContainer = screen.getByText('Sheet content').parentElement;
    if (sheetContainer) {
      fireEvent.touchStart(sheetContainer, { touches: [{ clientX: 0, clientY: 0 }] });
      fireEvent.touchEnd(sheetContainer, { changedTouches: [{ clientX: 100, clientY: 0 }] });
      expect(onClose).toHaveBeenCalledTimes(1);
    }
  });
});
