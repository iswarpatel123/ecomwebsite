#!/usr/bin/env python3
"""
download_creative.py — Download ad creatives (images, videos, thumbnails) by Ad ID.

Usage:
    python3 scripts/download_creative.py --ad-id 1480487800363056 --type video --count 1
    python3 scripts/download_creative.py --ad-id 1806161197219830 --type thumbnail --count 1
    python3 scripts/download_creative.py --ad-id 1359588788899410 --type image --count 2
    python3 scripts/download_creative.py --ad-id 1480487800363056 --all --count 3 --output-dir ./creatives
"""

import argparse
import os
import requests
from pathlib import Path

BASE_MEDIA_URL = "https://images.admakeai.com/ad-media"

def download_file(url: str, dest_path: Path) -> bool:
    """Download a single file with error handling."""
    print(f"[*] Downloading: {url} -> {dest_path}")
    try:
        response = requests.get(url, stream=True, timeout=30)
        if response.status_code == 200:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            with open(dest_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"[+] Saved {dest_path}")
            return True
        else:
            print(f"[-] Failed (Status {response.status_code}): {url}")
            return False
    except Exception as e:
        print(f"[-] Error downloading {url}: {e}")
        return False

def get_urls_for_type(ad_id: str, media_type: str, count: int) -> list[tuple[str, str]]:
    """Generate URLs and local filenames for a given media type and count."""
    urls = []
    for i in range(count):
        if media_type == "image":
            filename = f"image-{i}.jpg"
            url = f"{BASE_MEDIA_URL}/{ad_id}/{filename}"
        elif media_type == "video":
            filename = f"video-{i}.mp4"
            url = f"{BASE_MEDIA_URL}/{ad_id}/{filename}"
        elif media_type == "thumbnail":
            filename = f"thumbnail-{i}.jpg"
            url = f"{BASE_MEDIA_URL}/{ad_id}/{filename}"
        else:
            continue
        urls.append((url, filename))
    return urls

def main():
    parser = argparse.ArgumentParser(description="Download ad creatives from admakeai.com media storage.")
    parser.add_argument("--ad-id", type=str, required=True, help="Ad ID (e.g. 1480487800363056)")
    parser.add_argument("--type", type=str, choices=["image", "video", "thumbnail"], help="Creative type")
    parser.add_argument("--count", type=int, default=1, help="Number of creatives to attempt downloading (default: 1)")
    parser.add_argument("--all", action="store_true", help="Download all types (image, video, thumbnail) up to count")
    parser.add_argument("--output-dir", type=str, default="ad_creatives", help="Output directory (default: ./ad_creatives)")
    
    args = parser.parse_args()
    
    output_dir = Path(args.output_dir) / args.ad_id
    output_dir.mkdir(parents=True, exist_ok=True)
    
    types_to_download = []
    if args.all:
        types_to_download = ["image", "video", "thumbnail"]
    elif args.type:
        types_to_download = [args.type]
    else:
        parser.error("Specify either --type <image|video|thumbnail> or --all")

    success_count = 0
    for m_type in types_to_download:
        items = get_urls_for_type(args.ad_id, m_type, args.count)
        for url, filename in items:
            dest = output_dir / filename
            if download_file(url, dest):
                success_count += 1

    print(f"\n[+] Successfully downloaded {success_count} file(s) to {output_dir}/")

if __name__ == "__main__":
    main()
