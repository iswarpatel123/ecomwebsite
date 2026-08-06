#!/usr/bin/env python3
import asyncio, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
from clone_workflow.extractor import PlaywrightExtractor

EXTRA = r"""
() => {
  const pick = (el) => {
    if (!el) return null;
    const s = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    return {
      display: s.display, gap: s.gap, cols: s.gridTemplateColumns,
      width: s.width, height: s.height, padding: s.padding, margin: s.margin,
      bg: s.backgroundColor, border: s.border, borderColor: s.borderColor, borderWidth: s.borderWidth,
      borderTop: s.borderTop, borderRadius: s.borderRadius, shadow: s.boxShadow,
      fontSize: s.fontSize, fontWeight: s.fontWeight, color: s.color, lineHeight: s.lineHeight,
      aspectRatio: s.aspectRatio, position: s.position,
      rect: { w: r.width, h: r.height },
    };
  };

  const grid = document.querySelector('ul.product-grid');
  const li = grid?.querySelector('li.product-list-item');
  const cardWrapper = li?.querySelector('.card-wrapper');
  const card = li?.querySelector('.card');
  const cardMedia = li?.querySelector('.card__media, .media');
  const cardInner = li?.querySelector('.card__inner');
  const cardImg = li?.querySelector('.card__media img, .media img');
  const title = li?.querySelector('.card__heading');
  const section = document.querySelector('.collection-grid-wrapper, .section-template--');

  const tileItems = [...document.querySelectorAll('.mega-menu__complex-item')];
  const categoryTile = tileItems[0];
  const categoryImg = categoryTile?.querySelector('img');
  const categoryLabel = categoryTile?.querySelector('.mega-menu__complex-item-title, span, p');
  const lifestyleTiles = tileItems.filter(t => t.getBoundingClientRect().top > 350);
  const lifestyleTile = lifestyleTiles[0] || tileItems.find(t => t.getBoundingClientRect().width > 200);
  const lifestyleImg = lifestyleTile?.querySelector('img');

  return {
    section: pick(section),
    collectionGrid: pick(grid),
    productCell: pick(li),
    cardWrapper: pick(cardWrapper),
    productCard: pick(card),
    cardMedia: pick(cardMedia),
    cardInner: pick(cardInner),
    productImage: pick(cardImg),
    productTitle: pick(title),
    megaWrapper: pick(document.querySelector('.mega-menu-wrapper')),
    navDropdown: {
      panel: pick(document.querySelector('.mega-menu-wrapper')),
      inner: pick(document.querySelector('.mega-menu--inner')),
      headerRow: pick(document.querySelector('.mega-menu__complex-header')),
      title: pick(document.querySelector('.mega-menu__complex-title')),
      shopAll: pick(document.querySelector('.mega-menu__complex-header .button')),
      tileGrid: pick(document.querySelector('.mega-menu__complex-list')),
      tile: pick(categoryTile),
      tileImage: pick(categoryImg),
      tileLabel: pick(categoryLabel),
      lifestyleTile: pick(lifestyleTile),
      lifestyleImage: pick(lifestyleImg),
    },
    page: { backgroundColor: getComputedStyle(document.body).backgroundColor },
  };
}
"""

async def main():
    async with PlaywrightExtractor(headless=True) as ext:
        page = await ext._browser.new_page(viewport={"width": 1440, "height": 900})
        url = "https://us.koala.com/collections/bangalow-modular-sofas"
        await page.goto(url, wait_until="load", timeout=120000)
        await page.wait_for_timeout(5000)
        await ext.dismiss_page_popups(page)

        # collection grid screenshot
        grid = page.locator('ul.product-grid').first
        await grid.scroll_into_view_if_needed()
        await page.wait_for_timeout(500)
        clip = await grid.evaluate("""el => {
          const r = el.getBoundingClientRect();
          return { x: Math.max(0, r.x - 20), y: Math.max(106, r.y - 10), width: Math.min(1440, r.width + 40), height: Math.min(680, r.height) };
        }""")
        await page.screenshot(path=str(ROOT/".cloning/furniture/reference/collection-grid-desktop.png"), clip=clip)

        # open mega menu
        bb = await page.locator('header .header__mega-menu').first.bounding_box()
        await page.mouse.move(bb["x"] + 75, bb["y"] + 20)
        await page.wait_for_timeout(1800)

        data = await page.evaluate(EXTRA)
        print(json.dumps(data, indent=2))

        await page.screenshot(path=str(ROOT/".cloning/furniture/reference/nav-dropdown-modular-desktop.png"))
        await page.close()

asyncio.run(main())
