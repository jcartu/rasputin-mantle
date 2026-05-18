# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: computer-view.spec.ts >> Computer View >> shows empty state when Neko is unavailable
- Location: tests/e2e/computer-view.spec.ts:4:7

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('text=Live Computer View')
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for locator('text=Live Computer View')

```

```yaml
- separator
- button "Share"
- region "Chat":
  - button "Collapse chat pane":
    - img
  - text: session test-session-123 error
  - alert:
    - img
    - paragraph: Connection to event stream failed
    - button "Retry":
      - img
      - text: Retry
- region "Computer view": "Sandbox initializing… session: test-session-123"
- region "Files":
  - button "Collapse files pane":
    - img
  - tree "Sandbox file tree":
    - text: Sandbox files
    - alert:
      - img
      - text: Failed to list / (404)
- separator
- navigation "Mobile navigation":
  - button "Chat"
  - button "Computer"
  - button "Files"
- status:
  - img
  - text: Static route
  - button "Hide static indicator":
    - img
- alert
```

# Test source

```ts
  1  | import { test, expect } from "@playwright/test";
  2  | 
  3  | test.describe("Computer View", () => {
  4  |   test("shows empty state when Neko is unavailable", async ({ page }) => {
  5  |     // Mock the session creation API
  6  |     await page.route("**/api/sessions", async (route) => {
  7  |       if (route.request().method() === "POST") {
  8  |         await route.fulfill({
  9  |           status: 200,
  10 |           contentType: "application/json",
  11 |           body: JSON.stringify({ id: "test-session-123" }),
  12 |         });
  13 |       } else {
  14 |         await route.fulfill({
  15 |           status: 200,
  16 |           contentType: "application/json",
  17 |           body: JSON.stringify([]),
  18 |         });
  19 |       }
  20 |     });
  21 | 
  22 |     // Mock the messages API
  23 |     await page.route("**/api/sessions/*/messages", async (route) => {
  24 |       await route.fulfill({
  25 |         status: 200,
  26 |         contentType: "application/json",
  27 |         body: JSON.stringify([]),
  28 |       });
  29 |     });
  30 | 
  31 |     // Mock the health probe to fail (Neko not running)
  32 |     await page.route("**/health", async (route) => {
  33 |       await route.fulfill({
  34 |         status: 503,
  35 |         contentType: "text/plain",
  36 |         body: "Service Unavailable",
  37 |       });
  38 |     });
  39 | 
  40 |     // Navigate to a session page
  41 |     await page.goto("/session/test-session-123");
  42 | 
  43 |     // Check that the empty state is shown (not an iframe)
> 44 |     await expect(page.locator("text=Live Computer View")).toBeVisible();
     |                                                           ^ Error: expect(locator).toBeVisible() failed
  45 |     await expect(page.locator("text=Neko desktop instance is not available")).toBeVisible();
  46 |     await expect(page.locator("text=Retry")).toBeVisible();
  47 | 
  48 |     // Verify no iframe is present when Neko is down
  49 |     const iframe = page.locator("iframe");
  50 |     await expect(iframe).not.toBeVisible();
  51 |   });
  52 | });
  53 | 
```