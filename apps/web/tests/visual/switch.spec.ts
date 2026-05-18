import { test, expect } from '@playwright/test';

test.describe('Switch visual tests', () => {
  test('renders all sizes and states', async ({ page }) => {
    await page.setContent(`
      <div id="root"></div>
      <script type="module">
        import React from 'react';
        import { createRoot } from 'react-dom/client';
        import { Switch } from './components/ui/switch.tsx';

        const App = () => (
          <div style={{ padding: '20px', background: 'var(--color-background)', display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div style={{ display: 'flex', gap: '20px' }}>
              <Switch size="md" checked={false} />
              <Switch size="md" checked={true} />
              <Switch size="md" disabled checked={false} />
              <Switch size="md" disabled checked={true} />
            </div>
            <div style={{ display: 'flex', gap: '20px' }}>
              <Switch size="sm" checked={false} />
              <Switch size="sm" checked={true} />
              <Switch size="sm" disabled checked={false} />
              <Switch size="sm" disabled checked={true} />
            </div>
          </div>
        );

        const root = createRoot(document.getElementById('root'));
        root.render(<App />);
      </script>
    `);

    await page.waitForSelector('[role="switch"]');
    await expect(page.locator('#root')).toHaveScreenshot('switch-variants.png');
  });
});
