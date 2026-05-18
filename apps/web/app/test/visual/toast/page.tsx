'use client';
import { ToastProvider, useToast } from '@/components/ui/toast';

function Triggers() {
  const { addToast } = useToast();
  return (
    <div style={{ padding: '32px', display: 'flex', gap: '12px' }}>
      <button
        id="toast-info"
        onClick={() => addToast({ title: 'Info toast', description: 'An informational message.', variant: 'info', duration: 60000 })}
      >
        Info
      </button>
      <button
        id="toast-success"
        onClick={() => addToast({ title: 'Success toast', description: 'Operation completed.', variant: 'success', duration: 60000 })}
      >
        Success
      </button>
      <button
        id="toast-warn"
        onClick={() => addToast({ title: 'Warning toast', description: 'Proceed with caution.', variant: 'warn', duration: 60000 })}
      >
        Warn
      </button>
      <button
        id="toast-error"
        onClick={() => addToast({ title: 'Error toast', description: 'Something went wrong.', variant: 'error', duration: 60000 })}
      >
        Error
      </button>
    </div>
  );
}

export default function ToastVisualTest() {
  return (
    <ToastProvider>
      <Triggers />
    </ToastProvider>
  );
}
