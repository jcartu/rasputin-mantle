# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: mobile-tab-switch.spec.ts >> mobile tab bar appears at ≤768px
- Location: tests/e2e/mobile-tab-switch.spec.ts:3:5

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('[data-mobile-tabs]')
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for locator('[data-mobile-tabs]')

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
  3  | test('mobile tab bar appears at ≤768px', async ({ page }) => {
  4  |   await page.setViewportSize({ width: 375, height: 667 });
  5  |   await page.goto('/');
  6  |   const mobileTabs = page.locator('[data-mobile-tabs]');
> 7  |   await expect(mobileTabs).toBeVisible();
     |                            ^ Error: expect(locator).toBeVisible() failed
  8  | });
  9  | 
  10 | test('desktop shell appears at >768px', async ({ page }) => {
  11 |   await page.setViewportSize({ width: 1280, height: 900 });
  12 |   await page.goto('/');
  13 |   const mobileTabs = page.locator('[data-mobile-tabs]');
  14 |   await expect(mobileTabs).not.toBeVisible();
  15 | });
  16 | 
```