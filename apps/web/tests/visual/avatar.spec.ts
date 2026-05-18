import { test, expect } from '@playwright/test';

test.describe('Avatar visual tests', () => {
  test('renders all sizes and statuses', async ({ page }) => {
    await page.setContent(`
      <div id="root"></div>
      <script type="module">
        import React from 'react';
        import { createRoot } from 'react-dom/client';
        import { Avatar } from './components/ui/avatar.tsx';

        const App = () => (
          <div style={{ padding: '20px', background: 'var(--color-background)', display: 'flex', gap: '20px', alignItems: 'center', flexWrap: 'wrap' }}>
            <Avatar size="xs" initials="XS" />
            <Avatar size="sm" initials="SM" />
            <Avatar size="md" initials="MD" />
            <Avatar size="lg" initials="LG" />
            <Avatar size="xl" initials="XL" />
            
            <Avatar size="md" initials="ON" status="online" />
            <Avatar size="md" initials="AW" status="away" />
            <Avatar size="md" initials="BU" status="busy" />
            <Avatar size="md" initials="OF" status="offline" />
            
            <Avatar size="xl" src="https://github.com/shadcn.png" alt="shadcn" status="online" />
          </div>
        );

        const root = createRoot(document.getElementById('root'));
        root.render(<App />);
      </script>
    `);

    await page.waitForSelector('span');
    // Wait a bit for the image to load
    await page.waitForTimeout(500);
    await expect(page.locator('#root')).toHaveScreenshot('avatar-variants.png');
  });
});
