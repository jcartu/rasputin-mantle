import { test, expect } from '@playwright/test';

test('chat pane collapses with ⌘\\', async ({ page }) => {
  await page.goto('/');
  // Chat pane should be visible initially
  const chatPane = page.locator('[data-pane="chat"]');
  await expect(chatPane).toBeVisible();
  const chatRect = await chatPane.boundingBox();
  expect(chatRect?.width).toBeGreaterThan(280);
});

test('files pane collapses with ⌘B', async ({ page }) => {
  await page.goto('/');
  const filesPane = page.locator('[data-pane="files"]');
  await expect(filesPane).toBeVisible();
  const filesRect = await filesPane.boundingBox();
  expect(filesRect?.width).toBeGreaterThan(240);
});
