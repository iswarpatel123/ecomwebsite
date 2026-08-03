#!/usr/bin/env python3
"""
ads_publish_drafts.py — Stage 4 of the Ad Publishing Workflow (V1).

Operator-run local CLI. Publishes `ready` ad drafts to Meta as **PAUSED** ads
by shelling out to the Meta Ads CLI (`meta ads ...`). Nothing is ever
activated from here, and this is never wired into CI in V1 — the human gate
stays real.

Usage:
    python3 scripts/ads_publish_drafts.py --site furniture [--draft-id ID] [--dry-run] [--force]

Behavior:
    1. Loads sites/<slug>/ads/config.json meta.* + env ACCESS_TOKEN.
    2. On first publish for a site: idempotently creates the `always-on`
       campaign (ecom-<slug>, OUTCOME_SALES) and default ad set
       (ecom-<slug>-default, US, placeholder daily budget, conversion
       tracking). Writes campaign_id / default_adset_id back into config.
       List-by-name before create — never duplicates. Errors out if a name
       lookup returns more than one campaign/ad set.
    3. Refuses to create/publish under OUTCOME_SALES if meta.pixel_id is null.
    4. Scans drafts/*/draft.json where status == "ready" and link_url is set.
    5. Creates an Ad Creative, then an Ad under the resolved campaign/ad set,
       forcing status=PAUSED. Writes meta_result and status="published".

Exit codes (mirror the Meta Ads CLI): 0 success, 3 auth, 4 API, 5 not found.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = SCRIPT_DIR.parent
SITES_DIR = REPO_ROOT / "sites"

# Placeholder daily budget in cents ($1/day) until real spend starts.
# Named constant so it's easy to find and raise later.
DAILY_BUDGET_CENTS = 100

EXIT_OK = 0
EXIT_AUTH = 3
EXIT_API = 4
EXIT_NOT_FOUND = 5

# Meta Ads CLI binary. Override with META_BIN env if not on PATH.
META_BIN = os.environ.get("META_BIN", "meta")


class PublishError(Exception):
    """Raised with a Meta Ads CLI-style exit code."""

    def __init__(self, message: str, code: int = EXIT_API):
        super().__init__(message)
        self.code = code


# ── Helpers ────────────────────────────────────────────────────────────────


def load_config(site: str) -> dict:
    path = SITES_DIR / site / "ads" / "config.json"
    if not path.exists():
        raise PublishError(f"config not found: {path}", EXIT_NOT_FOUND)
    return json.loads(path.read_text())


def save_config(site: str, config: dict) -> None:
    path = SITES_DIR / site / "ads" / "config.json"
    path.write_text(json.dumps(config, indent=2) + "\n")


def meta_env(config: dict, dry_run: bool = False) -> dict:
    """Build the subprocess env. ACCESS_TOKEN required unless dry-run (no API calls)."""
    env = dict(os.environ)
    env.setdefault("AD_ACCOUNT_ID", str(config.get("meta", {}).get("ad_account_id") or ""))
    if not dry_run and not env.get("ACCESS_TOKEN"):
        raise PublishError(
            "ACCESS_TOKEN not set — add it to .env or export it (Meta system user token).",
            EXIT_AUTH,
        )
    return env


def run_meta(args: list[str], dry_run: bool, env: dict):
    """Run `meta [--output json --no-input] <args>`. Returns parsed JSON (or None in dry-run)."""
    cmd = [META_BIN, "--output", "json", "--no-input"] + args
    if dry_run:
        print("meta --output json --no-input " + " ".join(shlex_quote(a) for a in args))
        return None
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
    except FileNotFoundError:
        raise PublishError(
            f"`{META_BIN}` CLI not found — install it with: pip install meta-ads "
            "(and set ACCESS_TOKEN / AD_ACCOUNT_ID in .env).",
            EXIT_API,
        )
    if proc.returncode == 3:
        raise PublishError(f"Meta auth error: {proc.stderr.strip() or proc.stdout.strip()}", EXIT_AUTH)
    if proc.returncode == 4:
        raise PublishError(f"Meta API error: {proc.stderr.strip() or proc.stdout.strip()}", EXIT_API)
    if proc.returncode == 5:
        raise PublishError(f"Not found: {proc.stderr.strip() or proc.stdout.strip()}", EXIT_NOT_FOUND)
    if proc.returncode != 0:
        raise PublishError(f"meta CLI failed ({proc.returncode}): {proc.stderr.strip() or proc.stdout.strip()}")
    if not proc.stdout.strip():
        return None
    return json.loads(proc.stdout)


def shlex_quote(s: str) -> str:
    """Minimal shell quoting for dry-run display."""
    if s and all(c.isalnum() or c in "-_./:" for c in s):
        return s
    return "'" + s.replace("'", "'\\''") + "'"


def _items(data) -> list[dict]:
    """Normalize common Meta CLI response envelopes to a list of resources."""
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        # Depending on the CLI version, list responses are either a bare list
        # or wrapped in {"data": [...]}; create responses remain a dict.
        nested = data.get("data")
        if isinstance(nested, list):
            return [item for item in nested if isinstance(item, dict)]
        return [data]
    return []


def extract_id(data) -> str | None:
    """Best-effort id extraction from bare or {data: ...} CLI JSON."""
    items = _items(data)
    if items and items[0].get("id"):
        return str(items[0]["id"])
    return None


def find_by_name(items, name: str, kind: str) -> str:
    """Find a resource id by exact name; error out if the name is ambiguous."""
    items = _items(items)
    if not items:
        return ""
    matches = [i for i in items if i.get("name") == name]
    if len(matches) > 1:
        raise PublishError(
            f"Found {len(matches)} {kind} named '{name}'; Meta does not enforce unique "
            f"names. Rename/archive duplicates and retry.",
            EXIT_API,
        )
    return str(matches[0]["id"]) if matches else ""


# ── Campaign / ad set resolution (idempotent) ─────────────────────────────


def resolve_campaign(site: str, config: dict, dry_run: bool, env: dict) -> str:
    """Return (and if needed create) the always-on campaign id. Writes config back."""
    meta = config["meta"]
    entry = next((c for c in meta.get("campaigns", []) if c.get("purpose") == "always-on"), None)
    if entry is None:
        raise PublishError("config meta.campaigns has no 'always-on' entry", EXIT_API)
    if entry.get("campaign_id"):
        return str(entry["campaign_id"])

    defaults = config.get("campaign_defaults", {})
    objective = defaults.get("objective", "OUTCOME_SALES")
    name = f"ecom-{site}"

    campaigns = run_meta(["ads", "campaign", "list"], dry_run, env) or []
    existing = find_by_name(campaigns, name, "campaigns") if campaigns else ""
    if existing:
        entry["campaign_id"] = existing
        save_config(site, config)
        return existing

    created = run_meta(
        ["ads", "campaign", "create", "--name", name,
         "--objective", objective,
         "--daily-budget", str(DAILY_BUDGET_CENTS)],
        dry_run, env,
    )
    campaign_id = extract_id(created)
    if not campaign_id:
        if dry_run:
            return "<CAMPAIGN_ID>"
        raise PublishError(f"Could not read campaign id from create response: {created}")
    entry["campaign_id"] = campaign_id
    save_config(site, config)
    return campaign_id


def resolve_adset(site: str, config: dict, campaign_id: str, dry_run: bool, env: dict) -> str:
    """Return (and if needed create) the default ad set id. Writes config back."""
    meta = config["meta"]
    pixel_id = meta.get("pixel_id")
    if meta.get("dataset_mode", "per_site") == "shared" and not meta.get("shared_dataset_key"):
        raise PublishError("shared dataset mode requires shared_dataset_key", EXIT_API)
    if not pixel_id:
        raise PublishError(
            "meta.pixel_id is null but objective is OUTCOME_SALES — cannot create a "
            "conversion-optimized ad set. Configure the Meta Pixel first (fail fast).",
            EXIT_API,
        )
    entry = next((c for c in meta.get("campaigns", []) if c.get("purpose") == "always-on"), None)
    if entry is None:
        raise PublishError("config meta.campaigns has no 'always-on' entry", EXIT_API)
    if entry.get("default_adset_id"):
        return str(entry["default_adset_id"])

    defaults = config.get("campaign_defaults", {})
    countries = ",".join(defaults.get("countries", ["US"]))
    name = f"ecom-{site}-default"

    adsets = run_meta(["ads", "adset", "list", campaign_id], dry_run, env) or []
    existing = find_by_name(adsets, name, "ad sets") if adsets else ""
    if existing:
        entry["default_adset_id"] = existing
        save_config(site, config)
        return existing

    created = run_meta(
        ["ads", "adset", "create", campaign_id, "--name", name,
         "--optimization-goal", "OFFSITE_CONVERSIONS",
         "--billing-event", "IMPRESSIONS",
         "--pixel-id", str(pixel_id),
         "--custom-event-type", "PURCHASE",
         "--targeting-countries", countries,
         "--daily-budget", str(DAILY_BUDGET_CENTS)],
        dry_run, env,
    )
    adset_id = extract_id(created)
    if not adset_id:
        if dry_run:
            return "<AD_SET_ID>"
        raise PublishError(f"Could not read ad set id from create response: {created}")
    entry["default_adset_id"] = adset_id
    save_config(site, config)
    return adset_id


# ── Draft publishing ───────────────────────────────────────────────────────


def scan_drafts(site: str, only_draft_id: str | None):
    """Yield (draft_dir, draft) for every drafts/<id>/draft.json in the site."""
    drafts_root = SITES_DIR / site / "ads" / "drafts"
    if not drafts_root.exists():
        return
    for draft_dir in sorted(drafts_root.iterdir()):
        if not draft_dir.is_dir():
            continue
        if only_draft_id and draft_dir.name != only_draft_id:
            continue
        draft_path = draft_dir / "draft.json"
        if not draft_path.exists():
            continue
        try:
            draft = json.loads(draft_path.read_text())
        except json.JSONDecodeError as e:
            print(f"SKIP {draft_dir.name}: invalid draft.json ({e})")
            continue
        yield draft_dir, draft


def resolve_asset_paths(draft_dir: Path, creative: dict) -> list[Path]:
    """Resolve creative.assets paths (relative to the draft folder) to absolute."""
    assets = creative.get("assets") or []
    paths = []
    for asset in assets:
        p = (draft_dir / asset["path"]).resolve()
        if not p.exists():
            raise PublishError(f"asset missing: {p}", EXIT_NOT_FOUND)
        paths.append(p)
    return paths


def publish_draft(site: str, config: dict, draft_dir: Path, draft: dict,
                  campaign_id: str, adset_id: str, dry_run: bool, env: dict) -> None:
    """Create creative + ad for one ready draft, force PAUSED, write back meta_result."""
    creative = draft.get("creative", {})
    publish = draft.get("publish", {})

    link_url = creative.get("link_url")
    if not link_url:
        raise PublishError(f"{draft_dir.name}: ready draft with blank link_url — refusing", EXIT_API)

    asset_paths = resolve_asset_paths(draft_dir, creative)
    if not asset_paths:
        raise PublishError(f"{draft_dir.name}: no assets", EXIT_API)

    meta = config["meta"]
    page_id = meta.get("page_id")
    pixel_id = meta.get("pixel_id")
    if not page_id or page_id == "OUR_SHARED_PAGE_ID":
        raise PublishError(f"meta.page_id not configured for site '{site}'", EXIT_API)
    if not pixel_id:
        raise PublishError(f"meta.pixel_id not configured for site '{site}'", EXIT_API)

    fmt = creative.get("format", "image")
    ad_name = publish.get("ad_name") or f"{site} | {draft.get('draft_id', '')}"
    cta = creative.get("cta_type") or config.get("creative", {}).get("cta", "SHOP_NOW")

    creative_cmd = [
        "ads", "creative", "create",
        "--name", ad_name,
        "--page-id", str(page_id),
        "--body", creative.get("primary_text", ""),
        "--title", creative.get("headline", ""),
        "--link-url", link_url,
    ]
    if creative.get("description"):
        creative_cmd += ["--description", creative["description"]]
    creative_cmd += ["--call-to-action", cta]

    if fmt == "video":
        creative_cmd += ["--video", str(asset_paths[0])]
    elif len(asset_paths) > 1:
        # Carousel via DCO (plural --images), capped at 5 cards for cost control.
        for p in asset_paths[:5]:
            creative_cmd += ["--images", str(p)]
    else:
        creative_cmd += ["--image", str(asset_paths[0])]

    creative_data = run_meta(creative_cmd, dry_run, env)
    creative_id = extract_id(creative_data)
    if not creative_id and dry_run:
        creative_id = "<CREATIVE_ID>"
    if not creative_id:
        raise PublishError(f"Could not read creative id from create response: {creative_data}")

    ad_cmd = [
        "ads", "ad", "create", adset_id,
        "--name", ad_name,
        "--creative-id", creative_id,
        "--pixel-id", str(pixel_id),
        "--status", "PAUSED",  # explicitly enforce draft mode
    ]
    ad_data = run_meta(ad_cmd, dry_run, env)
    ad_id = extract_id(ad_data)
    if not ad_id and dry_run:
        ad_id = "<AD_ID>"
    if not ad_id:
        raise PublishError(f"Could not read ad id from create response: {ad_data}")

    if not dry_run:
        uploaded_hashes = []
        if isinstance(creative_data, dict):
            uploaded_hashes = [
                str(v) for k, v in creative_data.items()
                if "hash" in k.lower() and v
            ]
        draft["meta_result"] = {
            "creative_id": creative_id,
            "ad_id": ad_id,
            "uploaded_hashes": uploaded_hashes,
        }
        draft["status"] = "published"
        (draft_dir / "draft.json").write_text(json.dumps(draft, indent=2))
        print(f"PUBLISHED {draft_dir.name}: creative={creative_id} ad={ad_id} (PAUSED)")
    else:
        print(f"# (dry-run) would publish {draft_dir.name}")


# ── CLI ────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Stage 4: publish ready ad drafts as PAUSED Meta ads.")
    parser.add_argument("--site", required=True, help="Site slug, e.g. 'furniture'")
    parser.add_argument("--draft-id", help="Publish only this draft id")
    parser.add_argument("--dry-run", action="store_true", help="Print CLI commands without running them")
    parser.add_argument("--force", action="store_true", help="Re-publish drafts that already have meta_result.ad_id")
    args = parser.parse_args()

    site = args.site
    config = load_config(site)
    env = meta_env(config, args.dry_run)

    defaults = config.get("campaign_defaults", {})
    objective = defaults.get("objective", "OUTCOME_SALES")
    pixel_id = config.get("meta", {}).get("pixel_id")
    if objective == "OUTCOME_SALES" and not pixel_id:
        raise PublishError(
            f"Refusing: site '{site}' uses {objective} but meta.pixel_id is null. "
            "Configure the Meta Pixel first (fail fast — no campaign/ad set created).",
            EXIT_API,
        )

    if args.dry_run:
        print(f"# DRY-RUN for site '{site}' (nothing will be executed)")

    campaign_id = resolve_campaign(site, config, args.dry_run, env)
    adset_id = resolve_adset(site, config, campaign_id, args.dry_run, env)
    print(f"campaign_id={campaign_id} adset_id={adset_id}")

    published = 0
    for draft_dir, draft in scan_drafts(site, args.draft_id):
        status = draft.get("status")
        if status != "ready":
            print(f"SKIP {draft_dir.name}: status={status} (only 'ready' publishes)")
            continue
        meta_result = draft.get("meta_result") or {}
        if meta_result.get("ad_id") and not args.force:
            print(f"SKIP {draft_dir.name}: already published (ad_id={meta_result['ad_id']}); use --force to re-publish")
            continue
        publish_draft(site, config, draft_dir, draft, campaign_id, adset_id, args.dry_run, env)
        published += 1

    print(f"done: {published} draft(s) published (all PAUSED — nothing activated)")


if __name__ == "__main__":
    try:
        main()
    except PublishError as e:
        print(f"ERROR: {e}")
        sys.exit(e.code)
