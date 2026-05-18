import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Textarea } from './textarea';
import React from 'react';

describe('Textarea', () => {
  it('renders correctly', () => {
    render(<Textarea placeholder="Enter text" />);
    const textarea = screen.getByPlaceholderText('Enter text');
    expect(textarea).toBeDefined();
  });

  it('renders with label', () => {
    render(<Textarea label="Description" id="desc" />);
    expect(screen.getByText('Description')).toBeDefined();
  });

  it('renders with hint', () => {
    render(<Textarea hint="Max 500 characters." />);
    expect(screen.getByText('Max 500 characters.')).toBeDefined();
  });

  it('renders with error', () => {
    render(<Textarea error="Description is required" />);
    expect(screen.getByText('Description is required')).toBeDefined();
    // Should render the alert icon
    expect(document.querySelector('svg')).toBeDefined();
  });

  it('handles disabled state', () => {
    render(<Textarea disabled placeholder="Disabled textarea" />);
    const textarea = screen.getByPlaceholderText('Disabled textarea') as HTMLTextAreaElement;
    expect(textarea.disabled).toBe(true);
    expect(textarea.style.cursor).toBe('not-allowed');
  });

  it('displays character count when maxLength is provided', () => {
    render(<Textarea maxLength={100} defaultValue="Hello" />);
    expect(screen.getByText('5/100')).toBeDefined();
  });

  it('displays custom character count', () => {
    render(<Textarea characterCount={42} maxLength={100} />);
    expect(screen.getByText('42/100')).toBeDefined();
  });

  it('updates character count on change', () => {
    render(<Textarea maxLength={100} placeholder="Type here" />);
    
    const textarea = screen.getByPlaceholderText('Type here');
    expect(screen.getByText('0/100')).toBeDefined();
    
    fireEvent.change(textarea, { target: { value: 'Hello World' } });
    expect(screen.getByText('11/100')).toBeDefined();
  });

  it('handles focus and blur events', () => {
    const handleFocus = vi.fn();
    const handleBlur = vi.fn();
    
    render(
      <Textarea 
        placeholder="Focus me" 
        onFocus={handleFocus} 
        onBlur={handleBlur} 
      />
    );
    
    const textarea = screen.getByPlaceholderText('Focus me');
    
    fireEvent.focus(textarea);
    expect(handleFocus).toHaveBeenCalledTimes(1);
    
    fireEvent.blur(textarea);
    expect(handleBlur).toHaveBeenCalledTimes(1);
  });

  it('handles change events', () => {
    const handleChange = vi.fn();
    render(<Textarea placeholder="Type here" onChange={handleChange} />);
    
    const textarea = screen.getByPlaceholderText('Type here');
    fireEvent.change(textarea, { target: { value: 'Hello' } });
    
    expect(handleChange).toHaveBeenCalledTimes(1);
  });
});
