#!/usr/bin/env python3
import asyncio, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
from clone_workflow.extractor import PlaywrightExtractor

async def main():
    async with PlaywrightExtractor(headless=True) as ext:
        page = await ext._browser.new_page(viewport={"width": 1440, "height": 900})
        url = "https://us.koala.com/collections/bangalow-modular-sofas"
        await page.goto(url, wait_until="load", timeout=120000)
        await page.wait_for_timeout(5000)
        await ext.dismiss_page_popups(page)
        await page.wait_for_timeout(1000)

        # Hover modular sofas in header
        loc = page.locator("header .header__mega-menu").first
        print("mega count", await loc.count())
        bb = await loc.bounding_box()
        print("mega bb", bb)
        if bb:
            await page.mouse.move(bb["x"] + 75, bb["y"] + 20)
            await page.wait_for_timeout(200)
            await page.mouse.move(bb["x"] + 75, bb["y"] + 20)
        await page.wait_for_timeout(1500)

        data = await page.evaluate("""() => {
          const pick = (sel) => {
            const el = typeof sel === 'string' ? document.querySelector(sel) : sel;
            if (!el) return null;
            const s = getComputedStyle(el);
            const r = el.getBoundingClientRect();
            return {
              selector: typeof sel === 'string' ? sel : null,
              cls: String(el.className).slice(0,140),
              display: s.display, position: s.position, width: s.width, height: s.height,
              bg: s.backgroundColor, padding: s.padding,
              border: s.border, borderTop: s.borderTop, borderBottom: s.borderBottom,
              shadow: s.boxShadow, gap: s.gap, cols: s.gridTemplateColumns,
              radius: s.borderRadius, fontSize: s.fontSize, fontWeight: s.fontWeight, color: s.color,
              rect: {x:r.x,y:r.y,w:r.width,h:r.height},
              visible: r.height > 0 && r.width > 0,
            };
          };
          const allMega = [...document.querySelectorAll('[class*="mega-menu"]')].map(el => ({
            cls: String(el.className).slice(0,100),
            rect: el.getBoundingClientRect(),
            display: getComputedStyle(el).display,
            opacity: getComputedStyle(el).opacity,
            visibility: getComputedStyle(el).visibility,
            bg: getComputedStyle(el).backgroundColor,
          }));
          return {
            allMega: allMega.filter(x => x.rect.height > 0).slice(0, 10),
            pageBg: pick('body'),
            panel: pick('.mega-menu__content') || pick('.mega-menu'),
            headerRow: pick('.mega-menu__complex-header'),
            shopAll: pick('.mega-menu__complex-header .button'),
            tileGrid: pick('.mega-menu__complex-list'),
            tile: pick('.mega-menu__complex-item'),
          };
        }""")
        print(json.dumps(data, indent=2))
        await page.screenshot(path=str(ROOT/".cloning/furniture/reference/nav-test.png"))
        await page.close()

asyncio.run(main())
