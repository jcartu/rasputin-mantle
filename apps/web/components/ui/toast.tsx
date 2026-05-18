'use client';
import * as React from 'react';
import { createPortal } from 'react-dom';
import { Info, CheckCircle2, AlertTriangle, AlertCircle, X } from 'lucide-react';

export type ToastVariant = 'info' | 'success' | 'warn' | 'error';

export interface ToastData {
  id: string;
  variant?: ToastVariant;
  title: string;
  description?: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}

interface ToastContextValue {
  toasts: ToastData[];
  addToast: (toast: Omit<ToastData, 'id'>) => string;
  removeToast: (id: string) => void;
}

const ToastContext = React.createContext<ToastContextValue | null>(null);

export function useToast(): ToastContextValue {
  const ctx = React.useContext(ToastContext);
  if (!ctx) {
    throw new Error('useToast must be used within ToastProvider');
  }
  return ctx;
}

const variantConfig: Record<
  ToastVariant,
  { color: string; Icon: React.ComponentType<{ size?: number; color?: string }> }
> = {
  info: { color: 'var(--color-accent)', Icon: Info },
  success: { color: 'var(--color-success)', Icon: CheckCircle2 },
  warn: { color: 'var(--color-warning)', Icon: AlertTriangle },
  error: { color: 'var(--color-destructive)', Icon: AlertCircle },
};

interface ToastItemProps {
  toast: ToastData;
  onDismiss: (id: string) => void;
}

