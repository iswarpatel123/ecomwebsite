#!/usr/bin/env python3
"""
Meta Ads Collector Script

Fetches all ads from a specific Facebook page and saves them to JSONL.
Uses meta-ads-collector library to fetch ads from the Meta Ad Library.

Features:
- Fetches all ads from a specific page
- Persists collection state across runs using SQLite deduplication
  (only NEW ads are added on subsequent runs - existing data is preserved)
- Saves ad data to JSONL (appends new rows, never overwrites existing data)
- Downloads creatives (images/videos) for each ad (optional)
- Saves session tokens to avoid re-authentication

Usage:
    # Run for a specific page (from any directory)
    python3 scripts/MetaAdsCollector.py --page-id 151402834721433

    # Run in test mode (limit results)
    python3 scripts/MetaAdsCollector.py --page-id 151402834721433 --max-results 5 --test

    # Reset dedup state (re-collect all ads from scratch)
    python3 scripts/MetaAdsCollector.py --page-id 151402834721433 --reset-dedup

    # Also collect other page
    python3 scripts/MetaAdsCollector.py --page-id 109718494870340

Output locations (always relative to the script's directory, not CWD):
- JSON file:      ads_output/{page_id}.jsonl
- State file:    ads_output/{page_id}_state.db  (deduplication tracking)
- Session file:  ads_output/{page_id}_session.json  (token persistence)
- Creatives dir: ads_output/{page_id}_creatives/  (if --creative-dir requested)

Output: JSONL format with one JSON object per line containing:
    id, page_id, page_name, page_url, is_active, ad_status,
    delivery_start_time, delivery_stop_time, creative_body, creative_title,
    creative_description, creative_link_url, creative_image_url, snapshot_url,
    impressions_lower, impressions_upper, spend_lower, spend_upper, currency,
    publisher_platforms, languages, funding_entity, disclaimer, ad_type,
    collected_at
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ── Resolve paths relative to the script file, not CWD ───────────────────────
SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = SCRIPT_DIR.parent

# Add the MetaAdsCollector source to the path so we always use the local
# fixed version (with the doc_id / challenge patches applied)
sys.path.insert(0, str(REPO_ROOT / "MetaAdsCollector"))

from meta_ads_collector import (
    MetaAdsCollector,
    DeduplicationTracker,
    setup_logging,
)

# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────

DEFAULT_PAGE_ID = "151402834721433"
# Output file extension for JSON output
DEFAULT_OUTPUT_EXT = "jsonl"

# Output dir is always next to the script, regardless of CWD
DEFAULT_OUTPUT_DIR = str(SCRIPT_DIR / "ads_output")
DEFAULT_COUNTRY = "US"
DEFAULT_AD_TYPE = MetaAdsCollector.AD_TYPE_ALL
DEFAULT_STATUS = MetaAdsCollector.STATUS_ACTIVE  # "active"
DEFAULT_SEARCH_TYPE = MetaAdsCollector.SEARCH_PAGE  # "PAGE"
DEFAULT_PAGE_SIZE = 10
DEFAULT_LOG_LEVEL = "INFO"

# ──────────────────────────────────────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────────────────────────────────────

logger = logging.getLogger(__name__)


def setup_logger(level: str = DEFAULT_LOG_LEVEL) -> logging.Logger:
    """Configure logging for the script."""
    setup_logging(level=level)
    return logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Session persistence
# ──────────────────────────────────────────────────────────────────────────────

def load_session_file(session_path: Path) -> dict:
    """Load saved session tokens/cookies from file."""
    if not session_path.exists():
        logger.debug(f"Session file not found: {session_path}")
        return {}
    try:
        with open(session_path, "r") as f:
            data = json.load(f)
        logger.debug(f"Loaded session from {session_path}")
        return data
    except Exception as e:
        logger.warning(f"Failed to load session file {session_path}: {e}")
        return {}


def save_session_file(session_path: Path, session_data: dict) -> None:
    """Save session tokens/cookies to file."""
    try:
        session_path.parent.mkdir(parents=True, exist_ok=True)
        with open(session_path, "w") as f:
            json.dump(session_data, f, indent=2)
        logger.debug(f"Saved session to {session_path}")
    except Exception as e:
        logger.error(f"Failed to save session file {session_path}: {e}")


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main():
    global logger

    parser = argparse.ArgumentParser(
        description="Collect Meta Ads from a specific page and save to JSONL.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--page-id",
        type=str,
        default=os.getenv("PAGE_ID", DEFAULT_PAGE_ID),
        help=f"Facebook page ID (default: {DEFAULT_PAGE_ID})",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory for JSONL/state/session files (default: ads_output/ next to script)",
    )
    parser.add_argument(
        "--country",
        type=str,
        default=DEFAULT_COUNTRY,
        help=f"Country code (default: {DEFAULT_COUNTRY})",
    )
    parser.add_argument(
        "--ad-type",
        type=str,
        default=DEFAULT_AD_TYPE,
        choices=["all", "political", "housing", "employment", "credit"],
        help=f"Ad type filter (default: {DEFAULT_AD_TYPE})",
    )
    parser.add_argument(
        "--status",
        type=str,
        default=DEFAULT_STATUS,
        choices=["active", "inactive", "all"],
        help=f"Ad status filter (default: {DEFAULT_STATUS})",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=None,
        help="Maximum ads to collect (default: unlimited)",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=DEFAULT_PAGE_SIZE,
        help=f"Results per API request (default: {DEFAULT_PAGE_SIZE})",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default=DEFAULT_LOG_LEVEL,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help=f"Logging level (default: {DEFAULT_LOG_LEVEL})",
    )
    parser.add_argument(
        "--rate-limit-delay",
        type=float,
        default=1.0,
        help="Delay between requests in seconds (default: 1.0)",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=5,
        help="Maximum retry attempts for rate limiting (default: 5)",
    )
    parser.add_argument(
        "--creative-dir",
        type=str,
        default=None,
        help="Download creatives to this subdirectory (default: disabled)",
    )
    parser.add_argument(
        "--reset-dedup",
        action="store_true",
        help="Clear deduplication state and re-collect all ads from scratch",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test mode: limit to --max-results ads (default 5 if not set)",
    )

    args = parser.parse_args()

    # In test mode default to 5 results if no --max-results given
    if args.test and args.max_results is None:
        args.max_results = 5

    # Setup logger
    logger = setup_logger(level=args.log_level)

    # Resolve output directory (make absolute)
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path    = output_dir / f"{args.page_id}.{DEFAULT_OUTPUT_EXT}"
    state_path   = output_dir / f"{args.page_id}_state.db"
    session_path = output_dir / f"{args.page_id}_session.json"

    logger.info("=" * 70)
    logger.info("Meta Ads Collector")
    logger.info("=" * 70)
    logger.info(f"Page ID:          {args.page_id}")
    logger.info(f"Output JSON:      {json_path}")
    logger.info(f"State DB:         {state_path}")
    logger.info(f"Country:          {args.country}")
    logger.info(f"Ad type:          {args.ad_type}")
    logger.info(f"Status:           {args.status}")
    logger.info(f"Max results:      {args.max_results or 'unlimited'}")
    logger.info(f"Test mode:        {args.test}")
    logger.info(f"Reset dedup:      {args.reset_dedup}")
    logger.info("=" * 70)

    try:
        # Optionally clear dedup state
        if args.reset_dedup and state_path.exists():
            state_path.unlink()
            logger.info(f"Cleared dedup state: {state_path}")

        # Load existing ads count for reporting (JSONL format - count lines)
        existing_rows = 0
        if json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                existing_rows = sum(1 for _ in f)
            logger.info(f"Existing JSONL rows: {existing_rows}")

        # Load saved session (avoids full re-auth on repeat runs)
        session_data = load_session_file(session_path)
        logger.info(f"Session data loaded: {len(session_data)} keys")

        # Create deduplication tracker
        dedup_tracker = DeduplicationTracker(mode="persistent", db_path=str(state_path))
        logger.info(f"Deduplication tracker: {state_path.name}")

        # Create collector
        collector = MetaAdsCollector(
            cookies=session_data,
            rate_limit_delay=args.rate_limit_delay,
            max_retries=args.max_retries,
        )

        # Creative download directory
        creative_dir = None
        if args.creative_dir:
            creative_dir = output_dir / args.creative_dir
            if not args.test:
                creative_dir.mkdir(parents=True, exist_ok=True)

        # Collect and append to JSONL
        # collect_to_jsonl APPENDS new rows instead of overwriting
        new_count = collector.collect_to_jsonl(
            str(json_path),
            country=args.country,
            ad_type=args.ad_type,
            status=args.status,
            search_type=DEFAULT_SEARCH_TYPE,
            page_ids=[args.page_id],
            sort_by=MetaAdsCollector.SORT_IMPRESSIONS,
            max_results=args.max_results,
            page_size=args.page_size,
            dedup_tracker=dedup_tracker,
        )

        # Count total rows now in JSONL
        total_rows = 0
        if json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                total_rows = sum(1 for _ in f)

        if new_count == 0:
            logger.info(
                f"No NEW ads found (all already collected in a previous run). "
                f"JSONL still contains {total_rows} total ads."
            )
            logger.info(
                "To re-collect everything from scratch, use: --reset-dedup"
            )
        else:
            logger.info(f"Added {new_count} new ads. JSONL now has {total_rows} total ads.")
        logger.info(f"Output: {json_path}")

        # Download creatives if requested (skip in test mode)
        if creative_dir and not args.test:
            logger.info("Downloading creatives for newly collected ads...")
            ads = list(collector.collect(
                country=args.country,
                ad_type=args.ad_type,
                status=args.status,
                search_type=DEFAULT_SEARCH_TYPE,
                page_ids=[args.page_id],
                sort_by=MetaAdsCollector.SORT_IMPRESSIONS,
                max_results=new_count if new_count else None,
                dedup_tracker=None,  # don't dedup here, we want the new ones
            ))
            for ad in ads:
                try:
                    results = collector.download_ad_media(ad, str(creative_dir))
                    success = sum(1 for r in results if r.success)
                    logger.debug(
                        f"Downloaded {success}/{len(results)} creatives for ad {ad.id}"
                    )
                except Exception as e:
                    logger.warning(f"Failed to download creatives for ad {ad.id}: {e}")

        # Persist session for next run
        try:
            cookies = collector.client.session.cookies.get_dict()
            save_session_file(session_path, cookies)
        except Exception as e:
            logger.warning(f"Could not save session: {e}")

        logger.info("=" * 70)
        logger.info("Collection completed successfully!")

    except KeyboardInterrupt:
        logger.info("\nCollection interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Collection failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()