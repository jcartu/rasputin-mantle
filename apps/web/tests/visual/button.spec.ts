import { test, expect } from '@playwright/test';

test.describe('Button Visual Regression', () => {
  test('light mode', async ({ page }) => {
    await page.goto('/test-visual/button');
    // Force light mode if needed, assuming the app respects a class or media query.
    // We can inject a class to the html element.
    await page.evaluate(() => document.documentElement.classList.add('light'));
    await expect(page).toHaveScreenshot('button-light.png', { fullPage: true });
  });

  test('dark mode', async ({ page }) => {
    await page.goto('/test-visual/button');
    await page.evaluate(() => document.documentElement.classList.remove('light'));
    await expect(page).toHaveScreenshot('button-dark.png', { fullPage: true });
  });
});
