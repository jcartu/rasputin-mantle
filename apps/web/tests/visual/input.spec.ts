import { test, expect } from '@playwright/test';

test.describe('Input Visual Regression', () => {
  test('light mode', async ({ page }) => {
    await page.goto('/test-visual/input');
    await page.evaluate(() => document.documentElement.classList.add('light'));
    await expect(page).toHaveScreenshot('input-light.png', { fullPage: true });
  });

  test('dark mode', async ({ page }) => {
    await page.goto('/test-visual/input');
    await page.evaluate(() => document.documentElement.classList.remove('light'));
    await expect(page).toHaveScreenshot('input-dark.png', { fullPage: true });
  });
});
