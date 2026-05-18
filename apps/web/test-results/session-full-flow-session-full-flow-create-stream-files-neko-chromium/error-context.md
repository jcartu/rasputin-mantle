# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: session-full-flow.spec.ts >> session full flow: create, stream, files, neko
- Location: tests/e2e/session-full-flow.spec.ts:3:5

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('[data-top-bar]')
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for locator('[data-top-bar]')

```

```yaml
- button "New Session"
- text: No sessions yet
- main: Select a session or create a new one
- status:
  - img
  - text: Static route
  - button "Hide static indicator":
    - img
- alert
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test('session full flow: create, stream, files, neko', async ({ page }) => {
  4  |   // 1. Navigate to app
  5  |   await page.goto('/');
  6  |   await page.waitForTimeout(500);
  7  | 
  8  |   // 2. Verify shell renders
  9  |   const topBar = page.locator('[data-top-bar]');
> 10 |   await expect(topBar).toBeVisible();
     |                        ^ Error: expect(locator).toBeVisible() failed
  11 | 
  12 |   // 3. Create a session (if button exists)
  13 |   const newSessionBtn = page.locator('button:has-text("New")');
  14 |   if (await newSessionBtn.isVisible().catch(() => false)) {
  15 |     await newSessionBtn.click();
  16 |     await page.waitForTimeout(1000);
  17 |   }
  18 | 
  19 |   // 4. Verify three-pane layout
  20 |   const chatPane = page.locator('[data-pane="chat"]');
  21 |   const computerPane = page.locator('[data-pane="computer"]');
  22 |   const filesPane = page.locator('[data-pane="files"]');
  23 | 
  24 |   await expect(chatPane).toBeVisible();
  25 |   await expect(computerPane).toBeVisible();
  26 |   await expect(filesPane).toBeVisible();
  27 | 
  28 |   // 5. Screenshot: initial state
  29 |   await page.screenshot({ path: 'test-results/p3-initial.png', fullPage: false });
  30 | 
  31 |   // 6. Verify chat pane has content area
  32 |   const chatContent = chatPane.locator('[data-chat-stream]');
  33 |   await expect(chatContent).toBeVisible();
  34 | 
  35 |   // 7. Screenshot: mid-state
  36 |   await page.screenshot({ path: 'test-results/p3-mid.png', fullPage: false });
  37 | 
  38 |   // 8. Verify computer view placeholder
  39 |   const computerView = computerPane.locator('[data-computer-view]');
  40 |   await expect(computerView).toBeVisible();
  41 | 
  42 |   // 9. Screenshot: computer view
  43 |   await page.screenshot({ path: 'test-results/p3-computer.png', fullPage: false });
  44 | 
  45 |   // 10. Verify files pane
  46 |   const fileTree = filesPane.locator('[data-file-tree]');
  47 |   await expect(fileTree).toBeVisible();
  48 | 
  49 |   // 11. Screenshot: completion
  50 |   await page.screenshot({ path: 'test-results/p3-complete.png', fullPage: false });
  51 | });
  52 | 
```