const ToastItem: React.FC<ToastItemProps> = ({ toast, onDismiss }) => {
  const variant: ToastVariant = toast.variant ?? 'info';
  const duration = toast.duration ?? 5000;
  const { color, Icon } = variantConfig[variant];

  const [isPaused, setIsPaused] = React.useState(false);
  const [isExiting, setIsExiting] = React.useState(false);
  const [progress, setProgress] = React.useState(100);
  const startTimeRef = React.useRef<number>(Date.now());
  const remainingRef = React.useRef<number>(duration);
  const rafRef = React.useRef<number | null>(null);

  const handleDismiss = React.useCallback(() => {
    setIsExiting(true);
    window.setTimeout(() => {
      onDismiss(toast.id);
    }, 200);
  }, [onDismiss, toast.id]);

  React.useEffect(() => {
    if (isPaused || isExiting) {
      if (rafRef.current !== null) {
        cancelAnimationFrame(rafRef.current);
        rafRef.current = null;
      }
      return;
    }

    startTimeRef.current = Date.now();
    const startRemaining = remainingRef.current;

    const tick = () => {
      const elapsed = Date.now() - startTimeRef.current;
      const newRemaining = Math.max(0, startRemaining - elapsed);
      remainingRef.current = newRemaining;
      const newProgress = (newRemaining / duration) * 100;
      setProgress(newProgress);

      if (newRemaining <= 0) {
        handleDismiss();
        return;
      }
      rafRef.current = requestAnimationFrame(tick);
    };

    rafRef.current = requestAnimationFrame(tick);

    return () => {
      if (rafRef.current !== null) {
        cancelAnimationFrame(rafRef.current);
        rafRef.current = null;
      }
    };
  }, [isPaused, isExiting, duration, handleDismiss]);

  return (
    <div
      role="status"
      aria-live="polite"
      data-variant={variant}
      data-exiting={isExiting ? 'true' : 'false'}
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
      style={{
        position: 'relative',
        width: '100%',
        maxWidth: '420px',
        backgroundColor: 'var(--color-background-elevated)',
        border: '1px solid var(--color-border)',
        borderLeft: `3px solid ${color}`,
        borderRadius: 'var(--radius-md)',
        boxShadow: 'var(--shadow-xl)',
        padding: '10px 12px',
        display: 'flex',
        alignItems: 'flex-start',
        gap: 'var(--spacing-2)',
        overflow: 'hidden',
        fontFamily: 'var(--font-sans)',
        animation: isExiting
          ? 'toast-out 200ms cubic-bezier(0.4, 0, 1, 1) forwards'
          : 'toast-in 300ms cubic-bezier(0.34, 1.56, 0.64, 1) forwards',
      }}
    >
      <style>{`
        @keyframes toast-in {
          from { opacity: 0; transform: translateY(100%); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes toast-out {
          from { opacity: 1; transform: translateY(0); }
          to { opacity: 0; transform: translateY(100%); }
        }
        @media (prefers-reduced-motion: reduce) {
          [data-toast-item] {
            animation: none !important;
          }
        }
      `}</style>
      <span style={{ display: 'flex', alignItems: 'center', flexShrink: 0, color }}>
        <Icon size={16} color={color} />
      </span>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div
          style={{
            fontSize: 'var(--text-sm)',
            fontWeight: 'var(--font-weight-semibold)',
            color: 'var(--color-foreground)',
            lineHeight: 1.4,
          }}
        >
          {toast.title}
        </div>
        {toast.description && (
          <div
            style={{
              fontSize: 'var(--text-sm)',
              fontWeight: 'var(--font-weight-regular)',
              color: 'var(--color-foreground-muted)',
              marginTop: '2px',
              lineHeight: 1.4,
            }}
          >
            {toast.description}
          </div>
        )}
      </div>
      {toast.action && (
        <button
          type="button"
          onClick={toast.action.onClick}
          style={{
            backgroundColor: 'transparent',
            border: 'none',
            color: 'var(--color-accent)',
            fontSize: 'var(--text-sm)',
            fontWeight: 'var(--font-weight-semibold)',
            cursor: 'pointer',
            padding: '4px 8px',
            borderRadius: 'var(--radius-sm)',
            fontFamily: 'var(--font-sans)',
            flexShrink: 0,
          }}
        >
          {toast.action.label}
        </button>
      )}
      <button
        type="button"
        aria-label="Dismiss"
        onClick={handleDismiss}
        style={{
          backgroundColor: 'transparent',
          border: 'none',
          color: 'var(--color-foreground-muted)',
          cursor: 'pointer',
          padding: '2px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
          borderRadius: 'var(--radius-sm)',
        }}
      >
        <X size={14} />
      </button>
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          height: '2px',
          width: `${progress}%`,
          backgroundColor: color,
          transition: isPaused ? 'none' : 'width 16ms linear',
        }}
      />
    </div>
  );
};

export interface ToastProviderProps {
  children: React.ReactNode;
}

export const ToastProvider: React.FC<ToastProviderProps> = ({ children }) => {
  const [toasts, setToasts] = React.useState<ToastData[]>([]);
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    setMounted(true);
  }, []);

  const addToast = React.useCallback((toast: Omit<ToastData, 'id'>): string => {
    const id = `toast-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
    setToasts((prev) => [...prev, { ...toast, id }]);
    return id;
  }, []);

  const removeToast = React.useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const value = React.useMemo(
    () => ({ toasts, addToast, removeToast }),
    [toasts, addToast, removeToast]
  );

  return (
    <ToastContext.Provider value={value}>
      {children}
      {mounted &&
        typeof document !== 'undefined' &&
        createPortal(
          <div
            data-testid="toast-region"
            aria-live="polite"
            aria-atomic="false"
            style={{
              position: 'fixed',
              bottom: '16px',
              right: '16px',
              display: 'flex',
              flexDirection: 'column',
              gap: '8px',
              zIndex: 100,
              pointerEvents: 'none',
            }}
          >
            {toasts.map((toast) => (
              <div key={toast.id} style={{ pointerEvents: 'auto' }}>
                <ToastItem toast={toast} onDismiss={removeToast} />
              </div>
            ))}
          </div>,
          document.body
        )}
    </ToastContext.Provider>
  );
};

export default ToastProvider;
