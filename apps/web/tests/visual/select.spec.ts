import { test, expect } from '@playwright/test';

test.describe('Select Visual Regression', () => {
  test('light mode', async ({ page }) => {
    await page.goto('/test-visual/select');
    await page.evaluate(() => document.documentElement.classList.add('light'));
    await page.evaluate(() => document.documentElement.classList.remove('dark'));
    await expect(page).toHaveScreenshot('select-light.png', { fullPage: true });
  });

  test('dark mode', async ({ page }) => {
    await page.goto('/test-visual/select');
    await page.evaluate(() => document.documentElement.classList.add('dark'));
    await page.evaluate(() => document.documentElement.classList.remove('light'));
    await expect(page).toHaveScreenshot('select-dark.png', { fullPage: true });
  });

  test('dropdown open', async ({ page }) => {
    await page.goto('/test-visual/select');
    await page.click('#select-default [role="combobox"]');
    await expect(page).toHaveScreenshot('select-dropdown-open.png');
  });
});
