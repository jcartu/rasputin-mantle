import * as React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Card, CardHeader, CardBody, CardFooter } from './card';

describe('Card', () => {
  it('renders correctly', () => {
    render(
      <Card data-testid="card">
        <CardHeader data-testid="header" withBorder>Header</CardHeader>
        <CardBody data-testid="body">Body</CardBody>
        <CardFooter data-testid="footer" withBorder>Footer</CardFooter>
      </Card>
    );

    const card = screen.getByTestId('card');
    expect(card).toBeInTheDocument();
    expect(card).toHaveAttribute('style', expect.stringContaining('background-color: var(--color-background-elevated)'));
    expect(card).toHaveAttribute('style', expect.stringContaining('border: 1px solid var(--color-border)'));
    expect(card).toHaveAttribute('style', expect.stringContaining('border-radius: var(--radius-md)'));

    const header = screen.getByTestId('header');
    expect(header).toHaveAttribute('style', expect.stringContaining('padding: 16px'));
    expect(header).toHaveAttribute('style', expect.stringContaining('border-bottom: 1px solid var(--color-border)'));

    const body = screen.getByTestId('body');
    expect(body).toHaveAttribute('style', expect.stringContaining('padding: 16px'));

    const footer = screen.getByTestId('footer');
    expect(footer).toHaveAttribute('style', expect.stringContaining('padding: 16px'));
    expect(footer).toHaveAttribute('style', expect.stringContaining('border-top: 1px solid var(--color-border)'));
  });

  it('handles hover state', () => {
    render(<Card data-testid="card">Content</Card>);
    const card = screen.getByTestId('card');
    
    fireEvent.mouseEnter(card);
    expect(card).toHaveAttribute('style', expect.stringContaining('border-color: var(--color-border-strong)'));

    fireEvent.mouseLeave(card);
    expect(card).toHaveAttribute('style', expect.stringContaining('border-color: var(--color-border)'));
  });
});
