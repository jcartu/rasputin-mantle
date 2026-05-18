import { test, expect } from '@playwright/test';

test.describe('Tooltip Visual Regression', () => {
  test('renders tooltip correctly on hover', async ({ page }) => {
    await page.goto('/test/visual/tooltip');
    
    const trigger = page.locator('#tooltip-trigger');
    await trigger.hover();
    
    // Wait for delay
    await page.waitForTimeout(300);
    
    const tooltip = page.locator('[role="tooltip"]');
    await expect(tooltip).toBeVisible();
    
    await expect(page).toHaveScreenshot('tooltip-visible.png', {
      animations: 'disabled',
    });
  });
});
