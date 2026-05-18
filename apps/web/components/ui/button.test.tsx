import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './button';
import React from 'react';

describe('Button', () => {
  it('renders correctly with default props', () => {
    render(<Button>Click me</Button>);
    const button = screen.getByRole('button', { name: 'Click me' });
    expect(button).toBeDefined();
    expect(button.getAttribute('data-variant')).toBe('primary');
    expect(button.style.backgroundColor).toBe('var(--color-accent)');
  });

  it('renders all variants', () => {
    const variants = ['primary', 'secondary', 'ghost', 'destructive', 'link'] as const;
    
    variants.forEach(variant => {
      const { unmount } = render(<Button variant={variant}>{variant}</Button>);
      const button = screen.getByRole('button', { name: variant });
      expect(button.getAttribute('data-variant')).toBe(variant);
      unmount();
    });
  });

  it('renders all sizes', () => {
    const sizes = ['xs', 'sm', 'md', 'lg'] as const;
    
    sizes.forEach(size => {
      const { unmount } = render(<Button size={size}>{size}</Button>);
      const button = screen.getByRole('button', { name: size });
      expect(button).toBeDefined();
      unmount();
    });
  });

  it('handles disabled state', () => {
    render(<Button disabled>Disabled</Button>);
    const button = screen.getByRole('button', { name: 'Disabled' });
    expect(button.hasAttribute('disabled')).toBe(true);
    expect(button.style.cursor).toBe('not-allowed');
    expect(button.style.opacity).toBe('0.5');
    expect(button.style.pointerEvents).toBe('none');
  });

  it('handles loading state', () => {
    render(<Button loading>Loading</Button>);
    const button = screen.getByRole('button');
    expect(button.hasAttribute('disabled')).toBe(true);
    // Spinner should be rendered, children should not be
    expect(screen.queryByText('Loading')).toBeNull();
    expect(button.querySelector('svg')).toBeDefined();
  });

  it('renders icons', () => {
    const LeftIcon = <span data-testid="left-icon">L</span>;
    const RightIcon = <span data-testid="right-icon">R</span>;
    
    render(
      <Button iconLeft={LeftIcon} iconRight={RightIcon}>
        With Icons
      </Button>
    );
    
    expect(screen.getByTestId('left-icon')).toBeDefined();
    expect(screen.getByTestId('right-icon')).toBeDefined();
    expect(screen.getByText('With Icons')).toBeDefined();
  });

  it('renders icon only', () => {
    const Icon = <span data-testid="only-icon">O</span>;
    
    render(<Button iconOnly={Icon} aria-label="Icon button" />);
    
    expect(screen.getByTestId('only-icon')).toBeDefined();
    expect(screen.getByRole('button', { name: 'Icon button' })).toBeDefined();
  });

  it('handles click events', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    
    fireEvent.click(screen.getByRole('button', { name: 'Click me' }));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('does not fire click when disabled', () => {
    const handleClick = vi.fn();
    render(<Button disabled onClick={handleClick}>Click me</Button>);
    
    fireEvent.click(screen.getByRole('button', { name: 'Click me' }));
    expect(handleClick).not.toHaveBeenCalled();
  });
});
