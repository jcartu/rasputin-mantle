import { test, expect } from '@playwright/test';

test('⌘K opens command palette', async ({ page }) => {
  await page.goto('/');
  await page.press('body', 'Control+k');
  const palette = page.locator('[data-command-palette]');
  await expect(palette).toBeVisible();
});

test('⌘\\ toggles chat pane', async ({ page }) => {
  await page.goto('/');
  const chatPane = page.locator('[data-pane="chat"]');
  await expect(chatPane).toBeVisible();
});

test('⌘B toggles files pane', async ({ page }) => {
  await page.goto('/');
  const filesPane = page.locator('[data-pane="files"]');
  await expect(filesPane).toBeVisible();
});
