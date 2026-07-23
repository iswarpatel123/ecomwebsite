"""Standalone Playwright page extraction.

Adapted from ``Perfect-Web-Clone/backend/extractor/extractor_service.py``.
The web application service, cache endpoints, network API and theme UI are
intentionally omitted; this module only produces a portable extraction JSON
for the clone workspace.

Playwright is imported lazily so source-query and contract helpers remain
usable in environments that do not have browser binaries installed.
"""

from __future__ import annotations

import asyncio
import base64
import json
import logging
import re
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
from urllib.parse import urljoin

from .common import default_viewports
from .models import (
    AssetInfo,
    CSSData,
    ElementInfo,
    ElementRect,
    ElementStyles,
    ExtractionResult,
    InteractionData,
    InteractionState,
    PageAssets,
    PageMetadata,
    StyleSummary,
    StylesheetContent,
)

logger = logging.getLogger(__name__)


@dataclass
class ExtractOptions:
    """Options for one page/viewport extraction."""

    viewport_width: int = 1440
    viewport_height: int = 900
    wait_for_selector: Optional[str] = None
    wait_timeout_ms: int = 30_000
    wait_after_load_ms: int = 1_500
    include_screenshot: bool = True
    full_page_screenshot: bool = False
    screenshot_path: Optional[str] = None
    max_depth: int = 50
    include_hidden: bool = False
    extract_css: bool = True
    capture_interactions: bool = True
    scroll_step: int = 800
    scroll_pause_ms: int = 100
    # Dismiss cookie/email/promo overlays before screenshot and DOM capture.
    dismiss_popups: bool = True
    # Prefer largest srcset candidate when collecting image URLs.
    prefer_largest_srcset: bool = True


STYLE_PROPERTIES = [
    "display", "position", "float", "flexDirection", "flexWrap",
    "justifyContent", "alignItems", "gap", "gridTemplateColumns",
    "gridTemplateRows", "width", "height", "margin", "padding",
    "backgroundColor", "backgroundImage", "color", "border",
    "borderRadius", "boxShadow", "opacity", "overflow", "visibility",
    "fontFamily", "fontSize", "fontWeight", "lineHeight", "textAlign",
    "transform",
]


_DOM_SCRIPT = r"""
([maxDepth, includeHidden, styleProperties]) => {
  const skip = new Set(['SCRIPT', 'STYLE', 'META', 'LINK', 'NOSCRIPT', 'TEMPLATE']);
  const selectorFor = (el) => {
    if (el.id) return `#${CSS.escape(el.id)}`;
    let value = el.tagName.toLowerCase();
    if (typeof el.className === 'string') {
      const cls = el.className.trim().split(/\s+/).find(Boolean);
      if (cls) value += `.${CSS.escape(cls)}`;
    }
    return value;
  };
  const xpathFor = (el) => {
    const parts = [];
    let current = el;
    while (current && current.nodeType === 1 && current !== document.documentElement) {
      let index = 1;
      let sibling = current.previousElementSibling;
      while (sibling) {
        if (sibling.tagName === current.tagName) index++;
        sibling = sibling.previousElementSibling;
      }
      parts.unshift(`${current.tagName.toLowerCase()}[${index}]`);
      current = current.parentElement;
    }
    return '/' + parts.join('/');
  };
  const cleanText = (el) => {
    const direct = Array.from(el.childNodes)
      .filter((n) => n.nodeType === Node.TEXT_NODE)
      .map((n) => n.textContent || '')
      .join(' ').replace(/\s+/g, ' ').trim();
    return direct || null;
  };
  const walk = (el, depth) => {
    if (!el || depth > maxDepth || skip.has(el.tagName)) return null;
    const rect = el.getBoundingClientRect();
    const styles = getComputedStyle(el);
    const visible = styles.display !== 'none' && styles.visibility !== 'hidden' &&
      parseFloat(styles.opacity || '1') > 0 && (rect.width > 0 || rect.height > 0);
    if (!includeHidden && !visible && depth > 0) return null;
    const styleObject = {};
    for (const property of styleProperties) {
      const key = property.replace(/[A-Z]/g, (m) => '_' + m.toLowerCase());
      styleObject[key] = styles[property] || null;
    }
    const attrs = {};
    for (const attr of Array.from(el.attributes)) {
      if (['id', 'class', 'style'].includes(attr.name)) continue;
      if (['href', 'src', 'srcset', 'alt', 'role', 'name', 'type', 'aria-label'].includes(attr.name) || attr.name.startsWith('data-')) {
        attrs[attr.name] = attr.value;
      }
    }
    const children = [];
    if (depth < maxDepth) {
      for (const child of Array.from(el.children)) {
        const result = walk(child, depth + 1);
        if (result) children.push(result);
      }
    }
    const raw = el.innerHTML || '';
    const reduced = raw.replace(/data:image\/[^"]+/gi, '[data-image]')
      .replace(/<svg[\s\S]*?<\/svg>/gi, '<svg>[svg]</svg>');
    return {
      tag: el.tagName.toLowerCase(), id: el.id || null,
      classes: typeof el.className === 'string' ? el.className.trim().split(/\s+/).filter(Boolean) : [],
      rect: { x: rect.left, y: rect.top + window.scrollY, width: rect.width, height: rect.height,
        top: rect.top + window.scrollY, right: rect.right, bottom: rect.bottom + window.scrollY, left: rect.left },
      styles: styleObject, text_content: cleanText(el), inner_html_length: reduced.length,
      raw_html_length: raw.length, attributes: attrs, is_visible: visible,
      is_interactive: /^(a|button|input|select|textarea|summary)$/i.test(el.tagName) ||
        el.hasAttribute('onclick') || el.getAttribute('role') === 'button',
      children, children_count: el.children.length, xpath: xpathFor(el), selector: selectorFor(el)
    };
  };
  return walk(document.documentElement, 0);
}
"""

