import { test, expect } from '@playwright/test';

test.describe('Home Page Redirects', () => {
  test('redirects to onboarding on first visit', async ({ page }) => {
    // Clear localStorage
    await page.addInitScript(() => {
      window.localStorage.clear();
    });

    await page.goto('/');
    
    // Should redirect to onboarding
    await expect(page).toHaveURL(/\/onboarding/);
  });

  test('stays on home page if already onboarded', async ({ page }) => {
    // Set localStorage
    await page.addInitScript(() => {
      window.localStorage.setItem('mantle:onboarding:complete', 'true');
    });

    // Mock API calls for home page
    await page.route('**/api/playbooks', async (route) => {
      await route.fulfill({ json: [] });
    });
    await page.route('**/api/sessions', async (route) => {
      await route.fulfill({ json: [] });
    });

    await page.goto('/');
    
    // Should stay on home page
    await expect(page).toHaveURL(/\/$/);
    await expect(page.getByText('Try this')).toBeVisible();
  });
});
