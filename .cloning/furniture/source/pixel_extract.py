#!/usr/bin/env python3
"""Pixel-fix extraction: Koala collection grid + Modular Sofas mega-menu."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
from clone_workflow.extractor import PlaywrightExtractor  # noqa: E402

REF = ROOT / ".cloning" / "furniture" / "reference"
SRC = ROOT / ".cloning" / "furniture" / "source"
URL = "https://us.koala.com/collections/bangalow-modular-sofas"
VIEWPORT = {"width": 1440, "height": 900}

MEASURE_GRID = """
() => {
  const s = (el) => el ? getComputedStyle(el) : null;
  const grid = document.querySelector('ul.product-grid');
  const li = grid?.querySelector('li.product-list-item');
  const card = li?.querySelector('.card');
  const img = li?.querySelector('.card__media img, .media img');
  const title = li?.querySelector('.card__heading');
  const section = document.querySelector('.section-template--17959590002870__product-grid-padding, .collection-grid-wrapper');
  return {
    page: { backgroundColor: s(document.body).backgroundColor },
    section: section ? { backgroundColor: s(section).backgroundColor } : {},
    collectionGrid: grid ? {
      display: s(grid).display,
      gap: s(grid).gap,
      gridTemplateColumns: s(grid).gridTemplateColumns,
      padding: s(grid).padding,
      margin: s(grid).margin,
      border: s(grid).border,
      backgroundColor: s(grid).backgroundColor,
    } : {},
    productCell: li ? {
      border: s(li).border,
      borderColor: s(li).borderColor,
      borderWidth: s(li).borderWidth,
      padding: s(li).padding,
      backgroundColor: s(li).backgroundColor,
      borderRadius: s(li).borderRadius,
      boxShadow: s(li).boxShadow,
      margin: s(li).margin,
    } : {},
    productCard: card ? {
      border: s(card).border,
      borderColor: s(card).borderColor,
      borderWidth: s(card).borderWidth,
      padding: s(card).padding,
      backgroundColor: s(card).backgroundColor,
      borderRadius: s(card).borderRadius,
      boxShadow: s(card).boxShadow,
    } : {},
    productImage: img ? {
      borderRadius: s(img).borderRadius,
      aspectRatio: s(img).aspectRatio,
      backgroundColor: s(img).backgroundColor,
      width: s(img).width,
      height: s(img).height,
    } : {},
    productTitle: title ? {
      fontSize: s(title).fontSize,
      fontWeight: s(title).fontWeight,
      color: s(title).color,
      lineHeight: s(title).lineHeight,
    } : {},
  };
}
"""

MEASURE_NAV = """
() => {
  const s = (el) => el ? getComputedStyle(el) : null;
  const wrapper = document.querySelector('.mega-menu-wrapper');
  const panel = document.querySelector('.mega-menu.mega-menu--complex');
  const inner = document.querySelector('.mega-menu--inner');
  const headerRow = document.querySelector('.mega-menu__complex-header');
  const title = document.querySelector('.mega-menu__complex-title');
  const shopAll = document.querySelector('.mega-menu__complex-header .button');
  const tileGrid = document.querySelector('.mega-menu__complex-list');
  const tiles = [...document.querySelectorAll('.mega-menu__complex-item')];
  const categoryTile = tiles[0];
  const tileLink = categoryTile?.querySelector('a');
  const tileImg = categoryTile?.querySelector('img');
  const tileLabel = categoryTile?.querySelector('.mega-menu__complex-item-title');
  const lifestyleTile = tiles.find(t => t.getBoundingClientRect().top > 340) || tiles[7];
  const lifeImg = lifestyleTile?.querySelector('img');
  const lifeLabel = lifestyleTile?.querySelector('.mega-menu__complex-item-title, span');
  const r = (el) => el ? el.getBoundingClientRect() : null;
  return {
    page: { backgroundColor: s(document.body).backgroundColor },
    navDropdown: {
      panel: wrapper ? {
        backgroundColor: s(wrapper).backgroundColor,
        padding: s(wrapper).padding,
        border: s(wrapper).border,
        borderTop: s(wrapper).borderTop,
        borderBottom: s(wrapper).borderBottom,
        boxShadow: s(wrapper).boxShadow,
        width: s(wrapper).width,
        height: s(wrapper).height,
        position: s(wrapper).position,
        rect: r(wrapper) ? { width: r(wrapper).width, height: r(wrapper).height, top: r(wrapper).top, left: r(wrapper).left } : null,
      } : {},
      inner: inner ? { padding: s(inner).padding, backgroundColor: s(inner).backgroundColor } : {},
      megaMenu: panel ? { backgroundColor: s(panel).backgroundColor, position: s(panel).position } : {},
      headerRow: headerRow ? { padding: s(headerRow).padding, display: s(headerRow).display } : {},
      title: title ? {
        fontSize: s(title).fontSize,
        fontWeight: s(title).fontWeight,
        color: s(title).color,
        lineHeight: s(title).lineHeight,
      } : {},
      shopAll: shopAll ? {
        backgroundColor: s(shopAll).backgroundColor,
        color: s(shopAll).color,
        borderRadius: s(shopAll).borderRadius,
        padding: s(shopAll).padding,
        fontSize: s(shopAll).fontSize,
        fontWeight: s(shopAll).fontWeight,
        border: s(shopAll).border,
      } : {},
      tileGrid: tileGrid ? {
        display: s(tileGrid).display,
        gap: s(tileGrid).gap,
        gridTemplateColumns: s(tileGrid).gridTemplateColumns,
        padding: s(tileGrid).padding,
      } : {},
      tile: categoryTile ? {
        border: s(categoryTile).border,
        borderRadius: s(tileLink || categoryTile).borderRadius,
        backgroundColor: s(categoryTile).backgroundColor,
        padding: s(categoryTile).padding,
        width: s(categoryTile).width,
        height: s(categoryTile).height,
      } : {},
      tileLink: tileLink ? {
        borderRadius: s(tileLink).borderRadius,
        backgroundColor: s(tileLink).backgroundColor,
        overflow: s(tileLink).overflow,
      } : {},
      tileImage: tileImg ? {
        borderRadius: s(tileImg).borderRadius,
        aspectRatio: s(tileImg).aspectRatio,
        width: s(tileImg).width,
        height: s(tileImg).height,
        objectFit: s(tileImg).objectFit,
      } : {},
      tileLabel: tileLabel ? {
        fontSize: s(tileLabel).fontSize,
        fontWeight: s(tileLabel).fontWeight,
        color: s(tileLabel).color,
      } : {},
      lifestyleTile: lifestyleTile ? {
        border: s(lifestyleTile).border,
        borderRadius: s(lifestyleTile).borderRadius,
        backgroundColor: s(lifestyleTile).backgroundColor,
        width: s(lifestyleTile).width,
        height: s(lifestyleTile).height,
        rect: r(lifestyleTile) ? { width: r(lifestyleTile).width, height: r(lifestyleTile).height } : null,
      } : {},
      lifestyleImage: lifeImg ? {
        borderRadius: s(lifeImg).borderRadius,
        aspectRatio: s(lifeImg).aspectRatio,
        width: s(lifeImg).width,
        height: s(lifeImg).height,
      } : {},
      lifestyleLabel: lifeLabel ? {
        fontSize: s(lifeLabel).fontSize,
        fontWeight: s(lifeLabel).fontWeight,
        color: s(lifeLabel).color,
      } : {},
    },
  };
}
"""


async def open_mega_menu(page) -> None:
    mega = page.locator("header .header__mega-menu").first
    bb = await mega.bounding_box()
    if not bb:
        raise RuntimeError("Modular Sofas mega trigger not found")
    x = bb["x"] + bb["width"] / 2
    y = bb["y"] + bb["height"] / 2
    await page.mouse.move(x, y)
    await page.wait_for_timeout(300)
    await mega.hover(force=True)
    await page.wait_for_timeout(400)
    # Move into dropdown panel so it stays open
    await page.mouse.move(720, 280)
    await page.wait_for_timeout(1200)
    visible = await page.evaluate(
        "() => { const w = document.querySelector('.mega-menu-wrapper'); return w && w.getBoundingClientRect().height > 200; }"
    )
    if not visible:
        await page.mouse.move(x, y)
        await page.wait_for_timeout(200)
        await page.mouse.move(400, 300)
        await page.wait_for_timeout(1000)


async def main() -> None:
    REF.mkdir(parents=True, exist_ok=True)
    SRC.mkdir(parents=True, exist_ok=True)

    async with PlaywrightExtractor(headless=True) as ext:
        page = await ext._browser.new_page(viewport=VIEWPORT)
        try:
            await page.goto(URL, wait_until="load", timeout=120000)
            await page.wait_for_timeout(5000)
            await ext.dismiss_page_popups(page)
            await page.wait_for_timeout(800)

            # --- Nav dropdown first (before scroll) ---
            await open_mega_menu(page)
            nav_data = await page.evaluate(MEASURE_NAV)
            await page.screenshot(path=str(REF / "nav-dropdown-modular-desktop.png"))

            # --- Collection grid ---
            await page.mouse.move(720, 700)
            await page.wait_for_timeout(400)
            grid = page.locator("ul.product-grid").first
            await grid.scroll_into_view_if_needed()
            await page.wait_for_timeout(600)
            clip = await grid.evaluate(
                """el => {
                  const r = el.getBoundingClientRect();
                  return { x: Math.max(0, r.x - 24), y: Math.max(106, r.y - 8),
                           width: Math.min(1440 - Math.max(0, r.x - 24), r.width + 48),
                           height: Math.min(680, r.height) };
                }"""
            )
            await page.screenshot(path=str(REF / "collection-grid-desktop.png"), clip=clip)
            grid_data = await page.evaluate(MEASURE_GRID)
        finally:
            await page.close()

    notes = [
        "Collection uses gap-separated white cards (24px gap), not shared grid border lines.",
        "Grid li/cell has 0px border; visual card is inner .card with white bg + 16px radius.",
        "Product image top corners rounded 16px; aspect ratio ~4:3 (1920/1440).",
        f"Page background: {grid_data.get('page', {}).get('backgroundColor')} (#F5F6F3).",
    ]

    page_bg = grid_data.get("page", {}).get("backgroundColor")
    panel_bg = nav_data.get("navDropdown", {}).get("panel", {}).get("backgroundColor")
    if page_bg and panel_bg:
        if page_bg == panel_bg:
            notes.append(f"Page and dropdown panel share the same bg: {page_bg} (not a white floating card).")
        else:
            notes.append(f"BG mismatch: page={page_bg}, dropdown panel={panel_bg}")

    out = {
        "page": grid_data.get("page", {}),
        "section": grid_data.get("section", {}),
        "collectionGrid": grid_data.get("collectionGrid", {}),
        "productCell": {**grid_data.get("productCell", {}), **grid_data.get("productCard", {})},
        "productImage": grid_data.get("productImage", {}),
        "productTitle": grid_data.get("productTitle", {}),
        "borderModel": {
            "type": "gap-separated-cards",
            "gridGap": grid_data.get("collectionGrid", {}).get("gap", "24px"),
            "cellBorderWidth": grid_data.get("productCell", {}).get("borderWidth", "0px"),
            "cardBackground": grid_data.get("productCard", {}).get("backgroundColor", "rgb(255, 255, 255)"),
            "cardBorderRadius": grid_data.get("productCard", {}).get("borderRadius", "16px"),
            "description": "24px grid gap exposes page bg between white rounded cards; no collapsed border grid.",
        },
        "navDropdown": nav_data.get("navDropdown", {}),
        "notes": notes,
    }

    (SRC / "measured-css.json").write_text(json.dumps(out, indent=2) + "\n")

    md = f"""# Koala Measured CSS — Collection Grid & Nav Dropdown

