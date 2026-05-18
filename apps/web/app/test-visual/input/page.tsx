"use client";

import { Input } from '@/components/ui/input';

export default function InputVisualTest() {
  return (
    <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '20px', maxWidth: '400px' }}>
      <div id="default">
        <Input placeholder="Default input" />
      </div>
      
      <div id="with-label-hint">
        <Input label="Email" hint="We'll never share your email." placeholder="Enter email" />
      </div>
      
      <div id="error">
        <Input label="Username" error="Username is taken" defaultValue="johndoe" />
      </div>
      
      <div id="disabled">
        <Input label="Disabled" disabled placeholder="Cannot type here" />
      </div>
      
      <div id="icons">
        <Input leadingIcon={<span>@</span>} placeholder="Username" />
        <div style={{ height: '10px' }} />
        <Input trailingIcon={<span>✓</span>} placeholder="Success" />
      </div>
      
      <div id="sizes">
        <Input inputSize="sm" placeholder="Small input" />
        <div style={{ height: '10px' }} />
        <Input inputSize="md" placeholder="Medium input" />
        <div style={{ height: '10px' }} />
        <Input inputSize="lg" placeholder="Large input" />
      </div>
    </div>
  );
}