_ASSET_SCRIPT = r"""
([preferLargestSrcset]) => {
  const result = { images: [], scripts: [], stylesheets: [], fonts: [], image_usages: [] };
  const abs = (u) => {
    try { return new URL(u, document.baseURI).href; } catch (_) { return null; }
  };
  const selectorFor = (el) => {
    if (el.id) return `#${CSS.escape(el.id)}`;
    let value = el.tagName.toLowerCase();
    if (typeof el.className === 'string') {
      const cls = el.className.trim().split(/\s+/).find(Boolean);
      if (cls) value += `.${CSS.escape(cls)}`;
    }
    return value;
  };
  const xpathFor = (el) => {
    const parts = [];
    let current = el;
    while (current && current.nodeType === 1 && current !== document.documentElement) {
      let index = 1;
      let sibling = current.previousElementSibling;
      while (sibling) {
        if (sibling.tagName === current.tagName) index++;
        sibling = sibling.previousElementSibling;
      }
      parts.unshift(`${current.tagName.toLowerCase()}[${index}]`);
      current = current.parentElement;
    }
    return '/' + parts.join('/');
  };
  const sectionHint = (el) => {
    let cur = el;
    while (cur && cur !== document.body) {
      const tag = (cur.tagName || '').toLowerCase();
      const id = (cur.id || '').toLowerCase();
      const cls = (typeof cur.className === 'string' ? cur.className : '').toLowerCase();
      const hay = `${tag} ${id} ${cls}`;
      if (tag === 'header' || /header|masthead|top-?nav|navbar|site-nav/.test(hay)) return 'header-nav';
      if (tag === 'footer' || /footer/.test(hay)) return 'footer';
      if (/360|spin|rotate-view/.test(hay)) return '360-view';
      if (/gallery|thumbnail|media-gallery|product-gallery|pdp-gallery/.test(hay)) return 'gallery';
      if (/hero|banner|jumbotron/.test(hay)) return 'hero';
      if (/testimonial|review|social-proof/.test(hay)) return 'testimonials';
      if (/faq|accordion/.test(hay)) return 'faq';
      if (/feature|benefit|usp/.test(hay)) return 'features';
      if (/product|pdp|buy-box|purchase|add-to-cart|atc/.test(hay)) return 'product';
      if (tag === 'main' || tag === 'section' || tag === 'article') {
        return id || (cls.split(/\s+/).find(Boolean) || tag);
      }
      cur = cur.parentElement;
    }
    return 'page';
  };
  const pickFromSrcset = (srcset) => {
    if (!srcset) return null;
    const parts = srcset.split(',').map((p) => p.trim()).filter(Boolean);
    if (!parts.length) return null;
    let best = null;
    let bestW = -1;
    for (const part of parts) {
      const bits = part.split(/\s+/);
      const u = bits[0];
      let w = 0;
      for (const b of bits.slice(1)) {
        if (b.endsWith('w')) w = parseInt(b, 10) || 0;
        if (b.endsWith('x')) w = Math.round((parseFloat(b) || 1) * 1000);
      }
      if (!preferLargestSrcset) return abs(u);
      if (w >= bestW) { bestW = w; best = u; }
    }
    return abs(best || parts[parts.length - 1].split(/\s+/)[0]);
  };
  const pushImage = (url, type, el) => {
    if (!url || url.startsWith('data:')) return;
    const resolved = abs(url);
    if (!resolved) return;
    const rect = el.getBoundingClientRect();
    const styles = getComputedStyle(el);
    const visible = styles.display !== 'none' && styles.visibility !== 'hidden' &&
      parseFloat(styles.opacity || '1') > 0 && rect.width > 0 && rect.height > 0;
    const area = rect.width * rect.height;
    const usage = {
      url: resolved,
      type,
      selector: selectorFor(el),
      xpath: xpathFor(el),
      alt: el.getAttribute('alt') || el.getAttribute('aria-label') || null,
      role: el.getAttribute('role') || null,
      width: rect.width,
      height: rect.height,
      top: rect.top + window.scrollY,
      left: rect.left + window.scrollX,
      section_hint: sectionHint(el),
      is_visible: visible,
      is_primary: visible && area >= 40000 && rect.top < window.innerHeight * 1.5,
    };
    result.image_usages.push(usage);
    result.images.push({
      url: resolved,
      type,
      selector: usage.selector,
      xpath: usage.xpath,
      alt: usage.alt,
      role: usage.role,
      width: usage.width,
      height: usage.height,
      top: usage.top,
      left: usage.left,
      section_hint: usage.section_hint,
      is_visible: usage.is_visible,
      is_primary: usage.is_primary,
    });
  };

  document.querySelectorAll('img').forEach((el) => {
    const fromSrcset = pickFromSrcset(el.getAttribute('srcset') || el.currentSrc || '');
    const url = fromSrcset || el.currentSrc || el.src || el.getAttribute('src');
    if (url) pushImage(url, 'image', el);
    // Also record srcset candidates as related (not all downloaded by default)
    const ss = el.getAttribute('srcset');
    if (ss) {
      ss.split(',').forEach((part) => {
        const u = abs(part.trim().split(/\s+/)[0]);
        if (u && u !== url) {
          result.images.push({
            url: u, type: 'srcset-candidate', selector: selectorFor(el),
            xpath: xpathFor(el), alt: el.getAttribute('alt'), section_hint: sectionHint(el),
            is_visible: false, is_primary: false,
          });
        }
      });
    }
  });
  document.querySelectorAll('picture source[srcset]').forEach((el) => {
    const url = pickFromSrcset(el.getAttribute('srcset'));
    if (url) pushImage(url, 'picture-source', el.parentElement || el);
  });
  document.querySelectorAll('video[poster]').forEach((el) => {
    if (el.poster) pushImage(el.poster, 'video-poster', el);
  });
  document.querySelectorAll('*').forEach((el) => {
    const image = getComputedStyle(el).backgroundImage || '';
    const match = image.match(/url\(["']?([^"')]+)["']?\)/);
    if (match && !match[1].startsWith('data:')) pushImage(match[1], 'background-image', el);
  });
  document.querySelectorAll('script[src]').forEach((el) => {
    if (el.src) result.scripts.push({ url: el.src, type: 'script' });
  });
  document.querySelectorAll('link[rel="stylesheet"][href]').forEach((el) => {
    if (el.href) result.stylesheets.push({ url: el.href, type: 'stylesheet' });
  });
  for (const sheet of Array.from(document.styleSheets)) {
    try {
      for (const rule of Array.from(sheet.cssRules || [])) {
        if (rule instanceof CSSFontFaceRule) {
          const match = String(rule.style.getPropertyValue('src')).match(/url\(["']?([^"')]+)["']?\)/);
          if (match) result.fonts.push({ url: new URL(match[1], document.baseURI).href, type: 'font' });
        }
      }
    } catch (_) { /* cross-origin stylesheet */ }
  }
  // Dedupe flat image list by url keeping richest usage (primary > visible > first)
  const byUrl = new Map();
  for (const item of result.images) {
    if (!item.url) continue;
    const prev = byUrl.get(item.url);
    if (!prev) { byUrl.set(item.url, item); continue; }
    const score = (x) => (x.is_primary ? 4 : 0) + (x.is_visible ? 2 : 0) + (x.type === 'srcset-candidate' ? -1 : 0);
    if (score(item) > score(prev)) byUrl.set(item.url, item);
  }
  result.images = Array.from(byUrl.values());
  for (const key of ['scripts', 'stylesheets', 'fonts']) {
    const seen = new Set();
    result[key] = result[key].filter((item) => item.url && !seen.has(item.url) && seen.add(item.url));
  }
  return result;
}
"""

