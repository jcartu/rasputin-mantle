import { test, expect } from '@playwright/test';

test('session full flow: create, stream, files, neko', async ({ page }) => {
  // 1. Navigate to app
  await page.goto('/');
  await page.waitForTimeout(500);

  // 2. Verify shell renders
  const topBar = page.locator('[data-top-bar]');
  await expect(topBar).toBeVisible();

  // 3. Create a session (if button exists)
  const newSessionBtn = page.locator('button:has-text("New")');
  if (await newSessionBtn.isVisible().catch(() => false)) {
    await newSessionBtn.click();
    await page.waitForTimeout(1000);
  }

  // 4. Verify three-pane layout
  const chatPane = page.locator('[data-pane="chat"]');
  const computerPane = page.locator('[data-pane="computer"]');
  const filesPane = page.locator('[data-pane="files"]');

  await expect(chatPane).toBeVisible();
  await expect(computerPane).toBeVisible();
  await expect(filesPane).toBeVisible();

  // 5. Screenshot: initial state
  await page.screenshot({ path: 'test-results/p3-initial.png', fullPage: false });

  // 6. Verify chat pane has content area
  const chatContent = chatPane.locator('[data-chat-stream]');
  await expect(chatContent).toBeVisible();

  // 7. Screenshot: mid-state
  await page.screenshot({ path: 'test-results/p3-mid.png', fullPage: false });

  // 8. Verify computer view placeholder
  const computerView = computerPane.locator('[data-computer-view]');
  await expect(computerView).toBeVisible();

  // 9. Screenshot: computer view
  await page.screenshot({ path: 'test-results/p3-computer.png', fullPage: false });

  // 10. Verify files pane
  const fileTree = filesPane.locator('[data-file-tree]');
  await expect(fileTree).toBeVisible();

  // 11. Screenshot: completion
  await page.screenshot({ path: 'test-results/p3-complete.png', fullPage: false });
});
