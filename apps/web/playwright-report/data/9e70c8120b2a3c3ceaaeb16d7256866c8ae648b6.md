# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: session-stream.spec.ts >> Session Stream >> receives and displays SSE events
- Location: tests/e2e/session-stream.spec.ts:4:7

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('text=agent_action')
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for locator('text=agent_action')

```

```yaml
- separator
- button "Share"
- region "Chat":
  - button "Collapse chat pane":
    - img
  - text: session test-session-123 connected
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
  3  | test.describe("Session Stream", () => {
  4  |   test("receives and displays SSE events", async ({ page }) => {
  5  |     // Mock the session creation API
  6  |     await page.route("**/api/sessions", async (route) => {
  7  |       await route.fulfill({
  8  |         status: 200,
  9  |         contentType: "application/json",
  10 |         body: JSON.stringify([]),
  11 |       });
  12 |     });
  13 | 
  14 |     // Mock the messages API
  15 |     await page.route("**/api/sessions/*/messages", async (route) => {
  16 |       await route.fulfill({
  17 |         status: 200,
  18 |         contentType: "application/json",
  19 |         body: JSON.stringify([]),
  20 |       });
  21 |     });
  22 | 
  23 |     // We need to mock the EventSource endpoint
  24 |     // Playwright doesn't natively intercept EventSource easily with page.route
  25 |     // So we'll inject a mock EventSource into the page
  26 |     await page.addInitScript(() => {
  27 |       class MockEventSource {
  28 |         onmessage: ((ev: any) => void) | null = null;
  29 |         onopen: (() => void) | null = null;
  30 |         onerror: (() => void) | null = null;
  31 |         
  32 |         constructor(url: string) {
  33 |           setTimeout(() => {
  34 |             if (this.onopen) this.onopen();
  35 |             
  36 |             // Send a mock event after connection
  37 |             setTimeout(() => {
  38 |               if (this.onmessage) {
  39 |                 this.onmessage({
  40 |                   data: JSON.stringify({
  41 |                     id: "evt-1",
  42 |                     type: "agent_action",
  43 |                     data: { action: "click", target: "button" },
  44 |                     timestamp: new Date().toISOString()
  45 |                   })
  46 |                 });
  47 |               }
  48 |             }, 100);
  49 |           }, 50);
  50 |         }
  51 |         
  52 |         close() {}
  53 |       }
  54 |       
  55 |       (window as any).EventSource = MockEventSource;
  56 |     });
  57 | 
  58 |     await page.goto("/session/test-session-123");
  59 | 
  60 |     // Check if the event stream panel shows the connected status
  61 |     await expect(page.locator("text=connected")).toBeVisible();
  62 | 
  63 |     // Check if the mock event data is displayed
> 64 |     await expect(page.locator("text=agent_action")).toBeVisible();
     |                                                     ^ Error: expect(locator).toBeVisible() failed
  65 |     await expect(page.locator("text=click")).toBeVisible();
  66 |     await expect(page.locator("text=button")).toBeVisible();
  67 |   });
  68 | });
  69 | 
```