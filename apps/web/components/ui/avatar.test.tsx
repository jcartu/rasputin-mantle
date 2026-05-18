import * as React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Avatar } from './avatar';

describe('Avatar', () => {
  it('renders initials when no src is provided', () => {
    render(<Avatar initials="JD" data-testid="avatar" />);
    expect(screen.getByText('JD')).toBeInTheDocument();
  });

  it('truncates initials to 2 characters', () => {
    render(<Avatar initials="JDOE" />);
    expect(screen.getByText('JD')).toBeInTheDocument();
  });

  it('renders image when src is provided', () => {
    render(<Avatar src="https://example.com/avatar.jpg" alt="John Doe" />);
    const img = screen.getByAltText('John Doe');
    expect(img).toBeInTheDocument();
    expect(img).toHaveAttribute('src', 'https://example.com/avatar.jpg');
  });

  it('falls back to initials on image error', () => {
    render(<Avatar src="https://example.com/broken.jpg" alt="John Doe" initials="JD" />);
    const img = screen.getByAltText('John Doe');
    fireEvent.error(img);
    expect(screen.getByText('JD')).toBeInTheDocument();
    expect(screen.queryByAltText('John Doe')).not.toBeInTheDocument();
  });

  it('renders status dot', () => {
    const { container } = render(<Avatar initials="JD" status="online" />);
    // The status dot is the last span in the container
    const spans = container.querySelectorAll('span');
    const statusDot = spans[spans.length - 1];
    expect(statusDot).toHaveStyle({ backgroundColor: 'var(--color-success)' });
  });
});
