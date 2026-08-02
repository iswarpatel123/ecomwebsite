# Ad Publishing Workflow — V1 (Implementer Spec)

**Scope:** V1 only. Competitor scrape → rank/top-10 creatives → AI image+copy drafts → human verify (+ manual video) → publish as **Meta Ads drafts (PAUSED)**.
**Out of scope (V2):** LangGraph orchestration, auto video edit, auto competitor discovery, CI-triggered publishing.

> **Status: IMPLEMENTED (V1).** `scripts/ads_collect_site.py` (Stage 1 wrapper), `scripts/ads_publish_drafts.py` (Stage 4), the `-o/--out` flag on `scripts/agnes-image-to-image.cjs` (Stage 2), the `sites/furniture/ads/` scaffolding, and the `.gitignore` rules are all in place. The collector is the **fork** `https://github.com/iswarpatel123/MetaAdsCollector` (branch `fixes`) — cloned to `./MetaAdsCollector` as the pip editable source; it also fixes the double-fetch in `scripts/MetaAdsCollector.py` via a single-pass `collect_with_media()`. Remaining gaps are operational (real Meta IDs/token, competitor page IDs, product assets).

---

## Pipeline (4 stages)

```
1 collect  →  2 draft (AI)  →  3 human gate  →  4 publish (draft/PAUSED)
```

| Stage | Owner | Input | Output |
|-------|--------|--------|--------|
| 1 Collect | `scripts/ads_collect_site.py` (preferred thin wrapper around `MetaAdsCollector.py`) | `sites/<slug>/ads/config.json` | competitor JSONL + media under site |
| 2 Draft | LLM agent + image edit API | top creatives + our product assets | `drafts/<id>/draft.json` + images |
| 3 Human | operator | drafts | set `status: ready` or drop; drop video files + edit prompts |
| 4 Publish | `scripts/ads_publish_drafts.py` (local CLI, operator-run only) | ready drafts + Meta tokens | Meta Ad objects **PAUSED**; write back `meta_ids` |

Do **not** auto-activate ads in V1. Do **not** wire publish into CI in V1.

---

## Account / Page / Campaign topology

- **One Meta Business Manager, one ad account, one Page** shared across all sites. Sites are differentiated by campaign, not by account or page.
- **One campaign per site by default**, created idempotently (`list by name → reuse campaign_id`, no duplicate create). If a name lookup returns **more than one** campaign, the publish script must **error out**, not silently take the first — Meta does not enforce unique campaign names.
- Campaign naming: `ecom-<slug>` for the default/always-on campaign.
- **Known risk of one shared Page across all niches:** every site's ads run under a single Page identity, which hurts ad relevance/quality scores, muddies brand signals, and ties all 100+ niches together in the public Ad Library. Acceptable for V1; **per-niche Pages are the expected V2 migration**. The `ecom-<slug>` campaign naming is what keeps sites separable when that split happens.
- **Schema is 1:many (site → campaigns)**, not 1:1, so a site can later get a second campaign (e.g. a seasonal push) without a migration. Each campaign entry carries a `purpose` tag:
  - `always-on` — the default V1 campaign, created once, ads flow into it continuously.
  - `seasonal` / other — reserved for V2+, not created in V1.
- V1 only ever creates the `always-on` campaign per site. The array shape exists now so V2 doesn't require a schema/config migration.

```json
"meta": {
  "ad_account_id": "act_XXX",
  "page_id": "OUR_SHARED_PAGE_ID",
  "instagram_actor_id": null,
  "pixel_id": null,
  "campaigns": [
    {
      "purpose": "always-on",
      "campaign_id": null,
      "default_adset_id": null
    }
  ]
}
```

- **One ad set per campaign in V1**: `ecom-<slug>-default` — US only, `LINK_CLICKS`-style targeting isn't needed since objective is Sales (see below), placeholder daily budget until real spend starts.
- Ad sets, not new campaigns, are the unit of iteration/testing (audiences, placements, budget). New campaigns are reserved for genuinely different objectives or budgets that need independent kill-switches.

---

