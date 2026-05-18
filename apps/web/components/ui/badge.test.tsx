import * as React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Badge } from './badge';

describe('Badge', () => {
  it('renders correctly with default props', () => {
    render(<Badge>Default Badge</Badge>);
    const badge = screen.getByText('Default Badge');
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveStyle({
      backgroundColor: 'var(--color-muted)',
      color: 'var(--color-foreground-muted)',
      height: '22px',
      padding: '2px 8px',
    });
  });

  it('renders success variant', () => {
    render(<Badge variant="success">Success</Badge>);
    const badge = screen.getByText('Success');
    expect(badge).toHaveStyle({
      backgroundColor: 'var(--color-success-subtle)',
      color: 'var(--color-success)',
    });
  });

  it('renders sm size', () => {
    render(<Badge size="sm">Small</Badge>);
    const badge = screen.getByText('Small');
    expect(badge).toHaveStyle({
      height: '18px',
      padding: '2px 6px',
    });
  });
});
