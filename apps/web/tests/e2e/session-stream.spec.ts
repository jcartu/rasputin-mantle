import { test, expect } from "@playwright/test";

test.describe("Session Stream", () => {
  test("receives and displays SSE events", async ({ page }) => {
    // Mock the session creation API
    await page.route("**/api/sessions", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([]),
      });
    });

    // Mock the messages API
    await page.route("**/api/sessions/*/messages", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([]),
      });
    });

    // We need to mock the EventSource endpoint
    // Playwright doesn't natively intercept EventSource easily with page.route
    // So we'll inject a mock EventSource into the page
    await page.addInitScript(() => {
      class MockEventSource {
        onmessage: ((ev: any) => void) | null = null;
        onopen: (() => void) | null = null;
        onerror: (() => void) | null = null;
        
        constructor(url: string) {
          setTimeout(() => {
            if (this.onopen) this.onopen();
            
            // Send a mock event after connection
            setTimeout(() => {
              if (this.onmessage) {
                this.onmessage({
                  data: JSON.stringify({
                    id: "evt-1",
                    type: "agent_action",
                    data: { action: "click", target: "button" },
                    timestamp: new Date().toISOString()
                  })
                });
              }
            }, 100);
          }, 50);
        }
        
        close() {}
      }
      
      (window as any).EventSource = MockEventSource;
    });

    await page.goto("/session/test-session-123");

    // Check if the event stream panel shows the connected status
    await expect(page.locator("text=connected")).toBeVisible();

    // Check if the mock event data is displayed
    await expect(page.locator("text=agent_action")).toBeVisible();
    await expect(page.locator("text=click")).toBeVisible();
    await expect(page.locator("text=button")).toBeVisible();
  });
});