# Overlay / cookie / promo dismissors run in-page before capture.
_DISMISS_POPUPS_SCRIPT = r"""
() => {
  const textMatch = (el, patterns) => {
    const t = ((el.innerText || el.textContent || el.getAttribute('aria-label') || '') + '').trim().toLowerCase();
    return patterns.some((p) => t === p || t.includes(p));
  };
  const clickable = Array.from(document.querySelectorAll(
    'button, a, [role="button"], input[type="button"], input[type="submit"], .close, [aria-label], [data-testid], [data-action]'
  ));
  const closePatterns = [
    'accept all', 'accept cookies', 'allow all', 'i agree', 'got it', 'agree',
    'close', 'dismiss', 'no thanks', 'not now', 'maybe later', 'continue',
    'reject all', 'reject non-essential', 'decline', '×', '✕', 'x'
  ];
  let clicked = 0;
  for (const el of clickable) {
    const aria = (el.getAttribute('aria-label') || '').toLowerCase();
    const cls = (typeof el.className === 'string' ? el.className : '').toLowerCase();
    const isClose = /close|dismiss|cookie|consent|accept/.test(aria + ' ' + cls) || textMatch(el, closePatterns);
    if (!isClose) continue;
    const style = getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    if (style.display === 'none' || style.visibility === 'hidden' || rect.width < 1) continue;
    try { el.click(); clicked++; } catch (_) {}
    if (clicked >= 6) break;
  }
  // Hide leftover fixed full-viewport overlays that still block the page
  let hidden = 0;
  for (const el of Array.from(document.querySelectorAll('body *'))) {
    const style = getComputedStyle(el);
    if (style.position !== 'fixed' && style.position !== 'sticky') continue;
    const rect = el.getBoundingClientRect();
    const covers = rect.width >= window.innerWidth * 0.5 && rect.height >= window.innerHeight * 0.4;
    const z = parseInt(style.zIndex || '0', 10);
    if (!covers || z < 10) continue;
    const hay = ((el.id || '') + ' ' + (typeof el.className === 'string' ? el.className : '')).toLowerCase();
    if (/modal|overlay|popup|dialog|consent|cookie|newsletter|email-capture|promo|interstitial/.test(hay) ||
        el.getAttribute('role') === 'dialog' || el.getAttribute('aria-modal') === 'true') {
      el.style.setProperty('display', 'none', 'important');
      el.style.setProperty('visibility', 'hidden', 'important');
      el.style.setProperty('pointer-events', 'none', 'important');
      hidden++;
    }
  }
  document.documentElement.style.overflow = 'auto';
  document.body && (document.body.style.overflow = 'auto');
  return { clicked, hidden };
}
"""

