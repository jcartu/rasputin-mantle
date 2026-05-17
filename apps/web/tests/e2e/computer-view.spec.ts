import { test, expect } from "@playwright/test";

test.describe("Computer View", () => {
  test("renders iframe with correct Neko URL", async ({ page }) => {
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

    // Navigate to a session page
    await page.goto("/session/test-session-123");

    // Check if iframe exists
    const iframe = page.locator("iframe");
    await expect(iframe).toBeVisible();

    // Check if iframe src contains the expected Neko URL parameters
    const src = await iframe.getAttribute("src");
    expect(src).toContain("user=mantle");
    expect(src).toContain("pass=mantle-dev");
  });
});
