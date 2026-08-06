#!/usr/bin/env python3
import asyncio, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
from clone_workflow.extractor import PlaywrightExtractor

MEGA = r"""
(open) => {
  const pick = (el) => {
    if (!el) return null;
    const s = getComputedStyle(el);
    return {
      cls: String(el.className).slice(0,140),
      display: s.display, position: s.position, width: s.width, height: s.height,
      bg: s.backgroundColor, padding: s.padding, margin: s.margin,
      border: s.border, borderTop: s.borderTop, borderBottom: s.borderBottom,
      shadow: s.boxShadow, gap: s.gap, cols: s.gridTemplateColumns,
      radius: s.borderRadius, fontSize: s.fontSize, fontWeight: s.fontWeight, color: s.color,
      rect: el.getBoundingClientRect(), visible: el.getBoundingClientRect().height > 0,
    };
  };

  const modular = [...document.querySelectorAll('header .header__menu-item, header summary, header button')].find(el => /modular sofas/i.test(el.textContent||''));
  const megaRoot = document.querySelector('.mega-menu, .header__mega-menu, [class*="mega-menu"]');
  const panel = document.querySelector('.mega-menu__content, .mega-menu__inner, .header__mega-menu .mega-menu, details[open] .mega-menu__content') ||
    [...document.querySelectorAll('[class*="mega-menu"]')].find(el => el.getBoundingClientRect().height > 100);
  const headerRow = document.querySelector('.mega-menu__complex-header, .mega-menu__header');
  const title = headerRow?.querySelector('h2, h3, p, span');
  const shopAll = headerRow?.querySelector('a.button, .button, a[href*="modular-sofas"]');
  const tileGrid = document.querySelector('.mega-menu__complex-list, .mega-menu__grid, .mega-menu__complex-items');
  const tile = document.querySelector('.mega-menu__complex-item, .mega-menu__item');
  const tileImg = tile?.querySelector('img');
  const tileLabel = tile?.querySelector('span, p');
  const lifestyle = [...document.querySelectorAll('.mega-menu__complex-item, .mega-menu__item')].find(el => {
    const r = el.getBoundingClientRect();
    return r.width > 180;
  });

  return {
    pageBg: pick(document.body)?.bg,
    sectionBg: pick(document.querySelector('#MainContent section, main section'))?.bg,
    modularTrigger: pick(modular),
    megaRoot: pick(megaRoot),
    panel: pick(panel),
    headerRow: pick(headerRow),
    title: pick(title),
    shopAll: pick(shopAll),
    tileGrid: pick(tileGrid),
    tile: pick(tile),
    tileImg: pick(tileImg),
    lifestyleTile: pick(lifestyle),
    openDetails: [...document.querySelectorAll('header details')].map(d => ({open: d.open, cls: String(d.className).slice(0,80), text: (d.textContent||'').slice(0,30)})),
  };
}
"""

async def main():
    async with PlaywrightExtractor(headless=True) as ext:
        page = await ext._browser.new_page(viewport={"width": 1440, "height": 900})
        await page.goto("https://us.koala.com/", wait_until="load", timeout=120000)
        await page.wait_for_timeout(4000)
        await ext.dismiss_page_popups(page)

        # Hover Modular Sofas trigger
        trigger = page.locator('header .header__mega-menu .header__menu-item').filter(has_text="Modular Sofas").first
        if await trigger.count() == 0:
            trigger = page.locator('header').get_by_text("Modular Sofas", exact=True).first
        bb = await trigger.bounding_box()
        print("trigger", bb)
        await trigger.hover(force=True)
        await page.wait_for_timeout(500)
        if bb:
            await page.mouse.move(bb["x"] + bb["width"]/2, bb["y"] + 250)
        await page.wait_for_timeout(1000)

        data = await page.evaluate(MEGA, True)
        print(json.dumps(data, indent=2))
        await page.screenshot(path=str(ROOT/".cloning/furniture/reference/nav-dropdown-modular-desktop.png"))
        await page.close()

asyncio.run(main())
