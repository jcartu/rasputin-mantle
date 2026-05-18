import * as React from 'react';
import { render } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Spinner } from './spinner';

describe('Spinner', () => {
  it('renders indeterminate variant by default', () => {
    const { container } = render(<Spinner data-testid="spinner" />);
    const el = container.querySelector('[data-testid="spinner"]');
    expect(el).toBeInTheDocument();
    
    const svg = container.querySelector('svg');
    expect(svg).toHaveClass('spinner-svg-indeterminate');
    expect(svg).toHaveAttribute('width', '24'); // md size
  });

  it('renders determinate variant with progress text', () => {
    const { container, getByText } = render(
      <Spinner variant="determinate" progress={75} data-testid="spinner" />
    );
    
    const svg = container.querySelector('svg');
    expect(svg).not.toHaveClass('spinner-svg-indeterminate');
    
    const text = getByText('75%');
    expect(text).toBeInTheDocument();
    expect(text).toHaveStyle({ fontSize: 'var(--text-xs)' });
  });

  it('clamps progress between 0 and 100', () => {
    const { getByText, rerender } = render(<Spinner variant="determinate" progress={150} />);
    expect(getByText('100%')).toBeInTheDocument();

    rerender(<Spinner variant="determinate" progress={-50} />);
    expect(getByText('0%')).toBeInTheDocument();
  });

  it('renders correct sizes', () => {
    const { container, rerender } = render(<Spinner size="xs" />);
    expect(container.querySelector('svg')).toHaveAttribute('width', '16');

    rerender(<Spinner size="xl" />);
    expect(container.querySelector('svg')).toHaveAttribute('width', '40');
  });
});
