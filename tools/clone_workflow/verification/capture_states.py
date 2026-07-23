#!/usr/bin/env python3
"""Capture responsive reference screenshots and interaction-state snapshots.

This is deliberately a small Playwright script rather than a new CLI framework.
It captures a baseline at each viewport, then attempts hover/focus/active states,
ARIA-expanded toggles, and a theme toggle when the page exposes one. A failed
individual state is recorded and does not prevent other viewports from running.

Example:
  python tools/clone_workflow/verification/capture_states.py \
    --url https://example.test --slug furniture \
    --viewports desktop=1440x900,tablet=768x1024,mobile=390x844
"""

from __future__ import annotations

import argparse
import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
import re
import sys
from typing import Any

try:
    from .common import default_viewports, parse_viewport, resolve_workspace
except ImportError:  # direct ``python path/to/capture_states.py`` invocation
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from common import default_viewports, parse_viewport, resolve_workspace  # type: ignore


INTERACTIVE_JS = """
() => {
  const visible = el => { const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0 && getComputedStyle(el).visibility !== 'hidden'; };
  const cssPath = el => {
    if (el.id) return '#' + CSS.escape(el.id);
    const parts = [];
    while (el && el.nodeType === 1 && el !== document.body) {
      let part = el.tagName.toLowerCase();
      if (el.getAttribute('data-testid')) part += '[data-testid="' + CSS.escape(el.getAttribute('data-testid')) + '"]';
      const parent = el.parentElement;
      if (parent) {
        const siblings = [...parent.children].filter(x => x.tagName === el.tagName);
        if (siblings.length > 1) part += ':nth-of-type(' + (siblings.indexOf(el) + 1) + ')';
      }
      parts.unshift(part); el = parent;
    }
    return parts.join(' > ') || 'body';
  };
  const nodes = [...document.querySelectorAll('a,button,input,select,textarea,summary,[role="button"],[tabindex]')];
  return nodes.filter(visible).slice(0, 40).map((el, index) => ({
    selector: cssPath(el), index, tag: el.tagName.toLowerCase(),
    label: (el.getAttribute('aria-label') || el.textContent || el.getAttribute('name') || '').trim().slice(0, 60),
    expanded: el.getAttribute('aria-expanded'),
  }));
}
"""

SNAPSHOT_JS = """
() => {
  const cssPath = el => {
    if (el.id) return '#' + CSS.escape(el.id);
    const parts = [];
    while (el && el.nodeType === 1 && el !== document.body) {
      let part = el.tagName.toLowerCase();
      const parent = el.parentElement;
      if (parent) {
        const siblings = [...parent.children].filter(x => x.tagName === el.tagName);
        if (siblings.length > 1) part += ':nth-of-type(' + (siblings.indexOf(el) + 1) + ')';
      }
      parts.unshift(part); el = parent;
    }
    return parts.join(' > ') || 'body';
  };
  const interesting = ['display','position','width','height','color','backgroundColor','fontSize',
    'fontWeight','lineHeight','marginTop','marginRight','marginBottom','marginLeft','paddingTop',
    'paddingRight','paddingBottom','paddingLeft','borderRadius','opacity','transform',
    'transitionDuration','visibility'];
  const elements = [...document.querySelectorAll('*')].slice(0, 5000).map(el => {
    const style = getComputedStyle(el); const attributes = {};
    for (const attr of el.attributes) {
      if (attr.name === 'class' || attr.name === 'id' || attr.name.startsWith('aria-') ||
          ['role','tabindex','type','name','alt','for','disabled','hidden','open'].includes(attr.name))
        attributes[attr.name] = attr.value;
    }
    const computed = {}; for (const key of interesting) computed[key] = style[key];
    return {selector: cssPath(el), tag: el.tagName.toLowerCase(), attributes, classCount: (el.className && typeof el.className === 'string') ? el.className.trim().split(/\\s+/).filter(Boolean).length : 0, computed};
  });
  return {url: location.href, title: document.title, capturedAt: new Date().toISOString(), elements};
}
"""