_CSS_SCRIPT = r"""
() => {
  const result = { stylesheets: [], variables: [], media_queries: {} };
  document.querySelectorAll('style').forEach((el, i) => result.stylesheets.push({
    url: `inline-${i}`, content: el.textContent || '', is_inline: true
  }));
  for (const sheet of Array.from(document.styleSheets)) {
    try {
      const rules = sheet.cssRules || [];
      for (const rule of Array.from(rules)) {
        if (rule instanceof CSSMediaRule) result.media_queries[rule.conditionText] = rule.cssText;
        if (rule instanceof CSSStyleRule && [':root', 'html'].includes(rule.selectorText)) {
          for (let i = 0; i < rule.style.length; i++) {
            const name = rule.style[i];
            if (name.startsWith('--')) result.variables.push({ name, value: rule.style.getPropertyValue(name).trim(), scope: rule.selectorText });
          }
        }
      }
    } catch (_) { /* cross-origin stylesheet */ }
  }
  return result;
}
"""


def _require_playwright() -> Any:
    try:
        from playwright.async_api import async_playwright
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "Playwright is required for extraction. Install it with "
            "`python -m pip install playwright` and run `playwright install chromium`."
        ) from exc
    return async_playwright


def _element_from_dict(value: Dict[str, Any]) -> ElementInfo:
    rect = ElementRect(**{k: value.get("rect", {}).get(k, 0) for k in asdict(ElementRect())})
    style_fields = asdict(ElementStyles()).keys()
    raw_styles = value.get("styles", {})
    styles = ElementStyles(**{
        k: raw_styles.get(k, raw_styles.get("float")) if k == "float_" else raw_styles.get(k)
        for k in style_fields
    })
    return ElementInfo(
        tag=value.get("tag", "div"), id=value.get("id"), classes=value.get("classes", []),
        rect=rect, styles=styles, text_content=value.get("text_content"),
        inner_html_length=value.get("inner_html_length", 0), raw_html_length=value.get("raw_html_length", 0),
        attributes=value.get("attributes", {}), is_visible=value.get("is_visible", True),
        is_interactive=value.get("is_interactive", False), children=[_element_from_dict(c) for c in value.get("children", [])],
        children_count=value.get("children_count", 0), xpath=value.get("xpath"), selector=value.get("selector"),
    )