## Campaign defaults

- **Objective: `OUTCOME_SALES` from the first campaign create.** No traffic-objective phase — since the Meta Pixel (+ Conversions API) is being implemented before any spend, there's no reason to start on Traffic and switch later (switching objective on a live campaign disrupts the learning phase).
- **Pixel / Conversions API is a prerequisite, not a parallel-track nice-to-have.** Publish script must refuse to create a Sales-objective campaign if `pixel_id` is null in config — fail fast rather than create a campaign that can't optimize.
- Conversions API (server-side) should hook into the existing shared Cloudflare Function checkout backend, not per-site — same place Stripe logic already lives — so event submission is centralized and consistent across all 100+ storefronts.
- **Geography: US only** for the default ad set.
- **Budget: placeholder daily budget** (e.g. $1 / 100 cents) on first create, to be manually raised per site once ready to actually spend. Publish script should treat this as a named constant, not hardcoded inline, so it's easy to find and raise later. **Note:** Use 100 cents as-is for V1. Ads are created PAUSED so no real spend occurs; this exists only to satisfy the API budget field.
- **Ad set optimization goal:** For `OUTCOME_SALES` campaigns, the ad set must use `--optimization-goal OFFSITE_CONVERSIONS` with `--pixel-id` and `--custom-event-type PURCHASE` to enable conversion tracking. This is configured at the ad set level, not the campaign level.

```json
"creative": {
  "cta": "SHOP_NOW",
  "link_caption": "example.com"
},
"campaign_defaults": {
  "objective": "OUTCOME_SALES",
  "countries": ["US"],
  "daily_budget_cents": 100
}
```

---

## Layout (per site)

```
sites/<slug>/
  ads/
    config.json                 # competitors + our Meta IDs + defaults
    competitors/
      <page_id>/
        latest.jsonl            # symlink or copy of last collect
        <run_ts>.jsonl
        session.json            # Ad Library session cookies (gitignored)
        media/                  # top-N downloaded creatives only
          <ad_id>/
            0.jpg | 0.mp4 | …
            meta.json            # pointers into JSONL row (see schema below)
    products/                   # OUR product refs for image edit (local paths)
      manifest.json             # product_id → image paths, name, pdp url
    drafts/
      <draft_id>/
        draft.json              # publishable schema (below) — committed to git
        source/                 # optional copy of competitor creative used
        out/                    # AI-edited images — NOT committed
        video/                  # human drops final mp4 here (optional) — NOT committed
        video_prompt.md         # AI writes edit brief; human uses offline — committed
        REVIEW.md               # checklist for operator — committed
```

### `media/<ad_id>/meta.json` schema (creative metadata)

```json
{
  "ad_id": "2207230086481419",
  "jsonl_line": 3,
  "files": ["0.jpg"],
  "source_url": "https://facebook.com/ads/library/2207230086481419"
}
```

Points to the JSONL row and lists all downloaded files.

**Rule:** no more global `scripts/ads_output/` for production runs. Keep script default for ad-hoc/debug only.

### Git policy

- **Commit:** `config.json`, `products/manifest.json`, `draft.json`, `video_prompt.md`, `REVIEW.md` — all text, all small, useful for PR review and audit trail of what was drafted/published.
- **Do not commit:** `drafts/*/out/*` (AI-edited images), `drafts/*/video/*` (final video files), `competitors/**/media/*`, `competitors/**/session.json`.

```gitignore
sites/*/ads/competitors/**/session.json
sites/*/ads/competitors/**/media/**
sites/*/ads/drafts/**/out/**
sites/*/ads/drafts/**/video/**
sites/*/ads/drafts/**/source/**
```

---

## Config: `sites/<slug>/ads/config.json`

