# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: no-layout-shift-on-resize.spec.ts >> no layout shift on resize
- Location: tests/e2e/no-layout-shift-on-resize.spec.ts:3:5

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: locator.boundingBox: Test timeout of 30000ms exceeded.
Call log:
  - waiting for locator('[data-top-bar]')

```

# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - generic [ref=e2]:
    - button "New Session" [ref=e4]
    - generic [ref=e6]: No sessions yet
  - main [ref=e7]:
    - generic [ref=e8]: Select a session or create a new one
  - status [ref=e9]:
    - generic [ref=e10]:
      - img [ref=e12]
      - generic [ref=e14]:
        - text: Static route
        - button "Hide static indicator" [ref=e15] [cursor=pointer]:
          - img [ref=e16]
  - alert [ref=e19]
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test('no layout shift on resize', async ({ page }) => {
  4  |   await page.setViewportSize({ width: 1920, height: 1080 });
  5  |   await page.goto('/');
  6  | 
  7  |   // Wait for initial render
  8  |   await page.waitForTimeout(500);
  9  | 
  10 |   // Get initial positions
  11 |   const topBar = page.locator('[data-top-bar]');
  12 |   const bottomBar = page.locator('[data-bottom-bar]');
  13 | 
> 14 |   const topRect1 = await topBar.boundingBox();
     |                                 ^ Error: locator.boundingBox: Test timeout of 30000ms exceeded.
  15 |   const bottomRect1 = await bottomBar.boundingBox();
  16 | 
  17 |   // Resize
  18 |   await page.setViewportSize({ width: 1366, height: 768 });
  19 |   await page.waitForTimeout(300);
  20 | 
  21 |   const topRect2 = await topBar.boundingBox();
  22 |   const bottomRect2 = await bottomBar.boundingBox();
  23 | 
  24 |   // Bars should maintain their positions
  25 |   // Bars should maintain their positions (x/y are stable)
  26 |   expect(topRect2?.x).toBe(topRect1?.x);
  27 |   expect(topRect2?.y).toBe(topRect1?.y);
  28 |   expect(topRect2?.height).toBe(topRect1?.height);
  29 | });
  30 | 
```