def _asset_group(items: Iterable[Dict[str, Any]]) -> List[AssetInfo]:
    seen: set[str] = set()
    result = []
    for item in items:
        url = item.get("url", "")
        if url and url not in seen:
            seen.add(url)
            result.append(AssetInfo(
                url=url,
                type=item.get("type", "other"),
                size=item.get("size"),
                selector=item.get("selector"),
                xpath=item.get("xpath"),
                alt=item.get("alt"),
                role=item.get("role"),
                width=item.get("width"),
                height=item.get("height"),
                top=item.get("top"),
                left=item.get("left"),
                section_hint=item.get("section_hint"),
                is_visible=item.get("is_visible"),
                is_primary=item.get("is_primary"),
            ))
    return result


def _style_summary(root: Optional[ElementInfo]) -> StyleSummary:
    summary = StyleSummary()
    if not root:
        return summary

    def bump(bucket: Dict[str, int], value: Optional[str]) -> None:
        if value and value not in ("none", "normal", "auto", "0px"):
            bucket[value] = bucket.get(value, 0) + 1

    def walk(node: ElementInfo) -> None:
        s = node.styles
        bump(summary.colors, s.color); bump(summary.background_colors, s.background_color)
        bump(summary.font_families, s.font_family); bump(summary.font_sizes, s.font_size)
        bump(summary.margins, s.margin); bump(summary.paddings, s.padding)
        bump(summary.display_types, s.display); bump(summary.position_types, s.position)
        for child in node.children:
            walk(child)
    walk(root)

    for name in ("colors", "background_colors", "font_families", "font_sizes", "margins", "paddings", "display_types", "position_types"):
        value = getattr(summary, name)
        setattr(summary, name, dict(sorted(value.items(), key=lambda pair: pair[1], reverse=True)[:50]))
    return summary