```json
{
  "slug": "furniture",
  "destination_url_base": "https://example.com",
  "competitors": [],
  "collect": {
    "country": "US",
    "status": "active",
    "sort_by": "impressions",
    "max_per_page": 10,
    "download_media": true
  },
  "meta": {
    "ad_account_id": "act_XXX",
    "page_id": "OUR_SHARED_PAGE_ID",
    "instagram_actor_id": null,
    "pixel_id": null,
    "campaigns": [
      { "purpose": "always-on", "campaign_id": null, "default_adset_id": null }
    ]
  },
  "creative": {
    "cta": "SHOP_NOW",
    "link_caption": "example.com"
  },
  "campaign_defaults": {
    "objective": "OUTCOME_SALES",
    "countries": ["US"],
    "daily_budget_cents": 100
  }
}
```

**`competitors: []` ships empty.** Real competitor Page IDs are a per-site content task, sourced by the operator (you) when a specific site is actually being built — not part of the workflow scaffold. This is the same pattern as `products/manifest.json`, which also starts empty and is filled in once real products/suppliers are chosen for that niche. No page ID list is needed to consider the workflow itself "done."

**Assumptions (override if wrong):** top_n = 10; rank = library `SORT_IMPRESSIONS` (already used in `MetaAdsCollector.py`); one `always-on` campaign + one default adset per site for V1.

---

## Stage 1 — Collect (code changes)

**Existing:** `scripts/MetaAdsCollector.py` → `scripts/ads_output/{page_id}_*.jsonl`, optional `--creative-dir`, `sort_by=SORT_IMPRESSIONS`, `--max-results`.

**Change to implement:**

1. **Preferred: a thin wrapper** `scripts/ads_collect_site.py` that reads `sites/<slug>/ads/config.json`, loops `competitors[].page_id`, and shells out to the existing single-page `MetaAdsCollector.py` per page with `--output-dir sites/<slug>/ads/competitors/<page_id>` and `--creative-dir media`, then copies the newest `*.jsonl` to `latest.jsonl`. This leaves the working collector untouched. (Alternative: add `--site` mode directly to `MetaAdsCollector.py` — more invasive.)
   - Session path: `.../session.json` (not global ads_output)
   - Always download media for those top N into `media/<ad_id>/`
2. Write/update `latest.jsonl` after each run.
3. Optional: `--page-id` alone keeps old global path for debugging.
4. Fix double-fetch: today creatives re-call `collect()` after `collect_to_jsonl` — download from written JSONL instead (token/rate savings).

**Ranking:** rely on API sort impressions + `max_results=top_n`. The wrapper maps config `"impressions"` -> collector `SORT_IMPRESSIONS`.

**Note:** with `competitors: []` as the shipped default, this stage is a no-op until the operator fills in real page IDs per site — expected and fine.

**Implementation detail:** `scripts/MetaAdsCollector.py` now accepts `--session-file` (site wrapper passes `session.json`) and uses `collect_with_media()` in a single pass when `--creative-dir` is set, so creatives are downloaded from the same search that wrote the JSONL instead of a second `collect()` call. The wrapper then reorganizes flat downloads into `media/<ad_id>/0.ext` and writes `media/<ad_id>/meta.json` (`{ad_id, jsonl_line, files, source_url}`) from the JSONL rows.

---

## Stage 2 — AI drafts (agent brief, not a big framework)

**Trigger:** human or main agent: "draft ads for `sites/<slug>`".

**Inputs the agent must load:**
- `config.json`
- each competitor `latest.jsonl` + `media/`
- `products/manifest.json` + site storefront copy (routes, product names)
- image edit tool (Agnes image-to-image script — see Stage 2 note below)

**Per selected ad (image creatives only auto-edit):**
1. Pick our product image(s) that match category.
2. Image edit via `scripts/agnes-image-to-image.cjs`: the script accepts `-i/--image` (a file path directly, no base64 piping needed), `-p/--prompt`, `-s/--size`, `-r/--ratio`, `-m/--model` (default `agnes-image-2.1-flash`). The only missing piece is `-o/--out` to write the result to disk instead of printing base64 to stdout. Once wired, call it like:
   ```bash
   node scripts/agnes-image-to-image.cjs \
     -i competitors/<page_id>/media/<ad_id>/0.jpg \
     -p "Replace competitor product with ours; keep layout/lighting; remove competitor logos/URLs" \
     -o out/0.jpg
   ```
