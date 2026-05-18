import { test, expect } from '@playwright/test';

test.describe('Sheet Visual Regression', () => {
  test('light mode', async ({ page }) => {
    await page.goto('/test-visual/sheet');
    await page.evaluate(() => document.documentElement.classList.add('light'));
    await page.evaluate(() => document.documentElement.classList.remove('dark'));
    // Wait for animation
    await page.waitForTimeout(500);
    await expect(page).toHaveScreenshot('sheet-light.png', { fullPage: true });
  });

  test('dark mode', async ({ page }) => {
    await page.goto('/test-visual/sheet');
    await page.evaluate(() => document.documentElement.classList.add('dark'));
    await page.evaluate(() => document.documentElement.classList.remove('light'));
    // Wait for animation
    await page.waitForTimeout(500);
    await expect(page).toHaveScreenshot('sheet-dark.png', { fullPage: true });
  });
});
