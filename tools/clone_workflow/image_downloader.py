"""Local asset downloader for clone workspaces.

Adapted from ``Perfect-Web-Clone/backend/image_downloader/downloader.py``.
Unlike the original WebContainer integration, this module writes to a normal
filesystem directory and returns a URL-to-local-path manifest.  SVG files are
kept as SVG; raster processing is optional and uses Pillow when installed.
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import logging
from datetime import datetime, timezone
from dataclasses import asdict, dataclass
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


@dataclass
class ImageDownloadConfig:
    output_dir: str = "public/assets"
    public_prefix: str = "/assets"
    max_size_kb: int = 500
    quality: int = 80
    max_width: int = 1200
    max_height: int = 1200
    timeout: float = 15
    max_images: int = 200
    output_format: str = "webp"
    concurrency: int = 8
    include_base64: bool = False


@dataclass
class DownloadedImage:
    original_url: str
    local_path: str = ""
    public_path: str = ""
    base64_data: str = ""
    content_type: str = ""
    original_size: int = 0
    processed_size: int = 0
    width: int = 0
    height: int = 0
    success: bool = False
    error: Optional[str] = None

    # Compatibility aliases for the original downloader's result shape.
    @property
    def compressed_size(self) -> int:
        return self.processed_size


BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
}


def _is_svg(url: str, data: bytes) -> bool:
    if url.lower().split("?", 1)[0].endswith(".svg"):
        return True
    head = data[:500].lstrip().lower()
    return head.startswith(b"<svg") or head.startswith(b"<?xml") or b"<svg" in head


def _filename(url: str, index: int, extension: str) -> str:
    digest = hashlib.md5(url.encode("utf-8")).hexdigest()[:8]
    return f"img-{index:03d}-{digest}.{extension}"


def _compress(data: bytes, url: str, config: ImageDownloadConfig) -> tuple[bytes, int, int, str]:
    if _is_svg(url, data):
        return data, 0, 0, "svg"
    try:
        from PIL import Image
    except ImportError:
        logger.warning("Pillow is not installed; saving raster asset bytes without processing")
        return data, 0, 0, "original"

    with Image.open(BytesIO(data)) as image:
        if image.mode in ("RGBA", "P") and config.output_format in ("jpeg", "jpg"):
            rgba = image.convert("RGBA")
            background = Image.new("RGB", rgba.size, "white")
            background.paste(rgba, mask=rgba.getchannel("A"))
            image = background
        elif image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGB")
        width, height = image.size
        if width > config.max_width or height > config.max_height:
            ratio = min(config.max_width / width, config.max_height / height)
            image = image.resize((max(1, int(width * ratio)), max(1, int(height * ratio))), Image.Resampling.LANCZOS)
        width, height = image.size
        output_format = config.output_format.lower()
        pil_format = {"jpg": "JPEG", "jpeg": "JPEG", "png": "PNG", "webp": "WEBP"}.get(output_format, "WEBP")
        quality = max(10, min(100, config.quality))
        last = b""
        while quality >= 10:
            output = BytesIO()
            kwargs: Dict[str, Any] = {"format": pil_format}
            if pil_format in ("JPEG", "WEBP"):
                kwargs["quality"] = quality
            if pil_format == "WEBP":
                kwargs["method"] = 4
            image.save(output, **kwargs)
            last = output.getvalue()
            if len(last) <= config.max_size_kb * 1024 or quality == 10:
                break
            quality -= 10
        return last, width, height, "jpg" if output_format in ("jpg", "jpeg") else output_format


class ImageDownloader:
    """Download, optionally optimize, and localize a list of image URLs."""

    def __init__(self, config: Optional[ImageDownloadConfig] = None) -> None:
        self.config = config or ImageDownloadConfig()
        self._client = None

    async def _get_client(self) -> Any:
        if self._client is None:
            try:
                import httpx
            except ImportError as exc:
                raise RuntimeError("httpx is required for asset downloads: python -m pip install httpx") from exc
            self._client = httpx.AsyncClient(timeout=self.config.timeout, follow_redirects=True, headers=BROWSER_HEADERS)
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> "ImageDownloader":
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.close()

    async def download_single(self, url: str, index: int) -> DownloadedImage:
        result = DownloadedImage(original_url=url)
        try:
            parsed = urlparse(url)
            if parsed.scheme not in {"http", "https"}:
                raise ValueError(f"Invalid URL scheme: {parsed.scheme or '<empty>'}")
            client = await self._get_client()
            headers = {"Referer": f"{parsed.scheme}://{parsed.netloc}/", "Origin": f"{parsed.scheme}://{parsed.netloc}"}
            response = await client.get(url, headers=headers)
            if response.status_code == 403:
                response = await client.get(url)
            if response.status_code == 403:
                response = await client.get(url, headers={"Referer": ""})
            response.raise_for_status()
            original = response.content
            result.original_size = len(original)
            processed, width, height, extension = _compress(original, url, self.config)
            if extension == "original":
                extension = "bin"
            filename = _filename(url, index, extension)
            output_dir = Path(self.config.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            local_path = output_dir / filename
            local_path.write_bytes(processed)
            result.local_path = str(local_path)
            result.public_path = f"{self.config.public_prefix.rstrip('/')}/{filename}"
            result.processed_size = len(processed)
            result.width = width
            result.height = height
            result.content_type = "image/svg+xml" if extension == "svg" else {
                "webp": "image/webp", "jpg": "image/jpeg", "png": "image/png"
            }.get(extension, response.headers.get("content-type", "application/octet-stream"))
            if self.config.include_base64:
                result.base64_data = base64.b64encode(processed).decode("ascii")
            result.success = True
        except Exception as exc:
            result.error = str(exc)
            logger.warning("Asset download failed for %s: %s", url, exc)
        return result

    async def download_batch(self, urls: Iterable[str]) -> List[DownloadedImage]:
        unique = list(dict.fromkeys(url for url in urls if url))[: self.config.max_images]
        semaphore = asyncio.Semaphore(max(1, self.config.concurrency))

        async def one(index: int, url: str) -> DownloadedImage:
            async with semaphore:
                return await self.download_single(url, index)

        return await asyncio.gather(*(one(i, url) for i, url in enumerate(unique)))

    async def download_manifest(self, urls: Iterable[str], manifest_path: str) -> Dict[str, Any]:
        results = await self.download_batch(urls)
        entries = [asdict(item) for item in results]
        manifest = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "output_dir": self.config.output_dir,
            "public_prefix": self.config.public_prefix,
            "total": len(results),
            "succeeded": sum(item.success for item in results),
            "failed": sum(not item.success for item in results),
            "entries": entries,
            # A direct map makes CSS/HTML URL rewriting deterministic while
            # retaining per-download diagnostics in ``entries``.
            "url_map": {
                item.original_url: item.public_path
                for item in results if item.success and item.public_path
            },
        }
        path = Path(manifest_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
        return manifest


async def download_images(urls: Iterable[str], config: Optional[ImageDownloadConfig] = None) -> List[DownloadedImage]:
    """Convenience function matching the original batch-download workflow."""
    async with ImageDownloader(config) as downloader:
        return await downloader.download_batch(urls)


# Hints that usually should not be bulk-downloaded for a focused PDP clone.
DEFAULT_SKIP_SECTION_HINTS = frozenset({
    "header-nav", "footer", "360-view",
})


def select_download_urls(
    assets: Dict[str, Any],
    *,
    skip_hints: Optional[Iterable[str]] = None,
    skip_gallery: bool = False,
    primary_only: bool = False,
    max_images: int = 80,
    include_types: Optional[Iterable[str]] = None,
) -> List[Dict[str, Any]]:
    """Pick a bounded, section-aware image list for download.

    Returns usage dicts (url + selector + section_hint + ...) so the manifest
    can record where each asset is used. Without this filter, extractors often
    yield hundreds of srcset candidates and chrome icons.
    """
    skip = set(skip_hints if skip_hints is not None else DEFAULT_SKIP_SECTION_HINTS)
    if skip_gallery:
        skip.add("gallery")
    allowed_types = set(include_types or ("image", "background-image", "picture-source", "video-poster"))
    usages = list(assets.get("image_usages") or [])
    if not usages:
        usages = list(assets.get("images") or [])

    scored: List[tuple[int, Dict[str, Any]]] = []
    seen: set[str] = set()
    for usage in usages:
        url = usage.get("url") if isinstance(usage, dict) else str(usage)
        if not url or url in seen or url.startswith("data:"):
            continue
        if isinstance(usage, dict):
            utype = usage.get("type") or "image"
            if utype == "srcset-candidate":
                continue
            if utype not in allowed_types:
                continue
            hint = str(usage.get("section_hint") or "")
            if hint in skip:
                continue
            if primary_only and not usage.get("is_primary"):
                continue
            if usage.get("is_visible") is False and not usage.get("is_primary"):
                continue
            w = float(usage.get("width") or 0)
            h = float(usage.get("height") or 0)
            area = w * h
            score = 0
            if usage.get("is_primary"):
                score += 100
            if usage.get("is_visible"):
                score += 20
            score += min(int(area / 1000), 50)
            if hint in {"product", "hero", "features", "testimonials"}:
                score += 10
            scored.append((score, usage))
            seen.add(url)
        else:
            scored.append((1, {"url": url, "type": "image"}))
            seen.add(url)

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [item for _, item in scored[:max_images]]


async def download_from_extraction(
    extraction: Dict[str, Any],
    *,
    output_dir: str,
    public_prefix: str = "/assets",
    manifest_path: str,
    skip_gallery: bool = False,
    max_images: int = 80,
    config: Optional[ImageDownloadConfig] = None,
) -> Dict[str, Any]:
    """Download only section-relevant images and write an enriched manifest."""
    # Prefer desktop extraction when multi-viewport document is passed.
    selected = extraction
    if "extractions" in extraction:
        extractions = extraction.get("extractions") or []
        if extractions:
            selected = max(extractions, key=lambda item: item.get("viewport", {}).get("width", 0))
    assets = selected.get("assets") or extraction.get("assets") or {}
    usages = select_download_urls(assets, skip_gallery=skip_gallery, max_images=max_images)
    urls = [u["url"] for u in usages if u.get("url")]
    cfg = config or ImageDownloadConfig(output_dir=output_dir, public_prefix=public_prefix, max_images=max_images)
    cfg.output_dir = output_dir
    cfg.public_prefix = public_prefix
    cfg.max_images = max_images
    async with ImageDownloader(cfg) as downloader:
        manifest = await downloader.download_manifest(urls, manifest_path)
    # Enrich with usage context so contracts/agents know where each file belongs.
    usage_by_url = {u["url"]: u for u in usages}
    for entry in manifest.get("entries") or []:
        usage = usage_by_url.get(entry.get("original_url") or "", {})
        entry["selector"] = usage.get("selector")
        entry["section_hint"] = usage.get("section_hint")
        entry["alt"] = usage.get("alt")
        entry["is_primary"] = usage.get("is_primary")
        entry["xpath"] = usage.get("xpath")
    manifest["usage_index"] = [
        {
            "url": e.get("original_url"),
            "public_path": e.get("public_path"),
            "selector": e.get("selector"),
            "section_hint": e.get("section_hint"),
            "alt": e.get("alt"),
            "is_primary": e.get("is_primary"),
            "success": e.get("success"),
        }
        for e in (manifest.get("entries") or [])
    ]
    path = Path(manifest_path)
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    # Also mirror under .cloning assets if caller passed that path separately.
    return manifest
