import React, { useEffect, useRef, useState } from 'react';
import { X } from 'lucide-react';

export interface SheetProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
  side?: 'left' | 'right' | 'top' | 'bottom';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  closeOnOverlay?: boolean;
  className?: string;
}

export default function Sheet({
  isOpen,
  onClose,
  children,
  side = 'right',
  size = 'md',
  closeOnOverlay = true,
  className = '',
}: SheetProps) {
  const [isRendered, setIsRendered] = useState(isOpen);
  const [isVisible, setIsVisible] = useState(false);
  const sheetRef = useRef<HTMLDivElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);
  const touchStartRef = useRef<{ x: number; y: number } | null>(null);

  useEffect(() => {
    if (isOpen) {
      setIsRendered(true);
      previousFocusRef.current = document.activeElement as HTMLElement;
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
      }, 200);
      return () => clearTimeout(timer);
    }
  }, [isOpen]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;

      if (e.key === 'Escape') {
        onClose();
      }

      if (e.key === 'Tab' && sheetRef.current) {
        const focusableElements = sheetRef.current.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        if (focusableElements.length === 0) return;
        
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
    if (isVisible && sheetRef.current) {
      const closeBtn = sheetRef.current.querySelector('[aria-label="Close sheet"]') as HTMLElement;
      if (closeBtn) {
        closeBtn.focus();
      }
    }
  }, [isVisible]);

  const handleTouchStart = (e: React.TouchEvent) => {
    touchStartRef.current = {
      x: e.touches[0].clientX,
      y: e.touches[0].clientY,
    };
  };

  const handleTouchEnd = (e: React.TouchEvent) => {
    if (!touchStartRef.current) return;

    const touchEndX = e.changedTouches[0].clientX;
    const touchEndY = e.changedTouches[0].clientY;
    const deltaX = touchEndX - touchStartRef.current.x;
    const deltaY = touchEndY - touchStartRef.current.y;

    const threshold = 50;

    if (side === 'right' && deltaX > threshold) onClose();
    if (side === 'left' && deltaX < -threshold) onClose();
    if (side === 'bottom' && deltaY > threshold) onClose();
    if (side === 'top' && deltaY < -threshold) onClose();

    touchStartRef.current = null;
  };

  if (!isRendered) return null;

  const widths = {
    sm: '320px',
    md: '400px',
    lg: '480px',
    xl: '640px',
  };

  const getTransform = () => {
    if (isVisible) return 'translate3d(0, 0, 0)';
    switch (side) {
      case 'left': return 'translate3d(-100%, 0, 0)';
      case 'right': return 'translate3d(100%, 0, 0)';
      case 'top': return 'translate3d(0, -100%, 0)';
      case 'bottom': return 'translate3d(0, 100%, 0)';
    }
  };

  const getPositionStyles = (): React.CSSProperties => {
    const base: React.CSSProperties = {
      position: 'fixed',
      backgroundColor: 'var(--color-background-elevated)',
      boxShadow: 'var(--shadow-xl)',
      display: 'flex',
      flexDirection: 'column',
      padding: 'var(--spacing-6)',
      transition: `transform ${isVisible ? 'var(--duration-slow)' : 'var(--duration-default)'} ${isVisible ? 'var(--ease-enter)' : 'var(--ease-exit)'}`,
      transform: getTransform(),
    };

    switch (side) {
      case 'left':
        return {
          ...base,
          top: 0,
          bottom: 0,
          left: 0,
          width: '100%',
          maxWidth: widths[size],
          borderRight: '1px solid var(--color-border)',
        };
      case 'right':
        return {
          ...base,
          top: 0,
          bottom: 0,
          right: 0,
          width: '100%',
          maxWidth: widths[size],
          borderLeft: '1px solid var(--color-border)',
        };
      case 'top':
        return {
          ...base,
          top: 0,
          left: 0,
          right: 0,
          height: 'auto',
          maxHeight: '60vh',
          borderBottom: '1px solid var(--color-border)',
        };
      case 'bottom':
        return {
          ...base,
          bottom: 0,
          left: 0,
          right: 0,
          height: 'auto',
          maxHeight: '60vh',
          borderTop: '1px solid var(--color-border)',
        };
    }
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 100,
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

      {/* Sheet Container */}
      <div
        ref={sheetRef}
        className={className}
        style={getPositionStyles()}
        onTouchStart={handleTouchStart}
        onTouchEnd={handleTouchEnd}
      >
        <button
          onClick={onClose}
          aria-label="Close sheet"
          style={{
            position: 'absolute',
            top: 'var(--spacing-6)',
            right: 'var(--spacing-6)',
            background: 'transparent',
            border: 'none',
            padding: 'var(--spacing-1)',
            cursor: 'pointer',
            color: 'var(--color-foreground-muted)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            borderRadius: 'var(--radius-sm)',
            zIndex: 1,
          }}
          onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'var(--color-background-subtle)')}
          onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
        >
          <X size={20} />
        </button>

        <div
          style={{
            flex: 1,
            overflowY: 'auto',
            color: 'var(--color-foreground)',
            fontSize: 'var(--text-base)',
          }}
        >
          {children}
        </div>
      </div>
    </div>
  );
}
