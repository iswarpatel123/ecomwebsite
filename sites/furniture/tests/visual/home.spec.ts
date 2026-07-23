import { test } from "@playwright/test";
import { expectVisualSnapshot } from "./visual.helper.ts";

/**
 * Visual regression tests for the furniture site.
 * Run with: npm --workspace sites/furniture run test:visual
 *
 * The first run writes baselines under tests/visual/baselines/. Commit those
 * baselines; later runs fail on unintended visual changes.
 */
test.describe("furniture visual", () => {
  test("homepage matches baseline", async ({ page }, testInfo) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");
    await expectVisualSnapshot(page, "home", testInfo);
  });
});
