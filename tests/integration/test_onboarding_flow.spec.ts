import { test, expect } from '@playwright/test';

test.describe('Onboarding Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Clear localStorage before each test
    await page.addInitScript(() => {
      window.localStorage.clear();
    });
  });

  test('completes full onboarding flow', async ({ page }) => {
    await page.goto('/onboarding');

    // Step 1: Select Intent
    await expect(page.getByText('What do you want to do today?')).toBeVisible();
    await page.getByText('Research').click();

    // Step 2: Select Template
    await expect(page.getByText('Pick a starting template')).toBeVisible();
    await page.getByText('Competitor Analysis').click();

    // Step 3: Run Task
    await expect(page.getByText('First task')).toBeVisible();
    const textarea = page.getByRole('textbox');
    await expect(textarea).toHaveValue(/Analyze the competitor/);
    
    // Mock API calls
    await page.route('**/api/sessions', async (route) => {
      await route.fulfill({ json: { session_id: 'test-session-123' } });
    });
    await page.route('**/api/sessions/*/exec', async (route) => {
      await route.fulfill({ json: { status: 'ok' } });
    });

    await page.getByRole('button', { name: /Run Task/i }).click();

    // Should redirect to session page
    await expect(page).toHaveURL(/\/session\/test-session-123/);
    
    // Should have set localStorage
    const hasOnboarded = await page.evaluate(() => localStorage.getItem('mantle:onboarding:complete'));
    expect(hasOnboarded).toBe('true');
  });

  test('skip link works', async ({ page }) => {
    await page.goto('/onboarding');
    
    await page.getByText(/I know what I'm doing/i).click();
    
    await expect(page).toHaveURL(/\//);
    
    const hasOnboarded = await page.evaluate(() => localStorage.getItem('mantle:onboarding:complete'));
    expect(hasOnboarded).toBe('true');
  });
});
