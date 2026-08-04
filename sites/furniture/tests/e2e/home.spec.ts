import { test, expect } from "@playwright/test";

/**
 * Functional (e2e) smoke tests for the furniture site.
 * Run with: npm --workspace sites/furniture run test:e2e
 */
test.describe("furniture site", () => {
  test("home page loads with a document title", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveTitle(/\S+/);
  });

  test("no console errors on initial load", async ({ page }) => {
    const errors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") errors.push(msg.text());
    });
    page.on("pageerror", (err) => errors.push(err.message));
    await page.goto("/");
    await page.waitForLoadState("networkidle");
    expect(errors, errors.join("\n")).toHaveLength(0);
  });

  test("navigation between routes works", async ({ page }) => {
    await page.goto("/");
    const about = page.getByRole("link", { name: /about/i });
    if (await about.count()) {
      await about.first().click();
      await expect(page).toHaveURL(/\/about/);
    }
  });
});
