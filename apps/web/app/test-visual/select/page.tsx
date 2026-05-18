'use client';

import React, { useState } from 'react';
import Select from '@/components/ui/select';

export default function SelectTestPage() {
  const options = [
    { value: '1', label: 'Option 1' },
    { value: '2', label: 'Option 2' },
    { value: '3', label: 'Option 3' },
    { value: '4', label: 'Option 4' },
    { value: '5', label: 'Option 5' },
    { value: '6', label: 'Option 6' },
    { value: '7', label: 'Option 7' },
  ];

  const [val1, setVal1] = useState<string>();
  const [val2, setVal2] = useState<string[]>(['1', '2']);

  return (
    <div className="p-8 space-y-8 max-w-md" style={{ padding: '32px', display: 'flex', flexDirection: 'column', gap: '32px', maxWidth: '400px' }}>
      <div id="select-default">
        <label>Default</label>
        <Select options={options} value={val1} onChange={(v) => setVal1(typeof v === 'string' ? v : v[0])} />
      </div>
      
      <div id="select-multiple">
        <label>Multiple</label>
        <Select options={options} multiple value={val2} onChange={(v) => setVal2(Array.isArray(v) ? v : [v])} />
      </div>

      <div id="select-searchable">
        <label>Searchable</label>
        <Select options={options} searchable />
      </div>

      <div id="select-disabled">
        <label>Disabled</label>
        <Select options={options} disabled />
      </div>

      <div id="select-error">
        <label>Error</label>
        <Select options={options} error="This field is required" />
      </div>
    </div>
  );
}
