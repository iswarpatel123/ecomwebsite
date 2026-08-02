# Insights


This guide covers how to query ad performance data with Ads CLI, including date ranges, breakdowns, custom metrics, and sorting.

## Query options

### Basic usage

```
# Account-level metrics for the last 30 days (default)
meta ads insights get

# Specific metrics
meta ads insights get --adset-id <AD_SET_ID> --fields spend,impressions,ctr,cpc
```

### Date ranges

#### Preset ranges

```
meta ads insights get --date-preset last_30d
meta ads insights get --date-preset yesterday
```

Available presets: `today`, `yesterday`, `last_3d`, `last_7d`, `last_14d`, `last_30d`, `last_90d`, `this_month`, `last_month` (same as the [Marketing API](https://developers.facebook.com/documentation/ads-commerce/marketing-api/reference/ad-account/insights))

#### Custom date range

```
meta ads insights get --since 2024-01-01 --until 2024-01-31
```

**Note:** `--since` and `--until` must be used together and override `--date-preset`.

### Time granularity

Control how results are broken down over time with `--time-increment`:

| Value | Description |
|-------|-------------|
| `all_days` (default) | Aggregate across the entire date range |
| `daily` | One row per day |
| `weekly` | One row per week |
| `monthly` | One row per month |

```
# Daily spend for the last 30 days
meta ads insights get --date-preset last_30d --time-increment daily --fields spend

# Weekly campaign performance
meta ads insights get --campaign-id <CAMPAIGN_ID> --time-increment weekly
```

### Breakdowns

Add demographic or placement dimensions with `--breakdown` (repeatable):

| Breakdown | Description |
|-----------|-------------|
| `age` | Age ranges |
| `gender` | Gender |
| `country` | Country |
| `publisher_platform` | Facebook, Instagram, Audience Network (see [Breakdowns](https://developers.facebook.com/documentation/ads-commerce/marketing-api/insights/breakdowns) for others) |
| `device_platform` | Mobile, desktop |
| `platform_position` | Feed, Stories, Reels |
| `impression_device` | Device type |

```
# Performance by age and gender
meta ads insights get --breakdown age --breakdown gender

# Platform comparison
meta ads insights get --breakdown publisher_platform --fields spend,impressions,ctr
```

### Filtering

Filter results to a specific ad campaign, ad set, or ad:

```
meta ads insights get --campaign-id <CAMPAIGN_ID>
meta ads insights get --adset-id <AD_SET_ID>
meta ads insights get --ad-id <AD_ID>
```

### Sorting

Sort results by a metric:

```
meta ads insights get --adset-id <AD_SET_ID> --sort spend_descending
meta ads insights get --adset-id <AD_SET_ID> --sort impressions_ascending

# Last 30 days, ad campaign level, sorted by spend
meta ads insights get --campaign-id <CAMPAIGN_ID> --date-preset last_30d --sort spend_descending
```

The format is `<metric>_ascending` or `<metric>_descending`.

### Custom fields

Specify which metrics to include with `--fields` (comma-separated):

```
meta ads insights get --fields spend,impressions,clicks,ctr,cpc,reach
meta ads insights get --fields spend,conversions,cost_per_conversion,purchase_roas
```

Default fields: `spend`, `impressions`, `clicks`, `ctr`, `cpc`, `reach`

Any valid [Meta Insights API](https://developers.facebook.com/documentation/ads-commerce/marketing-api/reference/ad-account/insights) field can be used. Common fields include:

| Field | Description |
|-------|-------------|
| `spend` | Total amount spent |
| `impressions` | Number of times ads were shown |
| `reach` | Number of unique users who saw the ad |
| `clicks` | Total clicks |
| `ctr` | Click-through rate |
| `cpc` | Cost per click |
| `cpm` | Cost per 1,000 impressions |
| `frequency` | Average number of times each person saw the ad |
| `conversions` | Number of conversions |
| `cost_per_conversion` | Cost per conversion |
| `purchase_roas` | Return on ad spend |

### Result limit

```
meta ads insights get --campaign-id <CAMPAIGN_ID> --limit 100    # Default: 50
```

## Full options reference

| Option | Default | Description |
|--------|---------|-------------|
| `--date-preset` | `last_30d` | Predefined date range |
| `--since` | | Start date (YYYY-MM-DD). Requires `--until` |
| `--until` | | End date (YYYY-MM-DD). Requires `--since` |
| `--time-increment` | `all_days` | Time granularity: `all_days`, `daily`, `weekly`, `monthly` |
| `--breakdown` | | Breakdown dimension (repeatable) |
| `--fields` | `spend,impressions,...` | Comma-separated list of metrics |
| `--campaign-id` | | Filter to an ad campaign |
| `--adset-id` | | Filter to an ad set |
| `--ad-id` | | Filter to an ad |
| `--sort` | | Sort order (for example, `spend_descending`) |
| `--limit` / `-l` | 50 | Maximum rows to return |