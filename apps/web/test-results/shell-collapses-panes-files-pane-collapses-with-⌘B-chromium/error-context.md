# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: shell-collapses-panes.spec.ts >> files pane collapses with ⌘B
- Location: tests/e2e/shell-collapses-panes.spec.ts:12:5

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('[data-pane="files"]')
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for locator('[data-pane="files"]')

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
  3  | test('chat pane collapses with ⌘\\', async ({ page }) => {
  4  |   await page.goto('/');
  5  |   // Chat pane should be visible initially
  6  |   const chatPane = page.locator('[data-pane="chat"]');
  7  |   await expect(chatPane).toBeVisible();
  8  |   const chatRect = await chatPane.boundingBox();
  9  |   expect(chatRect?.width).toBeGreaterThan(280);
  10 | });
  11 | 
  12 | test('files pane collapses with ⌘B', async ({ page }) => {
  13 |   await page.goto('/');
  14 |   const filesPane = page.locator('[data-pane="files"]');
> 15 |   await expect(filesPane).toBeVisible();
     |                           ^ Error: expect(locator).toBeVisible() failed
  16 |   const filesRect = await filesPane.boundingBox();
  17 |   expect(filesRect?.width).toBeGreaterThan(240);
  18 | });
  19 | 
```