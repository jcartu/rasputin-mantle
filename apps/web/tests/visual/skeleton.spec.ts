import { test, expect } from '@playwright/test';

test.describe('Skeleton Visual Regression', () => {
  test('renders all variants correctly', async ({ page }) => {
    await page.goto('/test/visual/skeleton');
    
    // Wait for elements to be visible
    await expect(page.locator('#skeleton-block')).toBeVisible();
    
    // Take screenshot of the whole page
    await expect(page).toHaveScreenshot('skeleton-variants.png', {
      animations: 'disabled', // Disable animations for stable screenshots
    });
  });
});
