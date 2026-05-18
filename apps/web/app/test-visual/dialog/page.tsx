'use client';

import React, { useState } from 'react';
import Dialog from '@/components/ui/dialog';

export default function DialogTestPage() {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div className="p-8" style={{ padding: '32px' }}>
      <button onClick={() => setIsOpen(true)}>Open Dialog</button>
      
      <Dialog
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        title="Edit Profile"
        size="md"
        footer={
          <>
            <button style={{ padding: '8px 16px', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', background: 'transparent', color: 'var(--color-foreground)' }}>Cancel</button>
            <button style={{ padding: '8px 16px', border: 'none', borderRadius: 'var(--radius-md)', background: 'var(--color-accent)', color: '#fff' }}>Save Changes</button>
          </>
        }
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <p>Make changes to your profile here. Click save when you're done.</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label style={{ fontSize: 'var(--text-sm)', color: 'var(--color-foreground-muted)' }}>Name</label>
            <input type="text" defaultValue="Pedro Duarte" style={{ padding: '8px', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)', background: 'var(--color-background)', color: 'var(--color-foreground)' }} />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label style={{ fontSize: 'var(--text-sm)', color: 'var(--color-foreground-muted)' }}>Username</label>
            <input type="text" defaultValue="@peduarte" style={{ padding: '8px', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)', background: 'var(--color-background)', color: 'var(--color-foreground)' }} />
          </div>
        </div>
      </Dialog>
    </div>
  );
}
