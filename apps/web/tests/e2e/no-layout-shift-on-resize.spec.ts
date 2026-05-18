import { test, expect } from '@playwright/test';

test('no layout shift on resize', async ({ page }) => {
  await page.setViewportSize({ width: 1920, height: 1080 });
  await page.goto('/');

  // Wait for initial render
  await page.waitForTimeout(500);

  // Get initial positions
  const topBar = page.locator('[data-top-bar]');
  const bottomBar = page.locator('[data-bottom-bar]');

  const topRect1 = await topBar.boundingBox();
  const bottomRect1 = await bottomBar.boundingBox();

  // Resize
  await page.setViewportSize({ width: 1366, height: 768 });
  await page.waitForTimeout(300);

  const topRect2 = await topBar.boundingBox();
  const bottomRect2 = await bottomBar.boundingBox();

  // Bars should maintain their positions
  // Bars should maintain their positions (x/y are stable)
  expect(topRect2?.x).toBe(topRect1?.x);
  expect(topRect2?.y).toBe(topRect1?.y);
  expect(topRect2?.height).toBe(topRect1?.height);
});
