import * as React from 'react';
import { render } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Skeleton } from './skeleton';

describe('Skeleton', () => {
  it('renders block variant by default', () => {
    const { container } = render(<Skeleton data-testid="skeleton" />);
    const el = container.querySelector('[data-testid="skeleton"]');
    expect(el).toBeInTheDocument();
    expect(el).toHaveStyle({ height: '48px', width: '100%' });
    expect(el).toHaveClass('skeleton-shimmer');
  });

  it('renders circle variant with correct size', () => {
    const { container } = render(<Skeleton variant="circle" size={40} data-testid="skeleton" />);
    const el = container.querySelector('[data-testid="skeleton"]');
    expect(el).toBeInTheDocument();
    expect(el).toHaveStyle({ height: '40px', width: '40px', borderRadius: 'var(--radius-full)' });
    expect(el).toHaveClass('skeleton-shimmer');
  });

  it('renders text variant with correct number of lines', () => {
    const { container } = render(<Skeleton variant="text" lines={3} data-testid="skeleton" />);
    const el = container.querySelector('[data-testid="skeleton"]');
    expect(el).toBeInTheDocument();
    
    const lines = container.querySelectorAll('.skeleton-shimmer');
    expect(lines).toHaveLength(3);
    
    // Last line should have 60% width
    expect(lines[2]).toHaveStyle({ width: '60%' });
  });

  it('applies custom className and style', () => {
    const { container } = render(
      <Skeleton className="custom-class" style={{ marginTop: '10px' }} data-testid="skeleton" />
    );
    const el = container.querySelector('[data-testid="skeleton"]');
    expect(el).toHaveClass('custom-class');
    expect(el).toHaveStyle({ marginTop: '10px' });
  });
});
