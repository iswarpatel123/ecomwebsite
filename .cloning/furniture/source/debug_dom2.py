#!/usr/bin/env python3
import asyncio, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
from clone_workflow.extractor import PlaywrightExtractor

SCRIPT = r"""
() => {
  const pick = (el) => {
    if (!el) return null;
    const s = getComputedStyle(el);
    return {
      tag: el.tagName, cls: String(el.className).slice(0,120),
      display: s.display, gap: s.gap, cols: s.gridTemplateColumns,
      bg: s.backgroundColor, border: s.border, radius: s.borderRadius, shadow: s.boxShadow,
      padding: s.padding, margin: s.margin, width: s.width, height: s.height,
      fontSize: s.fontSize, fontWeight: s.fontWeight, color: s.color,
      rect: el.getBoundingClientRect(),
    };
  };

  const grid = document.querySelector('ul.product-grid, ul.grid.product-grid');
  const items = grid ? [...grid.querySelectorAll(':scope > li')].slice(0,2).map(pick) : [];
  const card = grid?.querySelector('li .card-wrapper, li .card, li .product-card-wrapper, li > div');
  const cardInner = card ? pick(card) : null;
  const imgWrap = card?.querySelector('.card__media, .media, [class*="media"]');
  const title = card?.querySelector('.card__heading, h3, [class*="heading"]');
  const main = document.querySelector('#MainContent, main');

  const headerLinks = [...document.querySelectorAll('header .header__menu-item, header nav a, .list-menu__item--link')].map(a => ({
    text: (a.textContent||'').replace(/\s+/g,' ').trim().slice(0,50),
    cls: String(a.className).slice(0,100),
    rect: a.getBoundingClientRect(),
    href: a.getAttribute('href'),
    hasDetails: !!a.closest('details, [data-menu], [class*="mega"]'),
    parentCls: a.parentElement ? String(a.parentElement.className).slice(0,80) : '',
  })).filter(x => x.rect.width > 0);

  return { grid: pick(grid), items, cardInner, image: pick(imgWrap), title: pick(title), mainBg: pick(main), headerLinks };
}
"""

PANELS = r"""
() => [...document.querySelectorAll('*')].filter(el => {
  const r = el.getBoundingClientRect(); const s = getComputedStyle(el);
  return r.height > 120 && r.width > 1000 && r.top > 80 && r.top < 350 && s.display !== 'none';
}).sort((a,b)=>b.getBoundingClientRect().height-a.getBoundingClientRect().height).slice(0,6).map(el => ({
  tag: el.tagName, cls: String(el.className).slice(0,160),
  rect: el.getBoundingClientRect(), bg: getComputedStyle(el).backgroundColor,
  padding: getComputedStyle(el).padding, borderTop: getComputedStyle(el).borderTop,
  shadow: getComputedStyle(el).boxShadow, zIndex: getComputedStyle(el).zIndex,
}))
"""

async def main():
    async with PlaywrightExtractor(headless=True) as ext:
        page = await ext._browser.new_page(viewport={"width": 1440, "height": 900})
        await page.goto("https://us.koala.com/collections/bangalow-modular-sofas", wait_until="load", timeout=120000)
        await page.wait_for_timeout(4000)
        await ext.dismiss_page_popups(page)
        print("GRID", json.dumps(await page.evaluate(SCRIPT), indent=2))

        await page.goto("https://us.koala.com/", wait_until="load", timeout=120000)
        await page.wait_for_timeout(4000)
        await ext.dismiss_page_popups(page)
        print("HEADER", json.dumps(await page.evaluate(SCRIPT), indent=2))

        # Find Modular Sofas in header
        triggers = [
            'header summary:has-text("Modular Sofas")',
            'header details:has-text("Modular Sofas")',
            'header .header__menu-item:has-text("Modular Sofas")',
            'nav .list-menu__item:has-text("Modular Sofas")',
            'header button:has-text("Modular Sofas")',
        ]
        for sel in triggers:
            loc = page.locator(sel).first
            if await loc.count() == 0:
                continue
            print(f"TRY {sel}")
            bb = await loc.bounding_box()
            print("bbox", bb)
            await loc.hover(force=True)
            await page.wait_for_timeout(1200)
            # keep mouse in dropdown zone
            if bb:
                await page.mouse.move(bb["x"] + bb["width"]/2, bb["y"] + bb["height"] + 200)
            await page.wait_for_timeout(800)
            panels = await page.evaluate(PANELS)
            print("PANELS", json.dumps(panels, indent=2))
            if panels:
                await page.screenshot(path=str(ROOT/".cloning/furniture/reference/nav-dropdown-modular-desktop.png"))
                break

        await page.close()

asyncio.run(main())
