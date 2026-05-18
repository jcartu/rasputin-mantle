import { test, expect } from '@playwright/test';

test('mobile tab bar appears at ≤768px', async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 667 });
  await page.goto('/');
  const mobileTabs = page.locator('[data-mobile-tabs]');
  await expect(mobileTabs).toBeVisible();
});

test('desktop shell appears at >768px', async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 900 });
  await page.goto('/');
  const mobileTabs = page.locator('[data-mobile-tabs]');
  await expect(mobileTabs).not.toBeVisible();
});
