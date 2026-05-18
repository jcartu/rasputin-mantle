# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: keyboard-shortcuts.spec.ts >> ⌘\ toggles chat pane
- Location: tests/e2e/keyboard-shortcuts.spec.ts:10:5

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('[data-pane="chat"]')
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for locator('[data-pane="chat"]')

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
  3  | test('⌘K opens command palette', async ({ page }) => {
  4  |   await page.goto('/');
  5  |   await page.press('body', 'Control+k');
  6  |   const palette = page.locator('[data-command-palette]');
  7  |   await expect(palette).toBeVisible();
  8  | });
  9  | 
  10 | test('⌘\\ toggles chat pane', async ({ page }) => {
  11 |   await page.goto('/');
  12 |   const chatPane = page.locator('[data-pane="chat"]');
> 13 |   await expect(chatPane).toBeVisible();
     |                          ^ Error: expect(locator).toBeVisible() failed
  14 | });
  15 | 
  16 | test('⌘B toggles files pane', async ({ page }) => {
  17 |   await page.goto('/');
  18 |   const filesPane = page.locator('[data-pane="files"]');
  19 |   await expect(filesPane).toBeVisible();
  20 | });
  21 | 
```