3. Rewrite primary text / headline / description to our brand; **link_url** → our PDP from manifest.
4. Write `drafts/<draft_id>/draft.json` + `out/*` + `REVIEW.md`.
5. If source is **video**: do **not** auto-edit. Download/keep source ref, write `video_prompt.md` (shot list + replacement instructions), leave `video/` empty, set `status: needs_video`.

**Note on media upload:** The Meta Ads CLI automatically handles media upload when creating ad creatives with `--image` or `--video` flags. The publish script doesn't need separate upload logic — just pass the local file path to `meta ads creative create` and the CLI uploads it to the ad account automatically.

**Carousel:** supported when competitor source has multiple cards. One Agnes call per card → `out/0.jpg … out/N.jpg`, referenced in `draft.json` as multiple `assets`. Cap at 5 cards (cost control — carousels are N× image API calls). 

**Carousel implementation via CLI:** The Meta Ads CLI supports Dynamic Creative Optimization (DCO) with multiple images using the plural `--images` flag (up to 10 images). DCO automatically tests combinations and can achieve similar outcomes to carousel format. If true carousel format is specifically required (multiple swipeable cards in a single ad), use raw Graph API as a fallback since the CLI's DCO is optimized for automated combination testing rather than manual carousel sequencing.

**`draft_id`:** `{page_id}_{ad_id}_{short_hash}` — deterministic ID for idempotent re-publish.

### `draft.json` schema (publish contract)

```json
{
  "schema_version": 1,
  "draft_id": "1514_220723_a1b2",
  "site": "furniture",
  "status": "pending_review",
  "source": {
    "competitor_page_id": "151402834721433",
    "competitor_ad_id": "2207230086481419",
    "creative_index": 0
  },
  "creative": {
    "format": "image | video | carousel",
    "primary_text": "...",
    "headline": "...",
    "description": "...",
    "link_url": null,
    "cta_type": "SHOP_NOW",
    "assets": [
      { "type": "image", "path": "out/0.jpg" }
    ]
  },
  "publish": {
    "campaign_purpose": "always-on",
    "campaign_id": null,
    "adset_id": null,
    "ad_name": "furniture | sofa | 220723 | v1",
    "status": "PAUSED"
  },
  "meta_result": { "creative_id": "...", "ad_id": "...", "uploaded_hashes": ["..."] }
}
```

`meta_result` is `null` until published; after publish it's populated with Meta IDs. Paths in `assets` are **relative to the draft folder**. The schema shows the populated form.

`link_url`: nullable while `pending_review` / `needs_video`; publish script must refuse if blank when `status: ready`.

Valid values for `status` are: `pending_review`, `needs_video`, `ready`, `published`, `rejected`. (Do not copy a literal string like `"pending_review | needs_video | ..."` into the schema.)

`publish.campaign_purpose` selects which entry in `meta.campaigns[]` to publish under — defaults to `"always-on"`, forward-compatible with future `seasonal` campaigns per F.

---

### `products/manifest.json` schema (product reference)

```json
{
  "products": [
    {
      "product_id": "sofa-001",
      "name": "Milano 3-Seat Sofa",
      "category": "sofas",
      "pdp_url": "https://example.com/products/milano-3-seat-sofa",
      "images": ["products/sofa-001/0.jpg", "products/sofa-001/1.jpg"]
    }
  ]
}
```

Each product entry maps to a directory in `sites/<slug>/ads/products/` containing its images. The Stage 2 draft agent loads this to pick product images matching the competitor ad's category.

---

## Stage 3 — Human gate

Operator:
1. Open `drafts/*/REVIEW.md` + images.
2. Drop final video into `video/final.mp4` when `needs_video`; point `creative.assets` at it (or agent helper updates paths).
3. Set `"status": "ready"` only when OK, and confirm `link_url` is filled in.
4. Rejected → `"status": "rejected"` (publish script skips).

**Publish script must refuse** anything not `ready`, and refuse `ready` drafts with a blank `link_url`.

---

## Stage 4 — Publish script

