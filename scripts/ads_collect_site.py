#!/usr/bin/env python3
"""
ads_collect_site.py — Stage 1 of the Ad Publishing Workflow (V1).

Thin wrapper around scripts/MetaAdsCollector.py. Reads
sites/<slug>/ads/config.json, loops competitors[].page_id, and shells out to
the single-page collector once per competitor with site-scoped output paths.
After each page run it copies the newest JSONL to latest.jsonl and reorganizes
the flat creative downloads into media/<ad_id>/ with a meta.json pointer per ad
(per the Ad Publishing Workflow layout).

Usage:
    python3 scripts/ads_collect_site.py --site furniture
    python3 scripts/ads_collect_site.py --site furniture --page-id 151402834721433
    python3 scripts/ads_collect_site.py --page-id 151402834721433   # debug: old global path

Layout produced per competitor page:
    sites/<slug>/ads/competitors/<page_id>/
        latest.jsonl            # copy of newest <run_ts>.jsonl
        <run_ts>.jsonl
        session.json            # Ad Library session cookies (gitignored)
        media/<ad_id>/          # top-N downloaded creatives only
            0.jpg | 0.mp4 | …
            meta.json           # { ad_id, jsonl_line, files, source_url }

With `competitors: []` (the shipped default) this is a no-op — expected until
real competitor page IDs are filled in per site.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = SCRIPT_DIR.parent
SITES_DIR = REPO_ROOT / "sites"
COLLECTOR = SCRIPT_DIR / "MetaAdsCollector.py"

# Collect config -> collector flag mapping. The collector always ranks by
# SORT_IMPRESSIONS; anything else in config is a warning, not a pass-through.
SUPPORTED_SORT = {"impressions"}

# Preferred media type when several are downloaded for the same creative
# (lower wins). video_hd > image > video_sd > thumbnail.
_MEDIA_PRIORITY = {"video_hd": 0, "image": 1, "video_sd": 2, "thumbnail": 3}

# media_type may contain underscores (e.g. video_hd, video_sd)
_FLAT_MEDIA_RE = re.compile(r"^(?P<ad_id>\d+)_(?P<idx>\d+)_(?P<type>\w+(?:_\w+)*)(?P<ext>\.[^.]+)$")


def load_config(slug: str) -> dict:
    path = SITES_DIR / slug / "ads" / "config.json"
    if not path.exists():
        sys.exit(f"config not found: {path} — scaffold the site first (see docs/AdPublishingWorkflow.md)")
    return json.loads(path.read_text())


def run_collector(page_id: str, output_dir: Path, config: dict, log_level: str = "INFO") -> None:
    """Shell out to the single-page collector with site-scoped paths."""
    collect = config.get("collect", {})
    sort_by = collect.get("sort_by", "impressions")
    if sort_by not in SUPPORTED_SORT:
        print(f"WARNING: collect.sort_by={sort_by!r} unsupported; using collector default (SORT_IMPRESSIONS)")

    cmd = [
        sys.executable, str(COLLECTOR),
        "--page-id", page_id,
        "--output-dir", str(output_dir),
        "--session-file", "session.json",
        "--country", collect.get("country", "US"),
        "--status", collect.get("status", "active"),
        "--max-results", str(collect.get("max_per_page", 10)),
        "--log-level", log_level,
    ]
    if collect.get("download_media", True):
        cmd += ["--creative-dir", "media"]

    print(f"\n=== Collecting page {page_id} -> {output_dir} ===")
    subprocess.run(cmd, check=True)


def update_latest(output_dir: Path) -> Path | None:
    """Copy the newest <run_ts>.jsonl to latest.jsonl; return its path."""
    jsonl_files = sorted(output_dir.glob("*.jsonl"))
    if not jsonl_files:
        return None
    newest = max(jsonl_files, key=lambda p: p.stat().st_mtime)
    latest = output_dir / "latest.jsonl"
    shutil.copy2(newest, latest)
    print(f"latest.jsonl <- {newest.name}")
    return latest


def organize_media(output_dir: Path, latest: Path) -> None:
    """Reorganize flat downloads into media/<ad_id>/0.ext + meta.json."""
    media_dir = output_dir / "media"
    if not media_dir.exists():
        print("  (no media dir — nothing to organize)")
        return

    rows = [json.loads(line) for line in latest.read_text().splitlines() if line.strip()]

    for line_idx, row in enumerate(rows):
        ad_id = row.get("id")
        if not ad_id:
            continue
        ad_dir = media_dir / str(ad_id)
        ad_dir.mkdir(parents=True, exist_ok=True)

        # Best file per creative index, by media type priority.
        best: dict[int, tuple[int, Path]] = {}
        for f in media_dir.glob(f"{ad_id}_*"):
            m = _FLAT_MEDIA_RE.match(f.name)
            if not m:
                continue
            idx = int(m.group("idx"))
            priority = _MEDIA_PRIORITY.get(m.group("type"), 99)
            if idx not in best or priority < best[idx][0]:
                best[idx] = (priority, f)

        files: list[str] = []
        for idx in sorted(best):
            src = best[idx][1]
            dest = ad_dir / f"{idx}{src.suffix}"
            shutil.move(str(src), str(dest))
            files.append(dest.name)

        source_url = row.get("snapshot_url") or f"https://facebook.com/ads/library/{ad_id}"
        meta = {
            "ad_id": str(ad_id),
            "jsonl_line": line_idx,
            "files": files,
            "source_url": source_url,
        }
        (ad_dir / "meta.json").write_text(json.dumps(meta, indent=2))
        print(f"  media/{ad_id}/: {', '.join(files) or '(no creatives)'}")


def collect_page(slug: str, config: dict, page_id: str) -> None:
    """Run one competitor page collection under the site ads layout."""
    output_dir = SITES_DIR / slug / "ads" / "competitors" / str(page_id)
    output_dir.mkdir(parents=True, exist_ok=True)
    run_collector(str(page_id), output_dir, config)
    latest = update_latest(output_dir)
    if latest:
        organize_media(output_dir, latest)


def collect_site(slug: str, only_page_id: str | None = None) -> None:
    config = load_config(slug)
    competitors = config.get("competitors", [])

    # Explicit --page-id override runs even when competitors: [] (ships empty).
    if only_page_id:
        collect_page(slug, config, only_page_id)
        return

    if not competitors:
        print(f"Site '{slug}': competitors: [] — nothing to collect (expected until page IDs are filled in).")
        return

    for comp in competitors:
        page_id = comp.get("page_id") if isinstance(comp, dict) else comp
        if not page_id:
            continue
        collect_page(slug, config, page_id)


def main():
    parser = argparse.ArgumentParser(description="Stage 1: collect competitor ads for a site (thin wrapper).")
    parser.add_argument("--site", help="Site slug, e.g. 'furniture' (reads sites/<slug>/ads/config.json)")
    parser.add_argument("--page-id", help="Collect a single page (with --site: scoped to that site; alone: old global path)")
    args = parser.parse_args()

    if args.site:
        collect_site(args.site, args.page_id)
    elif args.page_id:
        # Debug path: old global output, as before this workflow existed.
        subprocess.run([sys.executable, str(COLLECTOR), "--page-id", args.page_id], check=True)
    else:
        parser.error("provide --site (and optionally --page-id)")


if __name__ == "__main__":
    main()
