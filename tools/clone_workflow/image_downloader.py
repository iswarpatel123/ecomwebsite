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
    # binary/video: skip Pillow; larger timeout/size
    process_images: bool = True
    max_bytes: int = 80 * 1024 * 1024  # 80MB hard cap per file


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
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
}

IMAGE_TYPES = frozenset({"image", "background-image", "picture-source", "video-poster"})
VIDEO_TYPES = frozenset({"video", "video-source"})
EMBED_TYPES = frozenset({"embed"})
# Never HTTP-download these (keep URL in manifest only).
SKIP_DOWNLOAD_TYPES = frozenset({"embed", "srcset-candidate"})


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

    def _ext_from_url_ct(self, url: str, content_type: str) -> str:
        path = urlparse(url).path.lower()
        for ext in ("mp4", "webm", "mov", "m4v", "ogv", "webp", "png", "jpg", "jpeg", "gif", "svg", "avif"):
            if path.endswith("." + ext):
                return "jpg" if ext == "jpeg" else ext
        ct = (content_type or "").split(";")[0].strip().lower()
        return {
            "video/mp4": "mp4", "video/webm": "webm", "video/quicktime": "mov",
            "image/webp": "webp", "image/png": "png", "image/jpeg": "jpg",
            "image/gif": "gif", "image/svg+xml": "svg",
        }.get(ct, "bin")

    async def download_single(self, url: str, index: int, *, kind: str = "image") -> DownloadedImage:
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
            if len(original) > self.config.max_bytes:
                raise ValueError(f"Asset exceeds max_bytes ({len(original)} > {self.config.max_bytes})")
            ct = response.headers.get("content-type", "application/octet-stream")
            is_video = kind in VIDEO_TYPES or ct.startswith("video/") or not self.config.process_images
            if is_video or kind == "binary":
                extension = self._ext_from_url_ct(url, ct)
                processed, width, height = original, 0, 0
            else:
                processed, width, height, extension = _compress(original, url, self.config)
                if extension == "original":
                    extension = self._ext_from_url_ct(url, ct)
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
                "webp": "image/webp", "jpg": "image/jpeg", "png": "image/png",
                "mp4": "video/mp4", "webm": "video/webm", "mov": "video/quicktime",
            }.get(extension, ct)
            if self.config.include_base64 and not is_video:
                result.base64_data = base64.b64encode(processed).decode("ascii")
            result.success = True
        except Exception as exc:
            result.error = str(exc)
            logger.warning("Asset download failed for %s: %s", url, exc)
        return result

    async def download_batch(
        self,
        urls: Iterable[str],
        *,
        kinds: Optional[Dict[str, str]] = None,
    ) -> List[DownloadedImage]:
        unique = list(dict.fromkeys(url for url in urls if url))[: self.config.max_images]
        semaphore = asyncio.Semaphore(max(1, self.config.concurrency))
        kind_map = kinds or {}

        async def one(index: int, url: str) -> DownloadedImage:
            async with semaphore:
                return await self.download_single(url, index, kind=kind_map.get(url, "image"))

        return await asyncio.gather(*(one(i, url) for i, url in enumerate(unique)))

    async def download_manifest(
        self,
        urls: Iterable[str],
        manifest_path: str,
        *,
        kinds: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        results = await self.download_batch(urls, kinds=kinds)
        entries = [asdict(item) for item in results]
        manifest = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "output_dir": self.config.output_dir,
            "public_prefix": self.config.public_prefix,
            "total": len(results),
            "succeeded": sum(item.success for item in results),
            "failed": sum(not item.success for item in results),
            "entries": entries,
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


DEFAULT_SKIP_SECTION_HINTS = frozenset({"header-nav", "footer", "360-view"})


def _merge_usages(assets: Dict[str, Any]) -> List[Dict[str, Any]]:
    usages = list(assets.get("image_usages") or [])
    if not usages:
        usages = list(assets.get("images") or [])
    # media_usages may duplicate posters; merge by url preferring richer type
    seen = {u.get("url") for u in usages if isinstance(u, dict)}
    for m in assets.get("media_usages") or []:
        if isinstance(m, dict) and m.get("url") and m["url"] not in seen:
            usages.append(m)
            seen.add(m["url"])
    return usages


def select_download_urls(
    assets: Dict[str, Any],
    *,
    skip_hints: Optional[Iterable[str]] = None,
    allow_hints: Optional[Iterable[str]] = None,
    skip_gallery: bool = False,
    primary_only: bool = False,
    max_images: int = 80,
    include_types: Optional[Iterable[str]] = None,
    include_video: bool = False,
) -> List[Dict[str, Any]]:
    """Pick bounded, section-aware assets. Agent may further trim via download_from_url_list.

    - allow_hints: if set, only those section_hint values (e.g. {'features'})
    - include_video: add video/video-source (not embeds)
    """
    skip = set(skip_hints if skip_hints is not None else DEFAULT_SKIP_SECTION_HINTS)
    if skip_gallery:
        skip.add("gallery")
    allow = set(allow_hints) if allow_hints is not None else None
    if include_types is not None:
        allowed_types = set(include_types)
    else:
        allowed_types = set(IMAGE_TYPES)
        if include_video:
            allowed_types |= VIDEO_TYPES
    usages = _merge_usages(assets)

    scored: List[tuple[int, Dict[str, Any]]] = []
    seen: set[str] = set()
    for usage in usages:
        url = usage.get("url") if isinstance(usage, dict) else str(usage)
        if not url or url in seen or url.startswith("data:"):
            continue
        if isinstance(usage, dict):
            utype = usage.get("type") or "image"
            if utype in SKIP_DOWNLOAD_TYPES:
                continue
            if utype not in allowed_types:
                continue
            hint = str(usage.get("section_hint") or "")
            if hint in skip:
                continue
            if allow is not None and hint not in allow:
                continue
            if primary_only and not usage.get("is_primary"):
                continue
            if usage.get("is_visible") is False and not usage.get("is_primary") and utype not in VIDEO_TYPES:
                continue
            w = float(usage.get("width") or 0)
            h = float(usage.get("height") or 0)
            area = w * h
            score = 0
            if usage.get("is_primary"):
                score += 100
            if usage.get("is_visible"):
                score += 20
            if utype in VIDEO_TYPES:
                score += 30
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


def list_embeds(assets: Dict[str, Any]) -> List[Dict[str, Any]]:
    """YouTube/Vimeo/etc — record in contracts; do not download."""
    out: List[Dict[str, Any]] = []
    seen: set[str] = set()
    for usage in _merge_usages(assets):
        if not isinstance(usage, dict):
            continue
        if (usage.get("type") or "") not in EMBED_TYPES:
            continue
        url = usage.get("url")
        if url and url not in seen:
            out.append(usage)
            seen.add(url)
    return out


def _enrich_manifest(manifest: Dict[str, Any], usages: List[Dict[str, Any]], embeds: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    usage_by_url = {u["url"]: u for u in usages if u.get("url")}
    for entry in manifest.get("entries") or []:
        usage = usage_by_url.get(entry.get("original_url") or "", {})
        entry["selector"] = usage.get("selector")
        entry["section_hint"] = usage.get("section_hint")
        entry["alt"] = usage.get("alt")
        entry["is_primary"] = usage.get("is_primary")
        entry["xpath"] = usage.get("xpath")
        entry["asset_type"] = usage.get("type")
    manifest["usage_index"] = [
        {
            "url": e.get("original_url"),
            "public_path": e.get("public_path"),
            "selector": e.get("selector"),
            "section_hint": e.get("section_hint"),
            "alt": e.get("alt"),
            "is_primary": e.get("is_primary"),
            "asset_type": e.get("asset_type"),
            "content_type": e.get("content_type"),
            "success": e.get("success"),
        }
        for e in (manifest.get("entries") or [])
    ]
    if embeds is not None:
        manifest["embeds"] = [
            {"url": e.get("url"), "selector": e.get("selector"), "section_hint": e.get("section_hint"), "type": "embed"}
            for e in embeds
        ]
    return manifest


def _pick_extraction(extraction: Dict[str, Any]) -> Dict[str, Any]:
    if "extractions" in extraction:
        extractions = extraction.get("extractions") or []
        if extractions:
            return max(extractions, key=lambda item: item.get("viewport", {}).get("width", 0))
    return extraction


async def download_from_url_list(
    urls: Iterable[str],
    *,
    output_dir: str,
    public_prefix: str = "/assets",
    manifest_path: str,
    kinds: Optional[Dict[str, str]] = None,
    usages: Optional[List[Dict[str, Any]]] = None,
    embeds: Optional[List[Dict[str, Any]]] = None,
    config: Optional[ImageDownloadConfig] = None,
) -> Dict[str, Any]:
    """Agent-curated download: pass exact URLs (from extraction analysis). Tool stays dumb."""
    url_list = list(dict.fromkeys(u for u in urls if u and not str(u).startswith("data:")))
    kind_map = dict(kinds or {})
    for u in url_list:
        if u not in kind_map:
            low = u.lower().split("?", 1)[0]
            if any(low.endswith(ext) for ext in (".mp4", ".webm", ".mov", ".m4v", ".ogv")):
                kind_map[u] = "video"
            else:
                kind_map[u] = "image"
    cfg = config or ImageDownloadConfig(output_dir=output_dir, public_prefix=public_prefix, max_images=max(len(url_list), 1))
    cfg.output_dir = output_dir
    cfg.public_prefix = public_prefix
    cfg.max_images = max(len(url_list), cfg.max_images)
    # If any video, use longer timeout default when still defaultish
    if any(kind_map.get(u) in VIDEO_TYPES or kind_map.get(u) == "video" for u in url_list):
        if cfg.timeout <= 15:
            cfg.timeout = 60
    async with ImageDownloader(cfg) as downloader:
        manifest = await downloader.download_manifest(url_list, manifest_path, kinds=kind_map)
    return _enrich_manifest(manifest, usages or [{"url": u, "type": kind_map.get(u, "image")} for u in url_list], embeds)


async def download_from_extraction(
    extraction: Dict[str, Any],
    *,
    output_dir: str,
    public_prefix: str = "/assets",
    manifest_path: str,
    skip_gallery: bool = False,
    max_images: int = 80,
    allow_hints: Optional[Iterable[str]] = None,
    include_video: bool = False,
    include_types: Optional[Iterable[str]] = None,
    config: Optional[ImageDownloadConfig] = None,
) -> Dict[str, Any]:
    """Heuristic download from extraction; prefer allow_hints for section-only clones."""
    selected = _pick_extraction(extraction)
    assets = selected.get("assets") or extraction.get("assets") or {}
    usages = select_download_urls(
        assets,
        skip_gallery=skip_gallery,
        max_images=max_images,
        allow_hints=allow_hints,
        include_video=include_video,
        include_types=include_types,
    )
    embeds = list_embeds(assets)
    if allow_hints is not None:
        allow = set(allow_hints)
        embeds = [e for e in embeds if str(e.get("section_hint") or "") in allow]
    urls = [u["url"] for u in usages if u.get("url")]
    kinds = {u["url"]: (u.get("type") or "image") for u in usages if u.get("url")}
    cfg = config or ImageDownloadConfig(output_dir=output_dir, public_prefix=public_prefix, max_images=max_images)
    cfg.output_dir = output_dir
    cfg.public_prefix = public_prefix
    cfg.max_images = max_images
    if include_video and cfg.timeout <= 15:
        cfg.timeout = 60
    async with ImageDownloader(cfg) as downloader:
        manifest = await downloader.download_manifest(urls, manifest_path, kinds=kinds)
    return _enrich_manifest(manifest, usages, embeds)