**New:** `scripts/ads_publish_drafts.py`

```bash
python scripts/ads_publish_drafts.py --site furniture [--draft-id ID] [--dry-run] [--force]
```

**Execution model: local CLI, operator-invoked only.**
No CI integration in V1 — no scheduled/automated publish, no Meta token stored as a CI secret. The script is always run by hand (or via a coding-agent session) from the operator's machine using the local `.env`. This keeps secret management simple and preserves the human gate as a real gate, not a formality before automation takes over. CI-triggered publishing is an explicit V2+ consideration once the pipeline is trusted end to end.

**Behavior:**
1. Load config `meta.*` + env: `ACCESS_TOKEN` (never commit).
2. On first publish for a site: create the `always-on` campaign (`ecom-<slug>`, `OUTCOME_SALES`, paused) and default ad set (`ecom-<slug>-default`, US, placeholder daily budget, with conversion tracking) if `campaign_id`/`default_adset_id` are null in config; write IDs back. Idempotent — list-by-name before create, never duplicate.
3. Refuse to create/publish under `OUTCOME_SALES` if `pixel_id` is null in config.
4. Scan `drafts/*/draft.json` where `status==ready` and `link_url` is non-empty.
5. Upload image/video to Ad Account via CLI (automatic when creating creatives with `--image` or `--video`).
6. Create Ad Creative → Ad under the resolved campaign/adset (via `publish.campaign_purpose` → `meta.campaigns[]` lookup).
7. Force ad `status=PAUSED` (draft mode) — always, regardless of objective or campaign state (CLI default is PAUSED, but explicitly enforce).
8. Write `meta_result: { creative_id, ad_id, uploaded_hashes }` and set `status: published`.

**API surface — use Meta Ads CLI directly.**
The script should shell out to the **Meta Ads CLI** (`meta ads <resource> <action>`) and parse JSON output. The CLI is well-suited for this integration:

- **PAUSED-by-default**: All resources (campaigns, ad sets, ads) are created PAUSED unless `--status ACTIVE` is explicitly passed
- **Structured JSON output**: Use `--output json` for programmatic parsing
- **Automation-ready**: `--no-input` and `--force` flags suppress interactive prompts
- **Standard exit codes**: 0 (success), 3 (auth error), 4 (API error), 5 (not found)

**Key CLI commands for the publish script:**

```bash
# List campaigns (for idempotent campaign creation)
meta --output json ads campaign list

# Create campaign (PAUSED by default)
meta ads campaign create --name "ecom-furniture" \
  --objective OUTCOME_SALES --daily-budget 100

# Create ad set (PAUSED by default)
meta ads adset create <CAMPAIGN_ID> --name "ecom-furniture-default" \
  --optimization-goal OFFSITE_CONVERSIONS --billing-event IMPRESSIONS \
  --pixel-id <PIXEL_ID> --custom-event-type PURCHASE \
  --targeting-countries US --daily-budget 100

# Create ad creative (standard single image)
meta ads creative create --name "furniture | sofa | 220723 | v1" \
  --page-id <PAGE_ID> --image ./out/0.jpg \
  --body "Primary text" --title "Headline" \
  --link-url https://example.com/product \
  --description "Description" --call-to-action SHOP_NOW

# Create ad (PAUSED by default)
meta ads ad create <AD_SET_ID> --name "furniture | sofa | 220723 | v1" \
  --creative-id <CREATIVE_ID> --pixel-id <PIXEL_ID>

# Update campaign/adset/ad status
meta ads campaign update <CAMPAIGN_ID> --status ACTIVE
meta ads adset update <AD_SET_ID> --status ACTIVE
meta ads ad update <AD_ID> --status ACTIVE
```

**Note on campaign/adset parameters:**
- Budget is specified in **cents** (e.g., `100` = $1.00)
- For `OUTCOME_SALES` objective, use `--optimization-goal OFFSITE_CONVERSIONS` at the ad set level
- The CLI automatically uploads media files when creating creatives
- Use `--output json` and parse with jq or equivalent for ID extraction

