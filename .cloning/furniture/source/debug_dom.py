#!/usr/bin/env python3
"""Debug DOM structure for Koala collection + nav."""
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
from clone_workflow.extractor import PlaywrightExtractor

DEBUG = r"""
() => {
  const grids = [...document.querySelectorAll('*')].filter(el => {
    const s = getComputedStyle(el);
    return s.display === 'grid' && el.getBoundingClientRect().width > 800;
  }).slice(0, 5).map(el => ({
    tag: el.tagName,
    cls: String(el.className).slice(0, 120),
    cols: getComputedStyle(el).gridTemplateColumns,
    gap: getComputedStyle(el).gap,
    rect: el.getBoundingClientRect(),
    childCount: el.children.length,
  }));

  const navLinks = [...document.querySelectorAll('header a, nav a, [class*="nav"] a')].filter(a =>
    /modular/i.test(a.textContent || '')
  ).map(a => ({
    text: (a.textContent || '').trim().slice(0, 40),
    href: a.getAttribute('href'),
    cls: String(a.className).slice(0, 80),
    rect: a.getBoundingClientRect(),
  }));

  const productCards = [...document.querySelectorAll('[class*="product"], [class*="card"], [class*="grid"] > *')].filter(el => {
    const r = el.getBoundingClientRect();
    return r.width > 200 && r.height > 300 && el.querySelector('img');
  }).slice(0, 3).map(el => ({
    tag: el.tagName,
    cls: String(el.className).slice(0, 120),
    rect: el.getBoundingClientRect(),
    border: getComputedStyle(el).border,
    bg: getComputedStyle(el).backgroundColor,
    radius: getComputedStyle(el).borderRadius,
    shadow: getComputedStyle(el).boxShadow,
  }));

  return { grids, navLinks, productCards, title: document.title };
}
"""


async def main():
    async with PlaywrightExtractor(headless=True) as ext:
        page = await ext._browser.new_page(viewport={"width": 1440, "height": 900})
        await page.goto("https://us.koala.com/collections/bangalow-modular-sofas", wait_until="load", timeout=120000)
        await page.wait_for_timeout(4000)
        await ext.dismiss_page_popups(page)
        data = await page.evaluate(DEBUG)
        print("COLLECTION:", json.dumps(data, indent=2))

        await page.goto("https://us.koala.com/", wait_until="load", timeout=120000)
        await page.wait_for_timeout(3000)
        await ext.dismiss_page_popups(page)
        nav = await page.evaluate(DEBUG)
        print("HOME NAV:", json.dumps(nav, indent=2))

        # Try hover approaches
        for sel in ['text=Modular Sofas', 'a:has-text("Modular Sofas")', '[href*="modular-sofa"]']:
            loc = page.locator(sel).first
            try:
                if await loc.count() == 0:
                    print(f"MISS {sel}")
                    continue
                bb = await loc.bounding_box()
                print(f"FOUND {sel} at {bb}")
                await loc.hover(timeout=5000)
                await page.wait_for_timeout(1500)
                panels = await page.evaluate("""() => {
                  return [...document.querySelectorAll('*')].filter(el => {
                    const r = el.getBoundingClientRect();
                    const s = getComputedStyle(el);
                    return r.height > 80 && r.width > 900 && r.top >= 60 && r.top < 500 &&
                      s.display !== 'none' && s.visibility !== 'hidden' && parseFloat(s.opacity||'1') > 0.9;
                  }).sort((a,b) => b.getBoundingClientRect().height - a.getBoundingClientRect().height)
                  .slice(0, 8).map(el => ({
                    tag: el.tagName,
                    cls: String(el.className).slice(0, 150),
                    rect: el.getBoundingClientRect(),
                    bg: getComputedStyle(el).backgroundColor,
                    display: getComputedStyle(el).display,
                    zIndex: getComputedStyle(el).zIndex,
                    padding: getComputedStyle(el).padding,
                    shadow: getComputedStyle(el).boxShadow,
                  }));
                }""")
                print(f"PANELS after hover {sel}:", json.dumps(panels, indent=2))
            except Exception as e:
                print(f"ERR {sel}: {e}")

        await page.close()


if __name__ == "__main__":
    asyncio.run(main())
