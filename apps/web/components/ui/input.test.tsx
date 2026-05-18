import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Input } from './input';
import React from 'react';

describe('Input', () => {
  it('renders correctly', () => {
    render(<Input placeholder="Enter text" />);
    const input = screen.getByPlaceholderText('Enter text');
    expect(input).toBeDefined();
  });

  it('renders with label', () => {
    render(<Input label="Email Address" id="email" />);
    expect(screen.getByText('Email Address')).toBeDefined();
  });

  it('renders with hint', () => {
    render(<Input hint="We will never share your email." />);
    expect(screen.getByText('We will never share your email.')).toBeDefined();
  });

  it('renders with error', () => {
    render(<Input error="Invalid email address" />);
    expect(screen.getByText('Invalid email address')).toBeDefined();
    // Should render the alert icon
    expect(document.querySelector('svg')).toBeDefined();
  });

  it('handles disabled state', () => {
    render(<Input disabled placeholder="Disabled input" />);
    const input = screen.getByPlaceholderText('Disabled input') as HTMLInputElement;
    expect(input.disabled).toBe(true);
    expect(input.style.cursor).toBe('not-allowed');
  });

  it('renders with leading and trailing icons', () => {
    const LeadingIcon = <span data-testid="leading-icon">L</span>;
    const TrailingIcon = <span data-testid="trailing-icon">T</span>;
    
    render(
      <Input 
        leadingIcon={LeadingIcon} 
        trailingIcon={TrailingIcon} 
        placeholder="With icons" 
      />
    );
    
    expect(screen.getByTestId('leading-icon')).toBeDefined();
    expect(screen.getByTestId('trailing-icon')).toBeDefined();
  });

  it('handles focus and blur events', () => {
    const handleFocus = vi.fn();
    const handleBlur = vi.fn();
    
    render(
      <Input 
        placeholder="Focus me" 
        onFocus={handleFocus} 
        onBlur={handleBlur} 
      />
    );
    
    const input = screen.getByPlaceholderText('Focus me');
    
    fireEvent.focus(input);
    expect(handleFocus).toHaveBeenCalledTimes(1);
    
    fireEvent.blur(input);
    expect(handleBlur).toHaveBeenCalledTimes(1);
  });

  it('handles change events', () => {
    const handleChange = vi.fn();
    render(<Input placeholder="Type here" onChange={handleChange} />);
    
    const input = screen.getByPlaceholderText('Type here');
    fireEvent.change(input, { target: { value: 'Hello' } });
    
    expect(handleChange).toHaveBeenCalledTimes(1);
  });

  it('renders different sizes', () => {
    const { unmount } = render(<Input inputSize="sm" placeholder="Small" />);
    expect(screen.getByPlaceholderText('Small')).toBeDefined();
    unmount();
    
    render(<Input inputSize="lg" placeholder="Large" />);
    expect(screen.getByPlaceholderText('Large')).toBeDefined();
  });
});
