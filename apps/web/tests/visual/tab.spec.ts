import { test, expect } from '@playwright/test';

test.describe('Tab visual tests', () => {
  test('renders horizontal tabs correctly', async ({ page }) => {
    await page.setContent(`
      <div id="root"></div>
      <script type="module">
        import React from 'react';
        import { createRoot } from 'react-dom/client';
        import { Tabs, TabList, TabTrigger, TabContent } from './components/ui/tab.tsx';

        const App = () => (
          <div style={{ padding: '20px', background: 'var(--color-background)' }}>
            <Tabs defaultValue="tab1">
              <TabList>
                <TabTrigger value="tab1">Tab 1</TabTrigger>
                <TabTrigger value="tab2">Tab 2</TabTrigger>
                <TabTrigger value="tab3" disabled>Tab 3</TabTrigger>
              </TabList>
              <TabContent value="tab1">Content 1</TabContent>
              <TabContent value="tab2">Content 2</TabContent>
            </Tabs>
          </div>
        );

        const root = createRoot(document.getElementById('root'));
        root.render(<App />);
      </script>
    `);

    // Wait for render
    await page.waitForSelector('[role="tablist"]');
    
    // Take screenshot
    await expect(page.locator('#root')).toHaveScreenshot('tab-horizontal.png');
  });

  test('renders vertical tabs correctly', async ({ page }) => {
    await page.setContent(`
      <div id="root"></div>
      <script type="module">
        import React from 'react';
        import { createRoot } from 'react-dom/client';
        import { Tabs, TabList, TabTrigger, TabContent } from './components/ui/tab.tsx';

        const App = () => (
          <div style={{ padding: '20px', background: 'var(--color-background)' }}>
            <Tabs defaultValue="tab1" orientation="vertical">
              <TabList>
                <TabTrigger value="tab1">Tab 1</TabTrigger>
                <TabTrigger value="tab2">Tab 2</TabTrigger>
              </TabList>
              <TabContent value="tab1">Content 1</TabContent>
              <TabContent value="tab2">Content 2</TabContent>
            </Tabs>
          </div>
        );

        const root = createRoot(document.getElementById('root'));
        root.render(<App />);
      </script>
    `);

    await page.waitForSelector('[role="tablist"]');
    await expect(page.locator('#root')).toHaveScreenshot('tab-vertical.png');
  });
});
