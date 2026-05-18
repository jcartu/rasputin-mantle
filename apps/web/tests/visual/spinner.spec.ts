import { test, expect } from '@playwright/test';

test.describe('Spinner Visual Regression', () => {
  test('renders all variants correctly', async ({ page }) => {
    await page.goto('/test/visual/spinner');
    
    await expect(page.locator('#spinner-indeterminate')).toBeVisible();
    
    await expect(page).toHaveScreenshot('spinner-variants.png', {
      animations: 'disabled',
    });
  });
});
