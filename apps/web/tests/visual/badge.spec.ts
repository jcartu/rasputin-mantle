import { test, expect } from '@playwright/test';

test.describe('Badge visual tests', () => {
  test('renders all variants and sizes', async ({ page }) => {
    await page.setContent(`
      <div id="root"></div>
      <script type="module">
        import React from 'react';
        import { createRoot } from 'react-dom/client';
        import { Badge } from './components/ui/badge.tsx';

        const App = () => (
          <div style={{ padding: '20px', background: 'var(--color-background)', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
            <Badge variant="default" size="md">Default MD</Badge>
            <Badge variant="success" size="md">Success MD</Badge>
            <Badge variant="warn" size="md">Warn MD</Badge>
            <Badge variant="error" size="md">Error MD</Badge>
            <Badge variant="outline" size="md">Outline MD</Badge>
            
            <Badge variant="default" size="sm">Default SM</Badge>
            <Badge variant="success" size="sm">Success SM</Badge>
            <Badge variant="warn" size="sm">Warn SM</Badge>
            <Badge variant="error" size="sm">Error SM</Badge>
            <Badge variant="outline" size="sm">Outline SM</Badge>
          </div>
        );

        const root = createRoot(document.getElementById('root'));
        root.render(<App />);
      </script>
    `);

    await page.waitForSelector('span');
    await expect(page.locator('#root')).toHaveScreenshot('badge-variants.png');
  });
});