class PlaywrightExtractor:
    """Reusable browser-backed extractor with no web-server dependencies."""

    def __init__(self, *, headless: bool = True, browser_args: Optional[Sequence[str]] = None) -> None:
        self.headless = headless
        self.browser_args = list(browser_args or ["--no-sandbox", "--disable-dev-shm-usage"])
        self._playwright = None
        self._browser = None

    async def start(self) -> "PlaywrightExtractor":
        if self._browser is None:
            async_playwright = _require_playwright()
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(headless=self.headless, args=self.browser_args)
        return self

    async def close(self) -> None:
        if self._browser is not None:
            await self._browser.close()
            self._browser = None
        if self._playwright is not None:
            await self._playwright.stop()
            self._playwright = None

    async def __aenter__(self) -> "PlaywrightExtractor":
        return await self.start()

    async def __aexit__(self, *_: Any) -> None:
        await self.close()

    async def extract(self, url: str, options: Optional[ExtractOptions] = None) -> ExtractionResult:
        options = options or ExtractOptions()
        started = time.monotonic()
        try:
            await self.start()
            page = await self._browser.new_page(viewport={"width": options.viewport_width, "height": options.viewport_height})
            try:
                await page.goto(url, wait_until="load", timeout=60_000)
                await page.wait_for_timeout(options.wait_after_load_ms)
                if options.wait_for_selector:
                    await page.wait_for_selector(options.wait_for_selector, timeout=options.wait_timeout_ms)
                if options.dismiss_popups:
                    await self.dismiss_page_popups(page)
                await self._scroll_to_load_lazy_content(page, options)
                # Popups often reappear after scroll; dismiss again before capture.
                if options.dismiss_popups:
                    await self.dismiss_page_popups(page)

                info = await page.evaluate("""() => ({
                    title: document.title, viewport_width: innerWidth, viewport_height: innerHeight,
                    page_width: document.documentElement.scrollWidth, page_height: document.documentElement.scrollHeight,
                    total_elements: document.querySelectorAll('*').length
                })""")
                max_depth = await page.evaluate("""() => {
                    const depth = (el, n) => !el.children.length ? n : Math.max(...Array.from(el.children).map(c => depth(c, n + 1)));
                    return depth(document.body, 1);
                }""")
                tree_value = await page.evaluate(_DOM_SCRIPT, [options.max_depth, options.include_hidden, STYLE_PROPERTIES])
                dom_tree = _element_from_dict(tree_value) if tree_value else None
                raw_html = await page.content()
                assets_value = await page.evaluate(
                    _ASSET_SCRIPT, [options.prefer_largest_srcset]
                )
                assets = PageAssets(
                    images=_asset_group(assets_value.get("images", [])),
                    scripts=_asset_group(assets_value.get("scripts", [])),
                    stylesheets=_asset_group(assets_value.get("stylesheets", [])),
                    fonts=_asset_group(assets_value.get("fonts", [])),
                    image_usages=list(assets_value.get("image_usages") or []),
                )
                css_data = await self._extract_css(page, assets, options.extract_css)
                interactions = await self._extract_interactions(page) if options.capture_interactions else None

                screenshot_path = None
                if options.include_screenshot:
                    if options.screenshot_path:
                        screenshot_path = str(Path(options.screenshot_path))
                        Path(screenshot_path).parent.mkdir(parents=True, exist_ok=True)
                        await page.screenshot(path=screenshot_path, full_page=options.full_page_screenshot)
                    else:
                        # Keep the result JSON-safe while retaining the original service's screenshot capability.
                        screenshot = await page.screenshot(type="png", full_page=options.full_page_screenshot)
                        screenshot_path = "data:image/png;base64," + base64.b64encode(screenshot).decode("ascii")

                metadata = PageMetadata(
                    url=url, title=info.get("title", ""), viewport_width=info.get("viewport_width", options.viewport_width),
                    viewport_height=info.get("viewport_height", options.viewport_height), page_width=info.get("page_width", 0),
                    page_height=info.get("page_height", 0), total_elements=info.get("total_elements", 0),
                    max_depth=max_depth, load_time_ms=int((time.monotonic() - started) * 1000),
                )
                return ExtractionResult(True, "Extraction succeeded", metadata, dom_tree, _style_summary(dom_tree), assets, raw_html, css_data, interactions, screenshot_path)
            finally:
                await page.close()
        except Exception as exc:
            logger.exception("Extraction failed for %s", url)
            return ExtractionResult(False, "Extraction failed", error=str(exc))

    async def extract_many(self, url: str, viewports: Optional[Sequence[Tuple[str, int, int]]] = None, output_dir: Optional[str] = None, **kwargs: Any) -> Dict[str, ExtractionResult]:
        """Extract desktop/tablet/mobile (or any supplied viewport set).

        The default set is intentionally identical to the repository clone
        contract.  Results retain raw HTML and CSS in memory; callers can
        serialize ``ExtractionResult.to_dict()`` into ``source/``.
        """
        supplied = viewports or [(item.name, item.width, item.height) for item in default_viewports()]
        results: Dict[str, ExtractionResult] = {}
        for name, width, height in supplied:
            options = ExtractOptions(viewport_width=width, viewport_height=height, **kwargs)
            if output_dir and options.include_screenshot:
                options.screenshot_path = str(Path(output_dir) / f"{name}.png")
            results[name] = await self.extract(url, options)
        return results

    async def _scroll_to_load_lazy_content(self, page: Any, options: ExtractOptions) -> None:
        last_height = 0
        for _ in range(80):
            height = await page.evaluate("() => document.documentElement.scrollHeight")
            if height == last_height:
                break
            last_height = height
            await page.evaluate("step => window.scrollBy(0, step)", options.scroll_step)
            await page.wait_for_timeout(options.scroll_pause_ms)
        await page.evaluate("() => window.scrollTo(0, 0)")

    async def _extract_css(self, page: Any, assets: PageAssets, enabled: bool) -> Optional[CSSData]:
        if not enabled:
            return None
        value = await page.evaluate(_CSS_SCRIPT)
        stylesheets = [StylesheetContent(**s) for s in value.get("stylesheets", [])]
        for sheet in assets.stylesheets:
            try:
                response = await page.request.get(sheet.url)
                if response.ok:
                    stylesheets.append(StylesheetContent(sheet.url, await response.text(), False))
            except Exception:
                logger.debug("Could not read stylesheet %s", sheet.url)
        return CSSData(stylesheets=stylesheets, variables=value.get("variables", []), media_queries=value.get("media_queries", {}))

    async def _extract_interactions(self, page: Any) -> InteractionData:
        targets = await page.locator("a, button, input, select, textarea, [role='button']").all()
        result = InteractionData()
        for target in targets[:60]:
            try:
                selector = await target.evaluate("el => el.id ? '#' + el.id : el.tagName.toLowerCase()")
                await target.hover(timeout=500)
                hover = await target.evaluate("""el => { const s = getComputedStyle(el); return { color:s.color, background_color:s.backgroundColor, border:s.border, box_shadow:s.boxShadow, transform:s.transform, opacity:s.opacity }; }""")
                result.hover_states.append(InteractionState(selector, "hover", {k: v for k, v in hover.items() if v and v not in ("none", "normal")}))
                await target.focus(timeout=500)
                focus = await target.evaluate("""el => { const s = getComputedStyle(el); return { color:s.color, background_color:s.backgroundColor, border:s.border, box_shadow:s.boxShadow, outline:s.outline }; }""")
                result.focus_states.append(InteractionState(selector, "focus", {k: v for k, v in focus.items() if v and v not in ("none", "normal")}))
            except Exception:
                continue
        return result

    async def dismiss_page_popups(self, page: Any) -> Dict[str, Any]:
        """Dismiss cookie banners, email capture, and promo modals on *page*.

        Order: Escape key, common close/accept clicks, then hide residual
        full-viewport fixed overlays so screenshots are not blurred/blocked.
        """
        report: Dict[str, Any] = {"escape": False, "clicked": 0, "hidden": 0, "errors": []}
        try:
            await page.keyboard.press("Escape")
            report["escape"] = True
            await page.wait_for_timeout(200)
        except Exception as exc:
            report["errors"].append(f"escape: {exc}")
        # Prefer Playwright locators for common cookie/consent buttons.
        locator_labels = [
            "Accept all", "Accept All", "Accept cookies", "Allow all", "I agree",
            "Got it", "Agree", "Close", "No thanks", "Not now", "Reject all",
            "Decline", "Continue",
        ]
        for label in locator_labels:
            try:
                loc = page.get_by_role("button", name=re.compile(rf"^{re.escape(label)}$", re.I))
                if await loc.count() > 0:
                    await loc.first.click(timeout=800)
                    report["clicked"] += 1
                    await page.wait_for_timeout(150)
            except Exception:
                pass
            try:
                loc = page.locator(
                    f'button:has-text("{label}"), [role="button"]:has-text("{label}"), '
                    f'a:has-text("{label}")'
                )
                if await loc.count() > 0:
                    await loc.first.click(timeout=800)
                    report["clicked"] += 1
                    await page.wait_for_timeout(150)
            except Exception:
                pass
        try:
            close_btns = page.locator(
                '[aria-label*="close" i], [aria-label*="dismiss" i], button.close, '
                '.modal [class*="close" i], [data-testid*="close" i]'
            )
            count = await close_btns.count()
            for i in range(min(count, 4)):
                try:
                    await close_btns.nth(i).click(timeout=500)
                    report["clicked"] += 1
                except Exception:
                    continue
        except Exception as exc:
            report["errors"].append(f"close_btns: {exc}")
        try:
            await page.keyboard.press("Escape")
        except Exception:
            pass
        try:
            inpage = await page.evaluate(_DISMISS_POPUPS_SCRIPT)
            report["clicked"] += int(inpage.get("clicked") or 0)
            report["hidden"] += int(inpage.get("hidden") or 0)
        except Exception as exc:
            report["errors"].append(f"inpage: {exc}")
        await page.wait_for_timeout(300)
        return report

    async def close_popup(self, page: Optional[Any] = None) -> bool:
        """Try to close popups on the given page (or last open page)."""
        try:
            target = page or await self._first_page()
            if target is None:
                return False
            report = await self.dismiss_page_popups(target)
            return bool(report.get("clicked") or report.get("hidden") or report.get("escape"))
        except Exception:
            return False

    async def dismiss_modal(self, page: Optional[Any] = None) -> bool:
        """Dismiss modal via Escape + overlay hide on the given page."""
        return await self.close_popup(page)

    async def click_button(self, selector: str, page: Optional[Any] = None) -> bool:
        """Click a button by selector on the given page."""
        try:
            target = page or await self._first_page()
            if target is None:
                return False
            await target.locator(selector).first.click(timeout=2_000)
            return True
        except Exception:
            return False

    async def _first_page(self) -> Optional[Any]:
        if self._browser is None:
            return None
        for context in self._browser.contexts:
            pages = context.pages
            if pages:
                return pages[0]
        return None


