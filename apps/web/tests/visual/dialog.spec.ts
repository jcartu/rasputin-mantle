import { test, expect } from '@playwright/test';

test.describe('Dialog Visual Regression', () => {
  test('light mode', async ({ page }) => {
    await page.goto('/test-visual/dialog');
    await page.evaluate(() => document.documentElement.classList.add('light'));
    await page.evaluate(() => document.documentElement.classList.remove('dark'));
    // Wait for animation
    await page.waitForTimeout(500);
    await expect(page).toHaveScreenshot('dialog-light.png', { fullPage: true });
  });

  test('dark mode', async ({ page }) => {
    await page.goto('/test-visual/dialog');
    await page.evaluate(() => document.documentElement.classList.add('dark'));
    await page.evaluate(() => document.documentElement.classList.remove('light'));
    // Wait for animation
    await page.waitForTimeout(500);
    await expect(page).toHaveScreenshot('dialog-dark.png', { fullPage: true });
  });
});