def _slug_state(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")[:80] or "state"


async def _wait_ready(page: Any, wait_ms: int) -> None:
    await page.wait_for_timeout(wait_ms)
    try:
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(250)
        await page.evaluate("window.scrollTo(0, 0)")
    except Exception:
        pass


async def _write_state(page: Any, state_dir: Path, state: str, *, full_page: bool = False) -> dict[str, str]:
    state = _slug_state(state)
    png = state_dir / f"{state}.png"
    html = state_dir / f"{state}.html"
    computed = state_dir / f"{state}.json"
    await page.screenshot(path=str(png), full_page=full_page)
    html.write_text(await page.content(), encoding="utf-8")
    computed.write_text(json.dumps(await page.evaluate(SNAPSHOT_JS), indent=2), encoding="utf-8")
    return {"state": state, "screenshot": str(png), "html": str(html), "computed": str(computed)}


async def _capture_interactions(page: Any, state_dir: Path, max_elements: int, wait_ms: int) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    elements = (await page.evaluate(INTERACTIVE_JS))[:max_elements]
    for item in elements:
        selector = item["selector"]
        label = _slug_state(item.get("label") or item.get("tag") or "element")
        ordinal = f"{int(item['index']):03d}"
        try:
            locator = page.locator(selector).first
            if await locator.count() == 0:
                continue
            await locator.hover(timeout=1500)
            await page.wait_for_timeout(wait_ms)
            records.append(await _write_state(page, state_dir, f"hover-{ordinal}-{label}", full_page=False))

            await locator.focus(timeout=1500)
            await page.wait_for_timeout(wait_ms)
            records.append(await _write_state(page, state_dir, f"focus-{ordinal}-{label}", full_page=False))

            await locator.hover(timeout=1500)
            await page.mouse.down()
            await page.wait_for_timeout(wait_ms)
            records.append(await _write_state(page, state_dir, f"active-{ordinal}-{label}", full_page=False))
            await page.mouse.up()
        except Exception:
            # Cross-origin navigation, detached nodes, and non-focusable controls
            # are normal on real sites; continue with the remaining controls.
            try:
                await page.mouse.up()
            except Exception:
                pass
    return records


async def _capture_toggles(page: Any, state_dir: Path, max_elements: int, wait_ms: int) -> list[dict[str, str]]:
    """Capture safe, reversible disclosure controls and theme buttons."""
    records: list[dict[str, str]] = []
    candidates = await page.locator(
        '[aria-expanded="false"], details:not([open]), button, [role="button"]'
    ).all()
    count = 0
    for locator in candidates:
        if count >= max_elements:
            break
        try:
            if not await locator.is_visible():
                continue
            text = ((await locator.get_attribute("aria-label")) or (await locator.inner_text()) or "").strip()
            expanded = await locator.get_attribute("aria-expanded")
            details = await locator.evaluate("el => el.tagName.toLowerCase() === 'summary'")
            is_theme = bool(re.search(r"dark|theme|light mode|colour|color mode", text, re.I))
            if expanded != "false" and not details and not is_theme:
                continue
            count += 1
            label = _slug_state(text or "toggle")
            await locator.click(timeout=1500)
            await page.wait_for_timeout(wait_ms)
            records.append(await _write_state(page, state_dir, f"{'theme' if is_theme else 'toggle'}-open-{count:03d}-{label}"))
            # Click again where possible so this state is explicit and reversible.
            try:
                await locator.click(timeout=1500)
                await page.wait_for_timeout(wait_ms)
                records.append(await _write_state(page, state_dir, f"{'theme' if is_theme else 'toggle'}-closed-{count:03d}-{label}"))
            except Exception:
                pass
        except Exception:
            continue
    return records


async def capture_reference(args: argparse.Namespace) -> int:
    try:
        from playwright.async_api import async_playwright
    except ImportError as exc:
        raise RuntimeError("capture_states.py requires Python Playwright; install it with 'python -m pip install playwright' and run 'playwright install chromium'") from exc

    paths = resolve_workspace(args.slug, args.root)
    viewports = [parse_viewport(v, ["desktop", "tablet", "mobile"][i] if i < 3 else None)
                 for i, v in enumerate(args.viewports.split(","))] if args.viewports else default_viewports()
    requested = {s.strip().lower() for s in args.states.split(",") if s.strip()}
    manifest: dict[str, Any] = {
        "url": args.url, "slug": args.slug, "generatedAt": datetime.now(timezone.utc).isoformat(),
        "viewports": [], "notes": "Reference-only captures; state failures are retained in errors.",
    }
    async with async_playwright() as playwright:
        browser_args = {"headless": not args.headed}
        if args.proxy:
            browser_args["proxy"] = {"server": args.proxy}
        browser = await playwright.chromium.launch(**browser_args)
        try:
            for viewport in viewports:
                state_dir = paths["reference"] / "states" / viewport.name
                state_dir.mkdir(parents=True, exist_ok=True)
                page = await browser.new_page(viewport={"width": viewport.width, "height": viewport.height}, color_scheme=args.color_scheme)
                entry: dict[str, Any] = {"name": viewport.name, "width": viewport.width, "height": viewport.height, "states": [], "errors": []}
                try:
                    await page.goto(args.url, wait_until="load", timeout=args.timeout)
                    await _wait_ready(page, args.wait)
                    # Keep the flat baseline names compatible with the existing TS tooling.
                    top = paths["reference"] / f"{args.slug}-{viewport.name}-top.png"
                    full = paths["reference"] / f"{args.slug}-{viewport.name}.png"
                    if "baseline" in requested or "top" in requested:
                        await page.evaluate("window.scrollTo(0, 0)")
                        await page.screenshot(path=str(top), full_page=False)
                        entry["states"].append(await _write_state(page, state_dir, "baseline-top"))
                    if "baseline" in requested or "full" in requested:
                        await page.screenshot(path=str(full), full_page=True)
                        entry["states"].append(await _write_state(page, state_dir, "baseline-full", full_page=True))
                    if "hover" in requested or "focus" in requested or "active" in requested:
                        entry["states"].extend(await _capture_interactions(page, state_dir, args.max_elements, args.state_wait))
                    if "toggles" in requested or "theme" in requested:
                        entry["states"].extend(await _capture_toggles(page, state_dir, args.max_elements, args.state_wait))
                except Exception as exc:
                    entry["errors"].append(str(exc))
                finally:
                    await page.close()
                manifest["viewports"].append(entry)
        finally:
            await browser.close()
    (paths["reference"] / "capture-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"[capture-states] wrote reference captures to {paths['reference']}")
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--url", required=True)
    result.add_argument("--slug", required=True)
    result.add_argument("--viewports", default="", help="CSV of WIDTHxHEIGHT or NAME=WIDTHxHEIGHT")
    result.add_argument("--states", default="baseline,hover,focus,active,toggles", help="baseline, hover, focus, active, toggles, theme")
    result.add_argument("--root", help="monorepo root (defaults to nearest pnpm-workspace.yaml)")
    result.add_argument("--proxy")
    result.add_argument("--timeout", type=int, default=60000)
    result.add_argument("--wait", type=int, default=1500, help="milliseconds to wait after page load")
    result.add_argument("--state-wait", type=int, default=120)
    result.add_argument("--max-elements", type=int, default=20)
    result.add_argument("--color-scheme", choices=("light", "dark"), default="light")
    result.add_argument("--headed", action="store_true")
    return result


if __name__ == "__main__":
    try:
        raise SystemExit(asyncio.run(capture_reference(parser().parse_args())))
    except Exception as exc:
        print(f"[capture-states] error: {exc}", file=sys.stderr)
        raise SystemExit(1)
