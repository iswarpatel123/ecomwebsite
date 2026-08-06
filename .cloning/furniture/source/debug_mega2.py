#!/usr/bin/env python3
import asyncio, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
from clone_workflow.extractor import PlaywrightExtractor

MEGA = open(ROOT/".cloning/furniture/source/debug_mega.py").read().split("MEGA = r")[1].split('"""')[1]  # reuse

async def main():
    async with PlaywrightExtractor(headless=True) as ext:
        page = await ext._browser.new_page(viewport={"width": 1440, "height": 900})
        await page.goto("https://us.koala.com/", wait_until="load", timeout=120000)
        await page.wait_for_timeout(4000)
        await ext.dismiss_page_popups(page)

        # List mega menu structure
        structure = await page.evaluate("""() => ({
          megas: [...document.querySelectorAll('.header__mega-menu, [class*="mega-menu"]')].slice(0,5).map(el => ({
            cls: String(el.className).slice(0,120),
            rect: el.getBoundingClientRect(),
            html: el.outerHTML.slice(0, 300),
          })),
          modular: [...document.querySelectorAll('header *')].filter(el => /Modular Sofas/.test(el.textContent||'') && el.children.length < 3).slice(0,5).map(el => ({
            tag: el.tagName, cls: String(el.className).slice(0,100),
            rect: el.getBoundingClientRect(), visible: el.getBoundingClientRect().width > 0,
            parent: el.parentElement?.tagName + '.' + String(el.parentElement?.className||'').slice(0,60),
          })),
        })""")
        print("STRUCT", json.dumps(structure, indent=2))

        for sel in [
            '.header__mega-menu',
            'li:has(.title__modular-sofas)',
            'header details',
            'summary:has(.title__modular-sofas)',
            '.title__modular-sofas',
        ]:
            loc = page.locator(sel).first
            c = await loc.count()
            if c == 0:
                print(f"none {sel}")
                continue
            bb = await loc.bounding_box()
            vis = await loc.is_visible()
            print(f"sel {sel} count={c} visible={vis} bb={bb}")
            if bb and vis:
                await page.mouse.move(bb["x"] + bb["width"]/2, bb["y"] + bb["height"]/2)
                await page.wait_for_timeout(1500)
                panel_vis = await page.evaluate("""() => {
                  const p = document.querySelector('.mega-menu__content, .mega-menu');
                  return p ? {rect: p.getBoundingClientRect(), display: getComputedStyle(p).display, opacity: getComputedStyle(p).opacity} : null;
                }""")
                print("panel after hover", panel_vis)
                if panel_vis and panel_vis['rect']['height'] > 50:
                    break

        # JS open via class/details
        await page.evaluate("""() => {
          const d = document.querySelector('.header__mega-menu details, header details');
          if (d) { d.open = true; d.setAttribute('open',''); }
          const m = document.querySelector('.header__mega-menu');
          if (m) m.classList.add('mega-menu--open', 'is-open', 'open');
          const trigger = document.querySelector('.title__modular-sofas')?.closest('summary, .header__menu-item, li');
          if (trigger) {
            trigger.dispatchEvent(new MouseEvent('mouseenter', {bubbles:true}));
            trigger.dispatchEvent(new MouseEvent('mouseover', {bubbles:true}));
          }
        }""")
        await page.wait_for_timeout(1000)

        data = await page.evaluate("""() => {
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
              rect: el.getBoundingClientRect(),
            };
          };
          const panel = [...document.querySelectorAll('[class*="mega-menu"]')].sort((a,b)=>b.getBoundingClientRect().height-a.getBoundingClientRect().height)[0];
          const headerRow = document.querySelector('.mega-menu__complex-header');
          const tileGrid = document.querySelector('.mega-menu__complex-list');
          const tiles = [...document.querySelectorAll('.mega-menu__complex-item')];
          return {
            pageBg: pick(document.body)?.bg,
            panel: pick(panel),
            headerRow: pick(headerRow),
            title: pick(headerRow?.querySelector('h2, .mega-menu__title, p')),
            shopAll: pick(headerRow?.querySelector('.button, a.button')),
            tileGrid: pick(tileGrid),
            tile: pick(tiles[0]),
            tileImg: pick(tiles[0]?.querySelector('img')),
            tileLabel: pick(tiles[0]?.querySelector('.mega-menu__complex-item-title, span, p')),
            lifestyleTile: pick(tiles.find(t => t.getBoundingClientRect().width > 180)),
            tileCount: tiles.length,
          };
        }""")
        print("DATA", json.dumps(data, indent=2))
        await page.screenshot(path=str(ROOT/".cloning/furniture/reference/nav-dropdown-modular-desktop.png"))
        await page.close()

asyncio.run(main())
