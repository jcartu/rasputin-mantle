import React, { useEffect, useRef, useState } from 'react';
import { X } from 'lucide-react';

export interface DialogProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'full';
  closeOnOverlay?: boolean;
  className?: string;
}

export default function Dialog({
  isOpen,
  onClose,
  title,
  children,
  footer,
  size = 'md',
  closeOnOverlay = true,
  className = '',
}: DialogProps) {
  const [isRendered, setIsRendered] = useState(isOpen);
  const [isVisible, setIsVisible] = useState(false);
  const dialogRef = useRef<HTMLDivElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (isOpen) {
      setIsRendered(true);
      previousFocusRef.current = document.activeElement as HTMLElement;
      // Small delay to allow render before animation
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          setIsVisible(true);
        });
      });
    } else {
      setIsVisible(false);
      const timer = setTimeout(() => {
        setIsRendered(false);
        if (previousFocusRef.current) {
          previousFocusRef.current.focus();
        }
      }, 200); // Match exit duration
      return () => clearTimeout(timer);
    }
  }, [isOpen]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;

      if (e.key === 'Escape') {
        onClose();
      }

      // Focus trap
      if (e.key === 'Tab' && dialogRef.current) {
        const focusableElements = dialogRef.current.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        const firstElement = focusableElements[0] as HTMLElement;
        const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

        if (e.shiftKey) {
          if (document.activeElement === firstElement) {
            lastElement.focus();
            e.preventDefault();
          }
        } else {
          if (document.activeElement === lastElement) {
            firstElement.focus();
            e.preventDefault();
          }
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  useEffect(() => {
    if (isVisible && dialogRef.current) {
      const closeBtn = dialogRef.current.querySelector('[aria-label="Close dialog"]') as HTMLElement;
      if (closeBtn) {
        closeBtn.focus();
      }
    }
  }, [isVisible]);

  if (!isRendered) return null;

  const maxWidths = {
    sm: '400px',
    md: '520px',
    lg: '680px',
    full: 'min(90vw, 960px)',
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="dialog-title"
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 100,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontFamily: 'var(--font-sans)',
      }}
    >
      {/* Backdrop */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          opacity: isVisible ? 1 : 0,
          transition: 'opacity var(--duration-default) var(--ease-default)',
        }}
        onClick={() => closeOnOverlay && onClose()}
        aria-hidden="true"
      />

      {/* Dialog Container */}
      <div
        ref={dialogRef}
        className={className}
        style={{
          position: 'relative',
          backgroundColor: 'var(--color-background-elevated)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-lg)',
          boxShadow: 'var(--shadow-lg)',
          width: '100%',
          maxWidth: maxWidths[size],
          maxHeight: '90vh',
          display: 'flex',
          flexDirection: 'column',
          opacity: isVisible ? 1 : 0,
          transform: isVisible ? 'scale(1) translateY(0)' : 'scale(0.95) translateY(20px)',
          transition: `
            opacity ${isVisible ? 'var(--duration-slow)' : 'var(--duration-default)'} ${isVisible ? 'var(--ease-enter)' : 'var(--ease-exit)'},
            transform ${isVisible ? 'var(--duration-slow)' : 'var(--duration-default)'} ${isVisible ? 'var(--ease-enter)' : 'var(--ease-exit)'}
          `,
        }}
      >
        {/* Header */}
        <div
          style={{
            padding: 'var(--spacing-6) var(--spacing-8) 0',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <h2
            id="dialog-title"
            style={{
              margin: 0,
              fontSize: 'var(--text-2xl)',
              fontWeight: 'var(--font-weight-semibold)',
              color: 'var(--color-foreground)',
            }}
          >
            {title}
          </h2>
          <button
            onClick={onClose}
            aria-label="Close dialog"
            style={{
              background: 'transparent',
              border: 'none',
              padding: 'var(--spacing-1)',
              cursor: 'pointer',
              color: 'var(--color-foreground-muted)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              borderRadius: 'var(--radius-sm)',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'var(--color-background-subtle)')}
            onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
          >
            <X size={20} />
          </button>
        </div>

        {/* Body */}
        <div
          style={{
            padding: 'var(--spacing-4) var(--spacing-8)',
            overflowY: 'auto',
            fontSize: 'var(--text-base)',
            fontWeight: 'var(--font-weight-regular)',
            color: 'var(--color-foreground)',
            flex: 1,
          }}
        >
          {children}
        </div>

        {/* Footer */}
        {footer && (
          <div
            style={{
              padding: '0 var(--spacing-8) var(--spacing-6)',
              display: 'flex',
              justifyContent: 'flex-end',
              gap: 'var(--spacing-4)',
              marginTop: 'var(--spacing-4)',
            }}
          >
            {footer}
          </div>
        )}
      </div>
    </div>
  );
}
