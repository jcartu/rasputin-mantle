import { test, expect } from "@playwright/test";

test.describe("Computer View", () => {
  test("shows empty state when Neko is unavailable", async ({ page }) => {
    // Mock the session creation API
    await page.route("**/api/sessions", async (route) => {
      if (route.request().method() === "POST") {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({ id: "test-session-123" }),
        });
      } else {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify([]),
        });
      }
    });

    // Mock the messages API
    await page.route("**/api/sessions/*/messages", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([]),
      });
    });

    // Mock the health probe to fail (Neko not running)
    await page.route("**/health", async (route) => {
      await route.fulfill({
        status: 503,
        contentType: "text/plain",
        body: "Service Unavailable",
      });
    });

    // Navigate to a session page
    await page.goto("/session/test-session-123");

    // Check that the empty state is shown (not an iframe)
    await expect(page.locator("text=Live Computer View")).toBeVisible();
    await expect(page.locator("text=Neko desktop instance is not available")).toBeVisible();
    await expect(page.locator("text=Retry")).toBeVisible();

    // Verify no iframe is present when Neko is down
    const iframe = page.locator("iframe");
    await expect(iframe).not.toBeVisible();
  });
});
