# Tutorials and Recipes


Learn how to find the IDs you need, create your first ad campaign end-to-end, automate workflows with scripts, and clean up resources.

- [Find your IDs](#find-your-ids)
- [Your first ad campaign (end-to-end)](#your-first-ad-campaign-end-to-end)
- [Scripts and automation](#scripts-and-automation)
- [Cleanup: delete resources](#cleanup-delete-resources)


## Find your IDs

### Ad account ID

```
meta ads adaccount list
```

Look for the `id` column.

Set it with:

```
export AD_ACCOUNT_ID=<AD_ACCOUNT_ID>
```

### Facebook Business Page ID

Use the Business Page ID when creating ad creatives with the `--page-id` flag. You can also find Business Page IDs in Business Settings. These can only be Pages that are associated with a business the system user has access to.

```
meta ads page list
```

### Business ID

Ads CLI typically resolves the business ID automatically from your ad account. If needed, set it explicitly:

```
export BUSINESS_ID=<BUSINESS_ID>
```


## Your first ad campaign (end-to-end)

This walkthrough creates a complete ad setup: ad campaign, ad set, ad creative, and ad.

### 1. Authenticate and configure

Generate a system user token (see [Get Started](https://developers.facebook.com/documentation/ads-commerce/ads-ai-connectors/ads-cli/setup/get-started)), then configure it:

```
# Set your access token
export ACCESS_TOKEN=<ACCESS_TOKEN>

# Find your ad account
meta ads adaccount list

# Set it for the session
export AD_ACCOUNT_ID=<AD_ACCOUNT_ID>
```

### 2. Find your Business Page ID

Every ad creative needs a Business Page as its identity:

```
meta ads page list
```

Save the returned `id` for the Business Page you want to use.

### 3. Create an ad campaign

```
meta ads campaign create \
  --name "My First Campaign" \
  --objective OUTCOME_TRAFFIC \
  --daily-budget 5000
```

Save the returned ad campaign ID to create your ad set.

### 4. Create an ad set

```
meta ads adset create <CAMPAIGN_ID> \
  --name "US Audience" \
  --optimization-goal LINK_CLICKS \
  --billing-event IMPRESSIONS \
  --targeting-countries US
```

You can omit the budget here because the ad campaign already has a daily budget (campaign budget optimization). Save the returned ad set ID to create your ad.

### 5. Create an ad creative

```
meta ads creative create \
  --name "Hero Banner" \
  --image ./banner.jpg \
  --page-id <PAGE_ID> \
  --body "Check out our latest deals!" \
  --title "Shop Now" \
  --link-url https://example.com/sale \
  --call-to-action SHOP_NOW
```

Save the returned ad creative ID to create your ad.

### 6. Create an ad

```
meta ads ad create <AD_SET_ID> \
  --name "Hero Banner Ad" \
  --creative-id <CREATIVE_ID>
```

### 7. Activate your ad

Ads CLI creates everything in `PAUSED` status by default. When ready to go live, run:

```
meta ads campaign update <CAMPAIGN_ID> --status ACTIVE
meta ads adset update <AD_SET_ID> --status ACTIVE
meta ads ad update <AD_ID> --status ACTIVE
```


## Scripts and automation

Ads CLI supports scripting with `--no-input`, `--force`, and structured output.

### Environment-based configuration

For details on environment variables and configuration precedence, see [Configuration](https://developers.facebook.com/documentation/ads-commerce/ads-ai-connectors/ads-cli/setup/configuration).

```
# CI/CD pipeline example
export ACCESS_TOKEN="$META_SYSTEM_USER_TOKEN"
export AD_ACCOUNT_ID=<AD_ACCOUNT_ID>
export BUSINESS_ID=<BUSINESS_ID>  # Inferred from ad account if missing

meta --output json ads campaign list
```

### Non-interactive mode

Use `--no-input` and `--force` to suppress all prompts:

```
meta --no-input ads campaign delete <CAMPAIGN_ID> --force
```

### JSON output for scripts

```
# Retrieve ad campaign IDs
CAMPAIGN_IDS=$(meta --output json ads campaign list | jq -r '.[].id')

# Iterate over ad campaigns
for id in $CAMPAIGN_IDS; do
  echo "Processing ad campaign $id"
  meta ads insights get --campaign-id "$id" --fields conversions,purchase_roas
done
```

### Check exit codes

```
meta ads campaign list
if [ $? -eq 3 ]; then
  echo "Not authenticated -- add token to .env"
fi
```

| Exit Code | Meaning |
|-----------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Usage / argument error |
| 3 | Authentication error |
| 4 | API error |
| 5 | Resource not found |


## Cleanup: delete resources

### Delete resources

Deleting an ad campaign automatically cascades to its child ad sets and ads. Deleting an ad set cascades to its child ads. You can also delete individual resources directly.

```
# Delete a single ad
meta ads ad delete <AD_ID> --force

# Delete an ad set (and its ads)
meta ads adset delete <AD_SET_ID> --force

# Delete an ad campaign (and all its ad sets and ads)
meta ads campaign delete <CAMPAIGN_ID> --force

# Delete an ad creative
meta ads creative delete <CREATIVE_ID> --force
```

### Disconnect a dataset from an ad account

```
meta ads dataset disconnect <PIXEL_ID> --ad-account-id <AD_ACCOUNT_ID> --force
```

### Delete a catalog

```
meta ads catalog delete <CATALOG_ID> --force
```

