# Command Reference


Complete reference for all Ads CLI commands.

- [Global option flags](#global-option-flags)
- [Authentication](#authentication)
- [Ad accounts](#ad-accounts)
- [Facebook Business Pages](#facebook-business-pages)
- [Ad campaigns](#ad-campaigns)
- [Ad sets](#ad-sets)
- [Ads](#ads)
- [Ad creatives](#ad-creatives)
- [Datasets (Meta Pixels)](#datasets-meta-pixels)
- [Product catalogs](#product-catalogs)
- [Insights](#insights)

### Command syntax

- Ads commands follow the pattern `meta ads <resource> <action> [options]`
- Auth commands use `meta auth <action>`
- `<lowercase>` = fixed keyword (type exactly as shown)
- `<UPPER_CASE>` = placeholder (replace with your value)
- `[lowercase]` = optional keyword or group
- `--flag` = named option or parameter

---

## Global options

These options apply to all commands and must be placed before the subcommand when used:

```
meta [global options] ads <command> <subcommand> [options]
```

| Option | Short | Description |
|--------|-------|-------------|
| `--output <format>` | `-o` | Output format: `table` (default), `json`, `plain` |
| `--no-color` | | Disable colored output |
| `--no-input` | | Disable interactive prompts |
| `--debug` | | Enable debug output |
| `--help` | `-h` | Show help text |
| `--version` | `-v` | Show version |

#### Output formats

- **table** (default) -- Human-readable table with headers. Best for interactive use.
- **json** -- Structured JSON array. Ideal for piping to `jq` or other tools.
- **plain** -- Tab-separated values, one record per line. Works well with `cut`, `awk`, and `sort`.

```
# JSON output, pipe to jq
meta --output json ads campaign list | jq '.[].name'

# Plain output, sort by column
meta --output plain ads campaign list | sort -t$'\t' -k5 -rn
```

---

## Commands

### Authentication

Manage authentication with Meta.

Ads CLI authenticates using a Meta admin system user access token. See [Get Started](https://developers.facebook.com/documentation/ads-commerce/ads-ai-connectors/ads-cli/setup/get-started) for detailed setup instructions.

#### meta auth

Save your system user access token. Set the token in your `.env` file or as an environment variable:

```
# .env file
ACCESS_TOKEN=<ACCESS_TOKEN>

# Or export directly
export ACCESS_TOKEN=<ACCESS_TOKEN>
```

#### meta auth status

Check current authentication status. Shows a masked version of the stored token.

```
meta auth status
```

---

### Ad accounts

Manage ad accounts.

#### meta ads adaccount list

List all ad accounts the authenticated user has access to.

```
meta ads adaccount list
meta ads adaccount list --limit 50
meta --output json ads adaccount list
```

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--limit` | `-l` | 25 | Maximum number of accounts to return |

**Output columns:** `id`, `name`, `account_status`, `currency`, `timezone_name`

#### meta ads adaccount current

Show the currently configured ad account ID (from `--ad-account-id` or `AD_ACCOUNT_ID`).

```
meta ads adaccount current
```

---

### Facebook Business Pages

Manage Facebook Business Pages.

#### meta ads page list

List all Facebook Business Pages you have access to. Use Business Page IDs from this list with `--page-id` in ad creative commands.

```
meta ads page list
meta ads page list --limit 50
meta --output json ads page list
```

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--limit` | `-l` | 25 | Maximum number of Business Pages to return |

**Output columns:** `id`, `name`, `category`

---

### Ad campaigns

Manage ad campaigns.

#### meta ads campaign list

List ad campaigns in the ad account.

```
meta ads campaign list
meta ads campaign list --limit 25
meta --output json ads campaign list
```

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--limit` | `-l` | 10 | Maximum number of ad campaigns to return |

**Output columns:** `name`, `effective_status`, `id`, `objective`, `daily_budget`, `lifetime_budget`, `start_time`

#### meta ads campaign create

Create an ad campaign.

```
meta ads campaign create --name "My Campaign" --objective OUTCOME_TRAFFIC
meta ads campaign create --name "Sales Campaign" --objective OUTCOME_SALES \
  --daily-budget 5000
```

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--name` | Yes | | Name for the ad campaign |
| `--objective` | Yes | | Ad campaign objective |
| `--daily-budget` | No | | Daily budget in cents (for example, 5000 = $50.00) |
| `--lifetime-budget` | No | | Lifetime budget in cents |
| `--status` | No | `PAUSED` | Initial status: `ACTIVE` or `PAUSED` |

**Objectives:** `OUTCOME_APP_PROMOTION`, `OUTCOME_AWARENESS`, `OUTCOME_ENGAGEMENT`, `OUTCOME_LEADS`, `OUTCOME_SALES`, `OUTCOME_TRAFFIC`

#### meta ads campaign get

Get details for a specific ad campaign.

```
meta ads campaign get <CAMPAIGN_ID>
```

#### meta ads campaign delete

Delete an ad campaign and all its child ad sets and ads.

```
meta ads campaign delete <CAMPAIGN_ID>
meta ads campaign delete <CAMPAIGN_ID> --force    # Skip confirmation
```

| Option | Short | Description |
|--------|-------|-------------|
| `--force` | `-f` | Skip confirmation prompt |

#### meta ads campaign update

Update an ad campaign.

```
meta ads campaign update <CAMPAIGN_ID> --name "New Name"
meta ads campaign update <CAMPAIGN_ID> --status ACTIVE
meta ads campaign update <CAMPAIGN_ID> --daily-budget 10000
```

| Option | Description |
|--------|-------------|
| `--name` | New name for the ad campaign |
| `--status` | New status: `ACTIVE`, `PAUSED`, `ARCHIVED` |
| `--daily-budget` | New daily budget in cents |
| `--lifetime-budget` | New lifetime budget in cents |

**Note:** At least one option must be provided.

---

### Ad sets

Manage ad sets.

#### meta ads adset list

List ad sets. Optionally filter by ad campaign.

```
meta ads adset list                    # All ad sets in the ad account
meta ads adset list <CAMPAIGN_ID>        # Ad sets for a specific campaign
meta ads adset list --limit 25
```

| Argument | Required | Description |
|----------|----------|-------------|
| `<CAMPAIGN_ID>` | No | Filter to ad sets in this campaign |

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--limit` | `-l` | 10 | Maximum number of ad sets to return |

**Output columns:** `name`, `effective_status`, `id`, `optimization_goal`, `billing_event`, `daily_budget`, `lifetime_budget`, `start_time`

#### meta ads adset create

Create an ad set for an ad campaign.

```
meta ads adset create <CAMPAIGN_ID> --name "My Ad Set" \
  --optimization-goal LINK_CLICKS --billing-event IMPRESSIONS \
  --bid-amount 500 --targeting-countries US

# Conversion ad set
meta ads adset create <CAMPAIGN_ID> --name "Conversions Set" \
  --optimization-goal OFFSITE_CONVERSIONS \
  --billing-event IMPRESSIONS --pixel-id <PIXEL_ID> \
  --custom-event-type PURCHASE --targeting-countries US
```

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--name` | Yes | | Name for the ad set |
| `--optimization-goal` | Yes | | Optimization goal |
| `--billing-event` | Yes | | Billing event |
| `--daily-budget` | No | | Daily budget in cents. Omit if the ad campaign uses campaign budget optimization |
| `--lifetime-budget` | No | | Lifetime budget in cents. Requires `--end-time` |
| `--bid-amount` | No | | Bid amount in cents |
| `--start-time` | No | | Start time (ISO 8601) |
| `--end-time` | No | | End time (ISO 8601). Required with `--lifetime-budget` |
| `--status` | No | `PAUSED` | Initial status: `ACTIVE` or `PAUSED` |
| `--targeting-countries` | No | | Comma-separated country codes (for example, `US,CA,GB`) |
| `--pixel-id` | No | | Dataset (Pixel) ID for conversion tracking |
| `--custom-event-type` | No | `PURCHASE` | Conversion event type. Used with `--pixel-id` |

**Optimization goals:** `APP_INSTALLS`, `CONVERSATIONS`, `EVENT_RESPONSES`, `IMPRESSIONS`, `LANDING_PAGE_VIEWS`, `LEAD_GENERATION`, `LINK_CLICKS`, `OFFSITE_CONVERSIONS`, `PAGE_LIKES`, `POST_ENGAGEMENT`, `REACH`, `THRUPLAY`, `VALUE`

**Billing events:** `APP_INSTALLS`, `CLICKS`, `IMPRESSIONS`, `LINK_CLICKS`, `PAGE_LIKES`, `POST_ENGAGEMENT`, `THRUPLAY`

**Custom event types:** `ADD_PAYMENT_INFO`, `ADD_TO_CART`, `ADD_TO_WISHLIST`, `COMPLETE_REGISTRATION`, `CONTACT`, `CONTENT_VIEW`, `CUSTOMIZE_PRODUCT`, `DONATE`, `FIND_LOCATION`, `INITIATED_CHECKOUT`, `LEAD`, `OTHER`, `PURCHASE`, `SCHEDULE`, `SEARCH`, `START_TRIAL`, `SUBMIT_APPLICATION`, `SUBSCRIBE`

#### meta ads adset get

Get details for a specific ad set.

```
meta ads adset get <AD_SET_ID>
```

#### meta ads adset delete

Delete an ad set and all its child ads.

```
meta ads adset delete <AD_SET_ID>
meta ads adset delete <AD_SET_ID> --force
```

| Option | Short | Description |
|--------|-------|-------------|
| `--force` | `-f` | Skip confirmation prompt |

#### meta ads adset update

Update an ad set.

```
meta ads adset update <AD_SET_ID> --name "New Name"
meta ads adset update <AD_SET_ID> --status ACTIVE
meta ads adset update <AD_SET_ID> --daily-budget 10000
```

| Option | Description |
|--------|-------------|
| `--name` | New name for the ad set |
| `--status` | New status: `ACTIVE`, `PAUSED`, `ARCHIVED` |
| `--daily-budget` | New daily budget in cents |
| `--lifetime-budget` | New lifetime budget in cents |
| `--bid-amount` | New bid amount in cents |
| `--end-time` | New end time (ISO 8601) |

**Note:** At least one option must be provided.

---

### Ads

Manage ads.

#### meta ads ad list

List ads. Optionally filter by ad set.

```
meta ads ad list                  # All ads in the ad account
meta ads ad list <AD_SET_ID>         # Ads for a specific ad set
meta ads ad list --limit 25
```

| Argument | Required | Description |
|----------|----------|-------------|
| `<ADSET_ID>` | No | Filter to ads in this ad set |

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--limit` | `-l` | 10 | Maximum number of ads to return |

**Output columns:** `name`, `effective_status`, `id`, `adset_id`, `campaign_id`, `created_time`

#### meta ads ad create

Create an ad in an ad set. An ad references an ad creative -- create the ad creative first with `meta ads creative create`.

```
meta ads ad create <AD_SET_ID> --name "My Ad" --creative-id <CREATIVE_ID>
meta ads ad create <AD_SET_ID> --name "Conversion Ad" --creative-id <CREATIVE_ID> \
  --pixel-id <PIXEL_ID>
```

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--name` | Yes | | Name for the ad |
| `--creative-id` | Yes | | ID of the ad creative to use |
| `--status` | No | `PAUSED` | Initial status: `ACTIVE`, `PAUSED` |
| `--pixel-id` | No | | Dataset (Pixel) ID for conversion tracking |
| `--tracking-specs` | No | | Tracking specs as raw JSON (mutually exclusive with `--pixel-id`) |

**Note:** Use `--pixel-id` **or** `--tracking-specs`, not both.

#### meta ads ad get

Get details for a specific ad.

```
meta ads ad get <AD_ID>
meta --output json ads ad get <AD_ID>
```

#### meta ads ad update

Update an ad.

```
meta ads ad update <AD_ID> --name "New Name"
meta ads ad update <AD_ID> --creative-id <CREATIVE_ID>
meta ads ad update <AD_ID> --status ACTIVE
```

| Option | Description |
|--------|-------------|
| `--name` | New name for the ad |
| `--creative-id` | New ad creative ID |
| `--status` | New status: `ACTIVE`, `PAUSED`, `ARCHIVED` |

**Note:** At least one option must be provided.

#### meta ads ad delete

Delete an ad.

```
meta ads ad delete <AD_ID>
meta ads ad delete <AD_ID> --force
```

| Option | Short | Description |
|--------|-------|-------------|
| `--force` | `-f` | Skip confirmation prompt |

---

### Ad creatives

Manage ad creatives. See the [Ad Creatives](https://developers.facebook.com/documentation/ads-commerce/ads-ai-connectors/ads-cli/ad-creatives) for detailed usage.

#### meta ads creative list

List ad creatives in the ad account.

```
meta ads creative list
meta ads creative list --limit 25
```

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--limit` | `-l` | 10 | Maximum number of ad creatives to return |

**Output columns:** `name`, `id`, `status`, `title`, `body`

#### meta ads creative create

Create an ad creative. Supports two modes: **standard** and **Dynamic Creative Optimization**.

##### Standard ad creative

Provide a single image or video with ad copy:

```
meta ads creative create --name "Summer Sale" --image ./banner.jpg \
  --page-id <PAGE_ID> --body "50% off everything!" \
  --link-url https://example.com --title "Shop Now" \
  --call-to-action SHOP_NOW
```

| Option | Required | Description |
|--------|----------|-------------|
| `--name` | Yes | Ad creative name |
| `--page-id` | Yes | Facebook Business Page ID to use as the ad's identity |
| `--image` | No | Path to an image file |
| `--video` | No | Path to a video file |
| `--body` | No | Primary text / ad copy |
| `--title` | No | Headline text below the image |
| `--link-url` | No | Destination URL when clicked |
| `--description` | No | Link description below the headline |
| `--call-to-action` | No | Call-to-action button type |
| `--instagram-actor-id` | No | Instagram account ID for Instagram placements |

Provide `--image` **or** `--video`, not both.

##### Dynamic Creative Optimization

Supply multiple assets and Meta automatically tests combinations:

```
meta ads creative create --name "DCO Creative" --page-id <PAGE_ID> \
  --link-url https://example.com \
  --images ./img1.jpg --images ./img2.jpg --images ./img3.jpg \
  --titles "Title A" --titles "Title B" \
  --bodies "Body 1" --bodies "Body 2" \
  --call-to-actions SHOP_NOW --call-to-actions LEARN_MORE
```

| Option | Max | Description |
|--------|-----|-------------|
| `--images` | 10 | Image file paths (repeat for each) |
| `--videos` | 10 | Video file paths (repeat for each) |
| `--titles` | 5 | Headline variations (repeat for each) |
| `--bodies` | 5 | Primary text variations (repeat for each) |
| `--descriptions` | 5 | Description variations (repeat for each) |
| `--call-to-actions` | 5 | Call-to-action types (repeat for each) |

Dynamic Creative Optimization requires `--link-url` and at least one `--images` or `--videos`.

**Call-to-action types:** `APPLY_NOW`, `BOOK_TRAVEL`, `BUY_NOW`, `CONTACT_US`, `DOWNLOAD`, `GET_OFFER`, `GET_QUOTE`, `LEARN_MORE`, `NO_BUTTON`, `OPEN_LINK`, `SHOP_NOW`, `SIGN_UP`, `SUBSCRIBE`, `WATCH_MORE`

See the [Ad Creatives](https://developers.facebook.com/documentation/ads-commerce/ads-ai-connectors/ads-cli/ad-creatives#dynamic-creative-optimization) for detailed examples and format selection logic.

#### meta ads creative get

Get details for a specific ad creative.

```
meta ads creative get <CREATIVE_ID>
meta --output json ads creative get <CREATIVE_ID>
```

#### meta ads creative update

Update an existing ad creative. Ads CLI changes only the fields you specify.

```
meta ads creative update <CREATIVE_ID> --name "New Name"
meta ads creative update <CREATIVE_ID> --body "Updated copy" --title "New Title"
meta ads creative update <CREATIVE_ID> --image ./new-banner.jpg
meta ads creative update <CREATIVE_ID> --status PAUSED
```

| Option | Description |
|--------|-------------|
| `--name` | New ad creative name |
| `--image` | New image file to upload |
| `--video` | New video file to upload |
| `--body` | New primary text |
| `--title` | New headline |
| `--link-url` | New destination URL |
| `--description` | New link description |
| `--call-to-action` | New call-to-action button type |
| `--instagram-actor-id` | New Instagram account ID |
| `--status` | New status: `ACTIVE` or `PAUSED` |

**Note:** Some fields cannot be updated after creation due to Meta API restrictions. In those cases, create a new ad creative instead.

#### meta ads creative delete

Delete an ad creative.

**Note:** Ad creatives in use by active ads cannot be deleted.

```
meta ads creative delete <CREATIVE_ID>
meta ads creative delete <CREATIVE_ID> --force
```

| Option | Short | Description |
|--------|-------|-------------|
| `--force` | `-f` | Skip confirmation prompt |

---

### Datasets (Meta Pixels)

Manage datasets (Meta Pixels / Conversions API). See [Datasets and Catalogs](https://developers.facebook.com/documentation/ads-commerce/ads-ai-connectors/ads-cli/datasets-and-catalogs#datasets) for detailed usage.

#### meta ads dataset list

List datasets. Lists from the business by default, or from the ad account as a fallback.

```
meta ads dataset list
meta ads dataset list --business-id <BUSINESS_ID>
meta ads dataset list --limit 50
```

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--business-id` | | | List datasets owned by this business |
| `--limit` | `-l` | 25 | Maximum number of datasets to return |

**Output columns:** `name`, `id`, `creation_time`, `last_fired_time`

#### meta ads dataset get

Get details for a specific dataset.

```
meta ads dataset get <PIXEL_ID>
```

#### meta ads dataset create

Create a dataset (Pixel) in a business. Ads CLI automatically assigns permissions.

```
meta ads dataset create --name "My Pixel"
meta ads dataset create --name "My Pixel" --business-id <BUSINESS_ID>
```

| Option | Required | Description |
|--------|----------|-------------|
| `--name` | Yes | Name for the dataset |
| `--business-id` | No | Business to create under (resolved from ad account if omitted) |

#### meta ads dataset connect

Connect a dataset to an ad account and/or product catalog.

```
meta ads dataset connect <PIXEL_ID> --ad-account-id <AD_ACCOUNT_ID>
meta ads dataset connect <PIXEL_ID> --catalog-id <CATALOG_ID>
meta ads dataset connect <PIXEL_ID> --ad-account-id <AD_ACCOUNT_ID> --catalog-id <CATALOG_ID>
```

| Option | Description |
|--------|-------------|
| `--ad-account-id` | Ad account to connect the dataset to |
| `--catalog-id` | Product catalog to connect the dataset to |
| `--business-id` | Business that owns the dataset (resolved if omitted) |

**Note:** At least one of `--ad-account-id` or `--catalog-id` is required.

#### meta ads dataset disconnect

Unshare a dataset from an ad account.

```
meta ads dataset disconnect <PIXEL_ID> --ad-account-id <AD_ACCOUNT_ID>
meta ads dataset disconnect <PIXEL_ID> --ad-account-id <AD_ACCOUNT_ID> --force
```

| Option | Short | Required | Description |
|--------|-------|----------|-------------|
| `--ad-account-id` | | Yes | Ad account to unshare from |
| `--business-id` | | No (inferred from ad account) | Business that owns the dataset |
| `--force` | `-f` | No | Skip confirmation prompt |

#### meta ads dataset assign-user

Assign a user to a dataset with specified permissions.

```
meta ads dataset assign-user <PIXEL_ID>
meta ads dataset assign-user <PIXEL_ID> --user-id <USER_ID>
meta ads dataset assign-user <PIXEL_ID> --tasks ADVERTISE --tasks ANALYZE --tasks EDIT
```

| Option | Default | Description |
|--------|---------|-------------|
| `--user-id` | Authenticated user | User ID to assign |
| `--tasks` | `ADVERTISE`, `ANALYZE` | Permissions to grant (repeat for multiple) |

**Available tasks:** `ADVERTISE`, `ANALYZE`, `EDIT`, `UPLOAD`

---

### Product catalogs

Manage product catalogs. See [Datasets and Catalogs](https://developers.facebook.com/documentation/ads-commerce/ads-ai-connectors/ads-cli/datasets-and-catalogs#product-catalogs) for detailed usage.

#### Group-level option

All catalog commands accept:

| Option | Default | Description |
|--------|---------|-------------|
| `--business-id` | Resolved from ad account | Business ID. Also reads `BUSINESS_ID` env var. |

If `--business-id` is not provided, Ads CLI resolves it from the configured ad account.

#### meta ads catalog list

List product catalogs for a business.

```
meta ads catalog list
meta ads catalog list --business-id <BUSINESS_ID>
meta ads catalog list --limit 50
```

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--limit` | `-l` | 25 | Maximum number of catalogs to return |

**Output columns:** `name`, `id`, `vertical`, `product_count`, `feed_count`

#### meta ads catalog get

Get details for a specific product catalog.

```
meta ads catalog get <CATALOG_ID>
```

#### meta ads catalog create

Create a product catalog.

```
meta ads catalog create --name "My Catalog"
meta ads catalog create --name "Hotel Catalog" --vertical hotels
```

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--name` | Yes | | Name for the catalog |
| `--vertical` | No | `commerce` | Catalog type |

**Verticals:** `adoptable_pets`, `commerce`, `destinations`, `flights`, `generic`, `home_listings`, `hotels`, `local_service_businesses`, `offer_items`, `offline_commerce`, `transactable_items`, `vehicles`

#### meta ads catalog update

Update a product catalog.

```
meta ads catalog update <CATALOG_ID> --name "Renamed Catalog"
```

| Option | Description |
|--------|-------------|
| `--name` | New name for the catalog |

#### meta ads catalog delete

Delete a product catalog.

```
meta ads catalog delete <CATALOG_ID>
meta ads catalog delete <CATALOG_ID> --force
```

| Option | Short | Description |
|--------|-------|-------------|
| `--force` | `-f` | Skip confirmation prompt |

---

### Insights

Query ad performance data. See [Insights](https://developers.facebook.com/documentation/ads-commerce/ads-ai-connectors/ads-cli/insights) for detailed usage.

#### meta ads insights get

Query ad performance insights with full control over fields, date range and breakdowns.

```
meta ads insights get
meta ads insights get --fields spend,impressions,ctr
meta ads insights get --since 2024-01-01 --until 2024-01-31
meta ads insights get --breakdown age --breakdown gender
meta ads insights get --campaign-id <CAMPAIGN_ID>
```

See [Insights](https://developers.facebook.com/documentation/ads-commerce/ads-ai-connectors/ads-cli/insights) for the full options reference.
