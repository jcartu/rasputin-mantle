import { test, expect } from '@playwright/test';

test.describe('Toast Visual Regression', () => {
  test('renders all variants correctly', async ({ page }) => {
    await page.goto('/test/visual/toast');

    // Trigger all four toasts
    await page.click('#toast-info');
    await page.click('#toast-success');
    await page.click('#toast-warn');
    await page.click('#toast-error');

    // Wait for animations to settle
    await page.waitForTimeout(400);

    const region = page.locator('[data-testid="toast-region"]');
    await expect(region).toBeVisible();

    await expect(page).toHaveScreenshot('toast-variants.png', {
      animations: 'disabled',
    });
  });
});
