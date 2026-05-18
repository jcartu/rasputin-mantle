import { test, expect } from '@playwright/test';

test.describe('Card visual tests', () => {
  test('renders card with all slots', async ({ page }) => {
    await page.setContent(`
      <div id="root"></div>
      <script type="module">
        import React from 'react';
        import { createRoot } from 'react-dom/client';
        import { Card, CardHeader, CardBody, CardFooter } from './components/ui/card.tsx';

        const App = () => (
          <div style={{ padding: '20px', background: 'var(--color-background)' }}>
            <Card style={{ maxWidth: '400px' }}>
              <CardHeader withBorder>
                <h3 style={{ margin: 0, fontSize: 'var(--text-lg)', fontWeight: 'var(--font-weight-semibold)' }}>Card Title</h3>
              </CardHeader>
              <CardBody>
                <p style={{ margin: 0, color: 'var(--color-foreground-muted)' }}>This is the card body content. It has some text to show how it looks.</p>
              </CardBody>
              <CardFooter withBorder>
                <button style={{ padding: '8px 16px', background: 'var(--color-accent)', color: 'white', border: 'none', borderRadius: 'var(--radius-md)' }}>Action</button>
              </CardFooter>
            </Card>
          </div>
        );

        const root = createRoot(document.getElementById('root'));
        root.render(<App />);
      </script>
    `);

    await page.waitForSelector('h3');
    await expect(page.locator('#root')).toHaveScreenshot('card-full.png');
  });
});
