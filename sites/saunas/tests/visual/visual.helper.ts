import { expect, TestInfo } from "@playwright/test";
import { PNG } from "pngjs";
import pixelmatch from "pixelmatch";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";

/**
 * Minimal visual-regression helper: captures a full-page screenshot and
 * pixel-diffs it against a committed baseline. The first run establishes the
 * baseline (writes the PNG and passes). Subsequent runs fail when the mismatch
 * ratio exceeds `threshold`, and attach a diff image to the HTML report.
 */
const BASELINES_DIR = path.join(__dirname, "baselines");

export async function expectVisualSnapshot(
  page: import("@playwright/test").Page,
  name: string,
  testInfo: TestInfo,
  opts: { threshold?: number; fullPage?: boolean } = {}
) {
  const threshold = opts.threshold ?? 0.1;
  const baselinePath = path.join(BASELINES_DIR, `${name}.png`);
  const actual = await page.screenshot({ type: "png", fullPage: opts.fullPage ?? true });

  if (!existsSync(BASELINES_DIR)) mkdirSync(BASELINES_DIR, { recursive: true });

  if (!existsSync(baselinePath)) {
    writeFileSync(baselinePath, actual);
    // eslint-disable-next-line no-console
    console.warn(`[visual] baseline created: ${baselinePath}`);
    return;
  }

  const expected = PNG.sync.read(readFileSync(baselinePath));
  const actualPng = PNG.sync.read(actual);

  const width = Math.min(expected.width, actualPng.width);
  const height = Math.min(expected.height, actualPng.height);
  const diff = new PNG({ width, height });

  const mismatchPx = pixelmatch(
    expected.data,
    actualPng.data,
    diff.data,
    width,
    height,
    { threshold: 0.1, includeAA: true }
  );

  const totalPx = width * height;
  const ratio = totalPx ? mismatchPx / totalPx : 1;

  if (ratio > threshold) {
    const diffPath = testInfo.outputPath(`${name}-diff.png`);
    writeFileSync(diffPath, PNG.sync.write(diff));
    await testInfo.attach(`${name}-diff`, { path: diffPath, contentType: "image/png" });
    expect(ratio, `Visual mismatch ${(ratio * 100).toFixed(2)}% > ${threshold * 100}%`).toBeLessThanOrEqual(threshold);
  }
}