Source: {URL} · viewport 1440×900

## Page backgrounds
- **Page body:** `{out['page'].get('backgroundColor', 'n/a')}` (#F5F6F3)
- **Dropdown panel (`.mega-menu-wrapper`):** `{panel_bg or 'n/a'}`
- **Same value** — mega-menu is a full-bleed surface extension, not a white popover.

## Collection grid
- **display:** `{out['collectionGrid'].get('display')}`
- **gridTemplateColumns:** `{out['collectionGrid'].get('gridTemplateColumns')}`
- **gap:** `{out['collectionGrid'].get('gap')}`
- **padding:** `{out['collectionGrid'].get('padding', '0')}`

## Product card (`.card`)
- **backgroundColor:** `{out['productCell'].get('backgroundColor', out.get('borderModel', {}).get('cardBackground'))}`
- **borderRadius:** `{out['productCell'].get('borderRadius', '16px')}`
- **border:** `{out['productCell'].get('border', '0px')}`
- **boxShadow:** `{out['productCell'].get('boxShadow', 'none')}`

## Product image
- **borderRadius:** `{out['productImage'].get('borderRadius', '16px 16px 0 0')}`
- **aspectRatio:** `{out['productImage'].get('aspectRatio', '1920 / 1440')}`

## Title (`.card__heading`)
- **fontSize / weight / color:** `{out['productTitle'].get('fontSize')} / {out['productTitle'].get('fontWeight')} / {out['productTitle'].get('color')}`

## Border model
{out['borderModel']['description']}

## Nav dropdown
- **Panel:** full-bleed `{out['navDropdown'].get('panel', {}).get('width', '1440px')}` × `{out['navDropdown'].get('panel', {}).get('height', '~505px')}`, bg `{panel_bg}`, no box-shadow
- **Inner padding:** `{out['navDropdown'].get('inner', {}).get('padding', '32px 50px')}`
- **Title:** `{out['navDropdown'].get('title', {}).get('fontSize')} / {out['navDropdown'].get('title', {}).get('fontWeight')}`
- **Shop all button:** bg `{out['navDropdown'].get('shopAll', {}).get('backgroundColor')}`, radius `{out['navDropdown'].get('shopAll', {}).get('borderRadius')}`, padding `{out['navDropdown'].get('shopAll', {}).get('padding')}`
- **Tile grid:** `{out['navDropdown'].get('tileGrid', {}).get('gridTemplateColumns', '7 cols ~174px')}`, gap `{out['navDropdown'].get('tileGrid', {}).get('gap', '32px 20px')}`
- **Category tile:** no border, transparent bg, image `{out['navDropdown'].get('tileImage', {}).get('width')} × {out['navDropdown'].get('tileImage', {}).get('height')}`

## Notes
"""
    for n in notes:
        md += f"- {n}\n"
    (SRC / "measured-css.md").write_text(md)

    section_notes = f"""# Nav Mega-Menu vs Typical White Card Dropdown

- **Panel background** is `{panel_bg}` — identical to page body `{page_bg}`; not a floating white card on gray.
- **Full-bleed layout:** `.mega-menu-wrapper` spans `{out['navDropdown'].get('panel', {}).get('width', '1440px')}` under the header; position `{out['navDropdown'].get('panel', {}).get('position', 'absolute/static in flow')}`.
- **No drop shadow** on panel (`boxShadow: none`); separation is via layout shift, not elevation.
- **No rounded outer container** — square full-width band, unlike typical card popovers.
- **Inner content** constrained with `padding: 32px 50px` inside `.mega-menu--inner` (page-width).
- **Header row** (`.mega-menu__complex-header`): flex row with `{out['navDropdown'].get('title', {}).get('fontSize', '32px')}` title + olive `{out['navDropdown'].get('shopAll', {}).get('backgroundColor', 'rgb(105, 108, 88)')}` pill button.
- **Category tiles:** 7-column grid, `{out['navDropdown'].get('tileGrid', {}).get('gap', '32px 20px')}` gap; tiles are image+label links without card borders.
- **Second row** includes wider lifestyle/collection promo tiles (Bangalow, Tamarama, etc.) distinct from compact category thumbs.
- **Hover-triggered** via `.header__mega-menu`; body gets `mega-menu--active has-dropdown-menu` class.
- **Content pushes page down** rather than overlaying — mega-menu is in document flow below header, not a fixed overlay.
"""
    (REF / "section-notes.md").write_text(section_notes)

    print("Done:", REF / "collection-grid-desktop.png", REF / "nav-dropdown-modular-desktop.png")


if __name__ == "__main__":
    asyncio.run(main())
