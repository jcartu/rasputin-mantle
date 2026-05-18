import { test, expect } from '@playwright/test';

test.describe('Textarea Visual Regression', () => {
  test('light mode', async ({ page }) => {
    await page.goto('/test-visual/textarea');
    await page.evaluate(() => document.documentElement.classList.add('light'));
    await expect(page).toHaveScreenshot('textarea-light.png', { fullPage: true });
  });

  test('dark mode', async ({ page }) => {
    await page.goto('/test-visual/textarea');
    await page.evaluate(() => document.documentElement.classList.remove('light'));
    await expect(page).toHaveScreenshot('textarea-dark.png', { fullPage: true });
  });
});
