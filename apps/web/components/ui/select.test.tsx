import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import Select from './select';

describe('Select', () => {
  const options = [
    { value: 'apple', label: 'Apple' },
    { value: 'banana', label: 'Banana' },
    { value: 'cherry', label: 'Cherry' },
  ];

  it('renders with placeholder', () => {
    render(<Select options={options} placeholder="Choose fruit" />);
    expect(screen.getByText('Choose fruit')).toBeInTheDocument();
  });

  it('opens dropdown on click', async () => {
    const user = userEvent.setup();
    render(<Select options={options} />);
    
    const combobox = screen.getByRole('combobox');
    await user.click(combobox);
    
    expect(screen.getByRole('listbox')).toBeInTheDocument();
    expect(screen.getByText('Apple')).toBeInTheDocument();
  });

  it('selects an option', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<Select options={options} onChange={onChange} />);
    
    await user.click(screen.getByRole('combobox'));
    await user.click(screen.getByText('Banana'));
    
    expect(onChange).toHaveBeenCalledWith('banana');
  });

  it('supports multiple selection', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<Select options={options} multiple value={['apple']} onChange={onChange} />);
    
    await user.click(screen.getByRole('combobox'));
    await user.click(screen.getByText('Banana'));
    
    expect(onChange).toHaveBeenCalledWith(['apple', 'banana']);
  });

  it('removes selected option in multiple mode', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<Select options={options} multiple value={['apple', 'banana']} onChange={onChange} />);
    
    const removeBtn = screen.getByLabelText('Remove Apple');
    await user.click(removeBtn);
    
    expect(onChange).toHaveBeenCalledWith(['banana']);
  });

  it('filters options when searchable', async () => {
    const user = userEvent.setup();
    render(<Select options={options} searchable />);
    
    await user.click(screen.getByRole('combobox'));
    const searchInput = screen.getByPlaceholderText('Search...');
    await user.type(searchInput, 'che');
    
    expect(screen.getByText('Cherry')).toBeInTheDocument();
    expect(screen.queryByText('Apple')).not.toBeInTheDocument();
  });

  it('handles keyboard navigation', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<Select options={options} onChange={onChange} />);
    
    const combobox = screen.getByRole('combobox');
    combobox.focus();
    
    await user.keyboard('{Enter}');
    expect(screen.getByRole('listbox')).toBeInTheDocument();
    
    await user.keyboard('{ArrowDown}');
    await user.keyboard('{ArrowDown}');
    await user.keyboard('{Enter}');
    
    expect(onChange).toHaveBeenCalledWith('banana');
  });

  it('renders disabled state', () => {
    render(<Select options={options} disabled />);
    const combobox = screen.getByRole('combobox');
    expect(combobox).toHaveStyle({ cursor: 'not-allowed' });
  });

  it('renders error state', () => {
    render(<Select options={options} error="Required field" />);
    expect(screen.getByText('Required field')).toBeInTheDocument();
  });
});