**Pre-implementation validation steps (run before any bulk implementation):**
1. `meta auth status` to verify authentication with `ACCESS_TOKEN` in `.env`
2. Create `ecom-furniture` campaign with `OUTCOME_SALES`, PAUSED:
   ```bash
   meta ads campaign create --name "ecom-furniture" --objective OUTCOME_SALES --daily-budget 100
   ```
3. Create default ad set under it — US, placeholder budget, with conversion tracking:
   ```bash
   meta ads adset create <CAMPAIGN_ID> --name "ecom-furniture-default" \
     --optimization-goal OFFSITE_CONVERSIONS --billing-event IMPRESSIONS \
     --pixel-id <PIXEL_ID> --custom-event-type PURCHASE \
     --targeting-countries US --daily-budget 100
   ```
4. Single-image creative + ad:
   ```bash
   meta ads creative create --name "Test Creative" --page-id <PAGE_ID> \
     --image ./test.jpg --body "Test" --title "Test" \
     --link-url https://example.com --call-to-action SHOP_NOW
   meta ads ad create <AD_SET_ID> --name "Test Ad" --creative-id <CREATIVE_ID> --pixel-id <PIXEL_ID>
   ```
5. Multi-image/carousel creative — the CLI supports Dynamic Creative Optimization with `--images` (plural) for up to 10 images, or use raw Graph API if carousel format is specifically needed
6. Wire `ads_collect_site.py` collect paths and integrate full pipeline (Stage 1 uses wrapper).
7. Publish script (`ads_publish_drafts.py`) integration across Stages 2-4 — single-image creative upload, `--dry-run` output, PAUSED enforcement, config ID back-writing, and idempotency.

**Idempotency:** if `meta_result.ad_id` set, skip unless `--force`. Same idempotent-by-name logic applies to campaign/adset creation (step 2 above).

**Dry-run mode:** Implement `--dry-run` by printing the CLI commands that would be executed without actually running them. The script should use `--no-input` and `--output json` flags in dry-run mode for predictability. Example dry-run output:
```bash
# DRY-RUN: Would execute:
meta ads campaign create --name "ecom-furniture" --objective OUTCOME_SALES --daily-budget 100
meta ads adset create <CAMPAIGN_ID> --name "ecom-furniture-default" \
  --optimization-goal OFFSITE_CONVERSIONS --billing-event IMPRESSIONS \
  --pixel-id <PIXEL_ID> --custom-event-type PURCHASE \
  --targeting-countries US --daily-budget 100
meta ads creative create --name "furniture | sofa | 220723 | v1" \
  --page-id <PAGE_ID> --image ./out/0.jpg \
  --body "Primary text" --title "Headline" \
  --link-url https://example.com/product \
  --description "Description" --call-to-action SHOP_NOW
meta ads ad create <AD_SET_ID> --name "furniture | sofa | 220723 | v1" \
  --creative-id <CREATIVE_ID> --pixel-id <PIXEL_ID>
```

---

## Files to touch (checklist)

| Item | Action |
|------|--------|
| `docs/AdPublishingWorkflow.md` | this spec — status updated to IMPLEMENTED |
| `sites/<slug>/ads/config.json` | ✅ created for `furniture`, `competitors: []` |
| `sites/<slug>/ads/products/manifest.json` | ✅ created empty (`{ "products": [] }`) |
| `scripts/MetaAdsCollector.py` | ✅ `--session-file` arg; single-pass collect+media (fix double collect) |
| `scripts/ads_collect_site.py` | ✅ wrapper (config-driven, per-page output, `latest.jsonl`, `media/<ad_id>/` + `meta.json`) |
| `scripts/agnes-image-to-image.cjs` | ✅ `-o/--out` wired to `saveBase64Image()` |
| `scripts/ads_publish_drafts.py` | ✅ new — idempotent campaign/adset create + PAUSED publish, `--dry-run`/`--force` |
| `.gitignore` | ✅ sessions, media, `out/`, `video/`, `source/`, `MetaAdsCollector/` |
| Agent prompt (optional) | ✅ `.pi/agents/ad-drafter.md` — stage-2 brief, no LangGraph |

