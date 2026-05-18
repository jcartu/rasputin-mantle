"use client";

import React, { useState, useRef, useEffect, KeyboardEvent } from 'react';
import { ChevronDown, Check, X, Search } from 'lucide-react';

export interface SelectOption {
  value: string;
  label: string;
}

export interface SelectProps {
  options: SelectOption[];
  value?: string | string[];
  onChange?: (value: string | string[]) => void;
  placeholder?: string;
  multiple?: boolean;
  searchable?: boolean;
  disabled?: boolean;
  error?: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  'aria-label'?: string;
}

export default function Select({
  options,
  value,
  onChange,
  placeholder = 'Select...',
  multiple = false,
  searchable = false,
  disabled = false,
  error,
  size = 'md',
  className = '',
  'aria-label': ariaLabel,
}: SelectProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [focusedIndex, setFocusedIndex] = useState(-1);
  const containerRef = useRef<HTMLDivElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);
  const listboxRef = useRef<HTMLUListElement>(null);

  const isSelected = (val: string) => {
    if (multiple) {
      return Array.isArray(value) && value.includes(val);
    }
    return value === val;
  };

  const handleSelect = (val: string) => {
    if (multiple) {
      const currentValues = Array.isArray(value) ? value : [];
      const newValues = currentValues.includes(val)
        ? currentValues.filter((v) => v !== val)
        : [...currentValues, val];
      onChange?.(newValues);
    } else {
      onChange?.(val);
      setIsOpen(false);
    }
  };

  const handleRemove = (e: React.MouseEvent, val: string) => {
    e.stopPropagation();
    if (multiple && Array.isArray(value)) {
      onChange?.(value.filter((v) => v !== val));
    }
  };

  const filteredOptions = options.filter((opt) =>
    opt.label.toLowerCase().includes(searchQuery.toLowerCase())
  );

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    if (isOpen) {
      setSearchQuery('');
      setFocusedIndex(-1);
      if (searchable && searchInputRef.current) {
        searchInputRef.current.focus();
      } else if (listboxRef.current) {
        listboxRef.current.focus();
      }
    }
  }, [isOpen, searchable]);

  const handleKeyDown = (e: KeyboardEvent) => {
    if (disabled) return;

    if (!isOpen) {
      if (e.key === 'Enter' || e.key === ' ' || e.key === 'ArrowDown') {
        e.preventDefault();
        setIsOpen(true);
      }
      return;
    }

    switch (e.key) {
      case 'Escape':
        setIsOpen(false);
        break;
      case 'ArrowDown':
        e.preventDefault();
        setFocusedIndex((prev) => (prev < filteredOptions.length - 1 ? prev + 1 : prev));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setFocusedIndex((prev) => (prev > 0 ? prev - 1 : prev));
        break;
      case 'Enter':
        e.preventDefault();
        if (focusedIndex >= 0 && focusedIndex < filteredOptions.length) {
          handleSelect(filteredOptions[focusedIndex].value);
        }
        break;
    }
  };

  useEffect(() => {
    if (focusedIndex >= 0 && listboxRef.current) {
      const optionEl = listboxRef.current.children[focusedIndex] as HTMLElement;
      if (optionEl && typeof optionEl.scrollIntoView === 'function') {
        optionEl.scrollIntoView({ block: 'nearest' });
      }
    }
  }, [focusedIndex]);

  const selectedOptions = multiple
    ? options.filter((opt) => Array.isArray(value) && value.includes(opt.value))
    : options.filter((opt) => opt.value === value);

  return (
    <div
      ref={containerRef}
      className={`rm-select-container ${className}`}
      style={{
        position: 'relative',
        width: '100%',
        fontFamily: 'var(--font-sans)',
        fontSize: 'var(--text-sm)',
      }}
    >
      <div
        role="combobox"
        aria-expanded={isOpen}
        aria-haspopup="listbox"
        aria-controls="rm-select-listbox"
        aria-label={ariaLabel}
        tabIndex={disabled ? -1 : 0}
        onClick={() => !disabled && setIsOpen(!isOpen)}
        onKeyDown={handleKeyDown}
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          minHeight: size === 'sm' ? '28px' : size === 'lg' ? '40px' : '32px',
          padding: '0 var(--spacing-2)',
          borderRadius: 'var(--radius-md)',
          border: `1px solid ${error ? 'var(--color-destructive)' : isOpen ? 'var(--color-accent)' : 'var(--color-border)'}`,
          backgroundColor: disabled ? 'var(--color-muted)' : 'var(--color-background)',
          color: disabled ? 'var(--color-foreground-faint)' : 'var(--color-foreground)',
          cursor: disabled ? 'not-allowed' : 'pointer',
          outline: 'none',
          boxShadow: isOpen && !error ? '0 0 0 1px var(--color-accent)' : 'none',
          transition: 'border-color var(--duration-fast) var(--ease-default), box-shadow var(--duration-fast) var(--ease-default)',
        }}
      >
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--spacing-1)', flex: 1, overflow: 'hidden' }}>
          {multiple && selectedOptions.length > 0 ? (
            selectedOptions.map((opt) => (
              <span
                key={opt.value}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 'var(--spacing-1)',
                  backgroundColor: 'var(--color-accent-subtle)',
                  color: 'var(--color-accent)',
                  padding: '2px 6px',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: 'var(--text-xs)',
                  lineHeight: 1,
                }}
              >
                {opt.label}
                <button
                  type="button"
                  onClick={(e) => handleRemove(e, opt.value)}
                  style={{
                    background: 'none',
                    border: 'none',
                    padding: 0,
                    color: 'inherit',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                  }}
                  aria-label={`Remove ${opt.label}`}
                >
                  <X size={12} />
                </button>
              </span>
            ))
          ) : !multiple && selectedOptions.length > 0 ? (
            <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
              {selectedOptions[0].label}
            </span>
          ) : (
            <span style={{ color: 'var(--color-foreground-faint)' }}>{placeholder}</span>
          )}
        </div>
        <ChevronDown size={16} style={{ color: 'var(--color-foreground-muted)', flexShrink: 0, marginLeft: 'var(--spacing-2)' }} />
      </div>

      {error && (
        <div style={{ color: 'var(--color-destructive)', fontSize: 'var(--text-xs)', marginTop: 'var(--spacing-1)' }}>
          {error}
        </div>
      )}

      {isOpen && (
        <div
          style={{
            position: 'absolute',
            top: 'calc(100% + 4px)',
            left: 0,
            right: 0,
            backgroundColor: 'var(--color-background-elevated)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-md)',
            boxShadow: 'var(--shadow-md)',
            zIndex: 50,
            overflow: 'hidden',
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          {searchable && (
            <div style={{ padding: 'var(--spacing-2)', borderBottom: '1px solid var(--color-border)', display: 'flex', alignItems: 'center', gap: 'var(--spacing-2)' }}>
              <Search size={14} style={{ color: 'var(--color-foreground-muted)' }} />
              <input
                ref={searchInputRef}
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Search..."
                style={{
                  border: 'none',
                  background: 'none',
                  outline: 'none',
                  width: '100%',
                  color: 'var(--color-foreground)',
                  fontSize: 'var(--text-sm)',
                }}
              />
            </div>
          )}
          <ul
            ref={listboxRef}
            id="rm-select-listbox"
            role="listbox"
            aria-multiselectable={multiple}
            tabIndex={-1}
            onKeyDown={handleKeyDown}
            style={{
              maxHeight: '240px',
              overflowY: 'auto',
              margin: 0,
              padding: 'var(--spacing-1)',
              listStyle: 'none',
              outline: 'none',
            }}
          >
            {filteredOptions.length === 0 ? (
              <li style={{ padding: 'var(--spacing-2)', color: 'var(--color-foreground-faint)', textAlign: 'center' }}>
                No results found
              </li>
            ) : (
              filteredOptions.map((opt, index) => {
                const selected = isSelected(opt.value);
                const focused = index === focusedIndex;
                return (
                  <li
                    key={opt.value}
                    role="option"
                    aria-selected={selected}
                    onClick={() => handleSelect(opt.value)}
                    onMouseEnter={() => setFocusedIndex(index)}
                    style={{
                      height: '32px',
                      padding: '0 var(--spacing-2)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      cursor: 'pointer',
                      borderRadius: 'var(--radius-sm)',
                      backgroundColor: selected
                        ? 'var(--color-accent-subtle)'
                        : focused
                        ? 'var(--color-background-subtle)'
                        : 'transparent',
                      color: selected ? 'var(--color-accent)' : 'var(--color-foreground)',
                    }}
                  >
                    <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {opt.label}
                    </span>
                    {selected && <Check size={16} />}
                  </li>
                );
              })
            )}
          </ul>
        </div>
      )}
    </div>
  );
}
