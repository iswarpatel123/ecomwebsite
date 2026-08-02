# Datasets and Catalogs


This guide covers managing datasets (Meta Pixels) and product catalogs with Ads CLI.

## Business ID resolution

Both catalog and dataset commands need a business ID. Ads CLI resolves it in this order:

1. `--business-id` flag
2. `BUSINESS_ID` environment variable
3. Automatically derived from your configured ad account

If none of these are available, the command will prompt you to provide one.

## Datasets

A dataset represents a [Meta Pixel](https://developers.facebook.com/docs/meta-pixel) or [Conversions API](https://developers.facebook.com/documentation/ads-commerce/conversions-api) endpoint. Use datasets to track events on your website, such as purchases, add-to-carts, and page views. Datasets are essential for conversion ad campaigns and retargeting.

### List datasets

```shell
# List from the ad account (default and fallback)
meta ads dataset list

# List from a specific business
meta ads dataset list --business-id <BUSINESS_ID>
```

The business ID is resolved automatically from your configured ad account. Set the `BUSINESS_ID` environment variable (see [Configuration](https://developers.facebook.com/documentation/ads-commerce/ads-ai-connectors/ads-cli/setup/configuration)) or use `--business-id` to specify one explicitly.

### Create a dataset

Before creating a dataset, a business admin must accept the [Meta business tools terms of service](https://www.facebook.com/legal/terms/businesstools/). Ads CLI prompts you to complete this step if needed (see [Meta Platform Terms](https://developers.facebook.com/terms/dfc_platform_terms/)).

```shell
meta ads dataset create --name "My Website Pixel"
meta ads dataset create --name "My Pixel" --business-id <BUSINESS_ID>
```

After creation, Ads CLI automatically assigns the authenticated user to the dataset with `ADVERTISE`, `ANALYZE`, and `EDIT` permissions.

### View dataset details

```shell
meta ads dataset get <PIXEL_ID>
meta --output json ads dataset get <PIXEL_ID>
```

### Connect a dataset

Connect datasets to ad accounts and/or product catalogs before using them.

#### Connect to an ad account

```shell
meta ads dataset connect <PIXEL_ID> --ad-account-id <AD_ACCOUNT_ID>
```

#### Connect to a product catalog (for conversion tracking on catalog products)

```shell
meta ads dataset connect <PIXEL_ID> --catalog-id <CATALOG_ID>
```

#### Connect to both in a single command

```shell
meta ads dataset connect <PIXEL_ID> --ad-account-id <AD_ACCOUNT_ID> --catalog-id <CATALOG_ID>
```

### Disconnect a dataset

Remove a dataset's connection to an ad account:

```shell
meta ads dataset disconnect <PIXEL_ID> --ad-account-id <AD_ACCOUNT_ID>
meta ads dataset disconnect <PIXEL_ID> --ad-account-id <AD_ACCOUNT_ID> --force
```

### Assign users

Grant a user permissions on a dataset:

```shell
# Assign yourself (default: ADVERTISE + ANALYZE)
meta ads dataset assign-user <PIXEL_ID>

# Assign a specific user
meta ads dataset assign-user <PIXEL_ID> --user-id <USER_ID>

# Grant specific permissions
meta ads dataset assign-user <PIXEL_ID> --tasks ADVERTISE --tasks ANALYZE --tasks EDIT
```

Available tasks: `ADVERTISE`, `ANALYZE`, `EDIT`, `UPLOAD`

### Use datasets in ad campaigns

Once a dataset is connected to your ad account, reference it when creating conversion ad sets and ads:

```shell
# Create a conversion ad set with Pixel tracking
meta ads adset create <CAMPAIGN_ID> --name "Purchase Conversions" \
  --optimization-goal OFFSITE_CONVERSIONS \
  --billing-event IMPRESSIONS \
  --pixel-id <PIXEL_ID> \
  --custom-event-type PURCHASE \
  --targeting-countries US

# Create an ad with Pixel tracking
meta ads ad create <AD_SET_ID> --name "Conversion Ad" \
  --creative-id <CREATIVE_ID> --pixel-id <PIXEL_ID>
```

## Product catalogs

Product catalogs hold your product inventory for Advantage+ catalog ads, shopping, and commerce. Catalogs are owned by a business.

### List catalogs

```shell
meta ads catalog list
meta ads catalog list --business-id <BUSINESS_ID>
meta ads catalog list --limit 50
```

### Create a catalog

```shell
meta ads catalog create --name "My Product Catalog"
meta ads catalog create --name "Hotel Inventory" --vertical hotels
```

The `--vertical` option specifies the type of products in the catalog.

**Available verticals:** `adoptable_pets`, `commerce` (default), `destinations`, `flights`, `generic`, `home_listings`, `hotels`, `local_service_businesses`, `offer_items`, `offline_commerce`, `transactable_items`, `vehicles`

### View catalog details

```shell
meta ads catalog get <CATALOG_ID>
meta --output json ads catalog get <CATALOG_ID>
```

### Update a catalog

```shell
meta ads catalog update <CATALOG_ID> --name "Renamed Catalog"
```

### Delete a catalog

```shell
meta ads catalog delete <CATALOG_ID>
meta ads catalog delete <CATALOG_ID> --force
```

**Note:** You cannot delete catalogs that have active product feeds or ads referencing them.

## Full workflow: set up conversion tracking

```shell
# 1. Create a dataset (Pixel)
meta ads dataset create --name "Website Pixel"
# Output: Created dataset 'Website Pixel' (ID: <PIXEL_ID>)

# 2. Connect the dataset to your ad account
meta ads dataset connect <PIXEL_ID> --ad-account-id <AD_ACCOUNT_ID>

# 3. (Optional) Connect to a catalog for product-level tracking
meta ads dataset connect <PIXEL_ID> --catalog-id <CATALOG_ID>

# 4. Create a conversion ad campaign
meta ads campaign create --name "Sales Campaign" --objective OUTCOME_SALES

# 5. Create a conversion ad set using a Pixel
meta ads adset create <CAMPAIGN_ID> --name "Purchase Optimization" \
  --optimization-goal OFFSITE_CONVERSIONS \
  --billing-event IMPRESSIONS \
  --pixel-id <PIXEL_ID> \
  --custom-event-type PURCHASE \
  --targeting-countries US

# 6. Create an ad creative and ad
meta ads creative create --name "Product Ad" --page-id <PAGE_ID> \
  --image ./product.jpg --body "Buy now!" \
  --link-url https://example.com --call-to-action SHOP_NOW

meta ads ad create <AD_SET_ID> --name "Product Ad" \
  --creative-id <CREATIVE_ID> --pixel-id <PIXEL_ID>
```
