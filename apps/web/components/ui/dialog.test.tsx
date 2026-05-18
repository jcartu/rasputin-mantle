import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import Dialog from './dialog';

describe('Dialog', () => {
  it('renders when isOpen is true', () => {
    render(
      <Dialog isOpen={true} onClose={() => {}} title="Test Dialog">
        <p>Dialog content</p>
      </Dialog>
    );
    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByText('Test Dialog')).toBeInTheDocument();
    expect(screen.getByText('Dialog content')).toBeInTheDocument();
  });

  it('does not render when isOpen is false', () => {
    render(
      <Dialog isOpen={false} onClose={() => {}} title="Test Dialog">
        <p>Dialog content</p>
      </Dialog>
    );
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('calls onClose when close button is clicked', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    render(
      <Dialog isOpen={true} onClose={onClose} title="Test Dialog">
        <p>Dialog content</p>
      </Dialog>
    );
    
    const closeBtn = screen.getByLabelText('Close dialog');
    await user.click(closeBtn);
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('calls onClose when overlay is clicked', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    render(
      <Dialog isOpen={true} onClose={onClose} title="Test Dialog">
        <p>Dialog content</p>
      </Dialog>
    );
    
    // The overlay is the first div inside the dialog container
    // We can find it by aria-hidden="true"
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
      <Dialog isOpen={true} onClose={onClose} title="Test Dialog" closeOnOverlay={false}>
        <p>Dialog content</p>
      </Dialog>
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
      <Dialog isOpen={true} onClose={onClose} title="Test Dialog">
        <p>Dialog content</p>
      </Dialog>
    );
    
    await user.keyboard('{Escape}');
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('renders footer when provided', () => {
    render(
      <Dialog 
        isOpen={true} 
        onClose={() => {}} 
        title="Test Dialog"
        footer={<button>Save</button>}
      >
        <p>Dialog content</p>
      </Dialog>
    );
    expect(screen.getByText('Save')).toBeInTheDocument();
  });
});