async def extract_url(url: str, options: Optional[ExtractOptions] = None, **kwargs: Any) -> ExtractionResult:
    """Convenience function for agents and direct Python callers."""
    async with PlaywrightExtractor(**kwargs) as extractor:
        return await extractor.extract(url, options)


async def extract_responsive(
    url: str,
    output_dir: Optional[str] = None,
    *,
    viewports: Optional[Sequence[Tuple[str, int, int]]] = None,
    **kwargs: Any,
) -> Dict[str, ExtractionResult]:
    """Extract all required responsive viewports with one browser lifecycle."""
    async with PlaywrightExtractor(**kwargs) as extractor:
        return await extractor.extract_many(url, viewports, output_dir, **kwargs.pop("extract_options", {}))


def _script_entry() -> None:
    """Small direct-module entry point; this is not a repository-level CLI."""
    import argparse
    parser = argparse.ArgumentParser(description="Extract one URL to JSON")
    parser.add_argument("url")
    parser.add_argument("--output", required=True)
    parser.add_argument("--width", type=int, default=1440)
    parser.add_argument("--height", type=int, default=900)
    args = parser.parse_args()
    result = asyncio.run(extract_url(args.url, ExtractOptions(args.width, args.height)))
    Path(args.output).write_text(json.dumps(result.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    if not result.success:
        raise SystemExit(result.error or result.message)


if __name__ == "__main__":
    _script_entry()
