'use client';

import React, { useState } from 'react';
import Sheet from '@/components/ui/sheet';

export default function SheetTestPage() {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div className="p-8" style={{ padding: '32px' }}>
      <button onClick={() => setIsOpen(true)}>Open Sheet</button>
      
      <Sheet
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        side="right"
        size="md"
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <h2 style={{ margin: 0, fontSize: 'var(--text-2xl)', fontWeight: 'var(--font-weight-semibold)' }}>
            Settings
          </h2>
          <p style={{ color: 'var(--color-foreground-muted)' }}>
            Manage your account settings and preferences.
          </p>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <label style={{ fontSize: 'var(--text-sm)', fontWeight: 'var(--font-weight-medium)' }}>Email Notifications</label>
              <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-foreground-muted)' }}>Receive emails about your account activity.</p>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <label style={{ fontSize: 'var(--text-sm)', fontWeight: 'var(--font-weight-medium)' }}>Marketing Emails</label>
              <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-foreground-muted)' }}>Receive emails about new products, features, and more.</p>
            </div>
          </div>
        </div>
      </Sheet>
    </div>
  );
}