---

## Non-goals / guardrails

- No live spend / ACTIVE ads from scripts — always `PAUSED`.
- No scraping outside Ad Library collector already used.
- Do not copy competitor trademarks into final creatives (strip logos in edit prompt).
- Videos: prompt + human only in V1.
- Do not block storefront SSG on ads folders (`ads/` is data, not app routes).
- No CI-triggered publish in V1 — operator-run only.
- No `OUTCOME_SALES` campaign creation without a configured `pixel_id`.

---

## CLI setup requirements

**Installation:**
```bash
pip install meta-ads
```

**Environment configuration:**
The publish script expects these environment variables (set in `.env` or exported):
- `ACCESS_TOKEN` — Meta system user access token (not `META_ACCESS_TOKEN`)
- `AD_ACCOUNT_ID` — Ad account ID in format `act_XXX` or numeric ID

**Authentication verification:**
```bash
meta auth status
```

**Required token scopes:**
- `business_management`
- `ads_management`
- `pages_show_list`
- `pages_read_engagement`
- `pages_manage_ads`
- `catalog_management`
- `read_insights`

**System user setup:**
The script requires an admin system user with access to:
- The ad account specified in `AD_ACCOUNT_ID`
- The Business Page specified in config `meta.page_id`
- The Meta Pixel specified in config `meta.pixel_id`

---

## Minimal acceptance tests

1. `scripts/ads_collect_site.py --site furniture` writes ≤10 ads + media under `sites/furniture/ads/competitors/<id>/` (once real page IDs are filled into config — no-op on empty `competitors: []`).
2. Sample `draft.json` with local `out/0.jpg` validates schema.
3. First publish run for a site creates `ecom-<slug>` campaign (`OUTCOME_SALES`, PAUSED) + default ad set, writes IDs back to config; second run does not duplicate. The campaign uses a placeholder daily budget of 100 cents ($1/day) — not a ready-to-spend amount.
4. Publish refuses to run if `pixel_id` is null.
5. `--dry-run` publish prints Graph/CLI calls without side effects. Agnes `-o/--out` is wired to `saveBase64Image()` and produces a real file at `out/0.jpg`. (Acceptance test 1 covers the wrapper path; test 5 covers the script fix.)
6. Live publish (staging account) creates a **PAUSED** ad; second run on same draft no-ops without `--force`. The campaign uses a placeholder daily budget of 100 cents ($1/day) — not a ready-to-spend amount.
7. `needs_video` / `pending_review` / blank-`link_url` drafts never publish.

---

## REVIEW.md template

Each `drafts/<draft_id>/REVIEW.md` ships with this checklist (pre-filled where possible).

```markdown
# REVIEW — {draft_id}

- [ ] Image: no competitor logos, watermarks, or URLs visible
- [ ] Image: our product is substituted, lighting/layout preserved
- [ ] Copy: primary text, headline, description match brand voice
- [ ] Link URL points to the correct PDP ({pdp_url})
- [ ] No trademarked competitor terms in copy
- [ ] Carousel (if any): ≤5 cards, all images look on-brand
- [ ] Video: if \`needs_video\`, final MP4 dropped into \`video/\` and `creative.assets` updated

Set `status` in `draft.json`: `ready` / `rejected`.
```

---

## video_prompt.md template

Written by the Stage 2 agent when source is video. Human uses it to produce `video/final.mp4` offline.

```markdown
# VIDEO EDIT BRIEF — {draft_id}

**Source:** competitor ad ({competitor_ad_id}), clip index 0
**Length:** {target_length}s (match source aspect ratio)

## Shots to keep
1. {shot_description_1}
2. {shot_description_2}

## Replacements
- {competitor_product} → {our_product} ({pdp_url})
- Remove competitor logos, URLs, and watermarks
- Keep lighting and camera motion intact

## Music/broll
- Preserve original audio track
- Drop any text overlays or competitor branding

## Output
Drop final MP4 at `drafts/{draft_id}/video/final.mp4`, then point `creative.assets` at it.