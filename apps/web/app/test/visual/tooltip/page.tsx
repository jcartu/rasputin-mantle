'use client';
import { Tooltip } from '@/components/ui/tooltip';

export default function TooltipVisualTest() {
  return (
    <div style={{ padding: '120px', display: 'flex', gap: '32px' }}>
      <Tooltip content="This is a tooltip" shortcuts={['Ctrl', 'K']}>
        <button id="tooltip-trigger" style={{ padding: '8px 16px' }}>Hover me</button>
      </Tooltip>
    </div>
  );
}
