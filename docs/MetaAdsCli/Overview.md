Today we're introducing the Meta ads CLI, a command-line tool for developers to manage Meta ad campaigns. Developers and AI agents working with the Meta Marketing API can now create, edit, and analyze campaigns directly from the command line, without writing custom code.

Why we built the ads CLI
Developers tell us the Meta Marketing API is powerful, but using it programmatically means writing the same code many times: authentication, pagination, output formatting, and error handling. These repetitive tasks slow down development and make it harder to integrate ad management into automated workflows.

The ads CLI solves this by packaging the Meta Marketing API into one tool with predictable commands that both developers and AI agents can use reliably:

 meta ads campaign list 
 meta ads insights get --campaign_id COMPAIGN_ID --date-preset last_7d —-fields conversions,impressions
The CLI supports multiple output formats — including JSON and plain tab-separated values — allowing it to integrate seamlessly into existing workflows, whether debugging interactively or automating tasks via CI/CD pipelines.

What's in the ads CLI
Ad Creation and Management

Create, list, update, and delete campaigns, ad sets, ads, and creatives without leaving the terminal. Resources are created in PAUSED status by default, so nothing goes live until you are ready.

# Create a campaign with 50.00 budget (currency specified on ad account)

 meta ads campaign create --name "Summer Sale" --objective OUTCOME_SALES --daily-budget 5000 

# Create a corresponding adset

 meta ads adset create CAMPAIGN_ID --name "My Ad Set"
 --optimization-goal LINK_CLICKS --billing-event IMPRESSIONS 
 --bid-amount 500 --targeting-countries US 

# Create a creative with an image and CTA

 meta ads creative create --name "Hero Banner"
 --page-id 111222333 --image ./banner.jpg 
 --body "50% off everything!" --title "Shop Now"
 --link-url https://example.com/sale --call-to-action SHOP_NOW 

# Connect campaigns and creative together

 meta ads ad create ADSET_ID --name "Hero Banner Ad" --creative-id CREATIVE_ID 

# Go live

 meta ads campaign update CAMPAIGN_ID --status ACTIVE 
 meta ads adset update ADSET_ID --status ACTIVE 
 meta ads ad update AD_ID --status ACTIVE
Performance Insights

Query spend, impressions, CTR, ROAS, and more with flexible date ranges, breakdowns by age/gender/platform, and multiple aggregation levels:

# Campaign-level detail

 meta ads insights get --campaign_id COMPAIGN_ID --fields=impressions,conversions --date-preset last_7d
Catalog Creation and Management

Create and manage catalogs, products, and product sets.

# Create a catalog

 meta ads catalog create --name "My Catalog"

# Add products to the catalog

 meta ads product-item create --catalog-id 123456 
 --retailer-id sku_a --name "Blue Shirt"
 --url https://example.com/blue_shirt --price "999" --currency "USD"
 --image-url https://example.com/blue_shirt.jpg

# List product sets

 meta ads product-set list --catalog-id 123456
Datasets
Create conversion pixels, connect them to ad accounts and product catalogs, and set up end-to-end conversion tracking.

meta ads dataset create --name "Website Pixel"
meta ads dataset connect 111222 --ad-account-id 333444 --catalog-id 555666
Built for Automation
meta ads is designed to run unattended in CI/CD pipelines, interactively in shell, and scripts:

Three output formats -- table (human-readable), json (pipe to jq), plain (tab-separated for sort, awk, cut)

--no-input and --force suppress all interactive prompts

Standard exit codes (0 success, 3 auth error, 4 API error, etc.) make error handling straightforward

Environment variables for tokens, secrets, and account IDs, keeping sensitive values out of command history and version control.

# Ads CLI


**Ads CLI is a command-line tool** for managing Meta advertising from your terminal. It provides a developer-friendly interface to the Meta Marketing API, so you can create ad campaigns from start to finish, manage product catalogs and Meta Pixels, and query performance insights. Ads CLI helps you build integrations and scale operations for your existing apps.

Ads CLI is built for developers who manage advertising programmatically:

- **Developers building ad management integrations** who want to prototype and test Marketing API workflows from the terminal before writing application code
- **Operations teams** who need to automate ad campaign creation, monitoring, and cleanup through scripts and CI/CD pipelines
- **AI agents and tools** that interact with Meta advertising through a structured command-line interface

## Key capabilities

### Full ad lifecycle management

Create, read, update, and delete resources across the entire Meta advertising hierarchy — ad campaigns, ad sets, ads, and ad creatives. Each resource supports the operations you need to manage it end-to-end.

| Resource | Operations |
|----------|------------|
| Ad Campaigns | `list`, `create`, `get`, `update`, `delete` |
| Ad Sets | `list`, `create` (with targeting, Pixels, conversion tracking), `get`, `update`, `delete` |
| Ads | `list`, `create` (with tracking specs), `get`, `update`, `delete` |
| Ad Creatives | `list`, `create`, `get`, `update`, `delete` |
| Insights | `get` (with date ranges, breakdowns, and custom fields) |
| Product Catalogs | `list`, `create`, `get`, `update`, `delete` |
| Product Items | `list`, `create`, `get`, `update`, `delete` |
| Product Sets | `list`, `create`, `get`, `update`, `delete` |
| Datasets (Pixels) | `list`, `create`, `get`, `connect`, `disconnect`, `assign-user` |
| Ad Accounts | `list`, `get`, `current` |
| Facebook Business Pages | `list`, `get` |

### Performance insights

- Query ad performance data with flexible date ranges, breakdowns, and custom metrics
- Filter by ad campaign, ad set, or individual ad
- Sort and limit results for the data you need

### Product catalogs and conversion tracking

- Manage product catalogs for Advantage+ catalog ads
- Create datasets (Pixels) for conversion tracking
- Connect datasets to ad accounts and catalogs
- Assign user permissions on datasets

### Automation-ready

Ads CLI is designed for scripting and automation:

- `--no-input` and `--force` flags suppress interactive prompts for unattended operation
- Three output formats: `table` for interactive use, `json` for piping to `jq` and other tools, `plain` (tab-separated) for Unix pipelines
- Consistent exit codes (0-5) for reliable error handling in scripts
- `.env` file support for managing credentials across environments

## How it works

Ads CLI authenticates with a Meta system user access token and calls the Marketing API on your behalf. The command structure follows a noun-verb pattern:

```
meta ads <resource> <action> [options]
```

For example, `meta ads campaign list` lists your ad campaigns, and `meta ads creative create --name "My Ad" --page-id <PAGE_ID> --image ./banner.jpg` creates an ad creative.

All commands require an ad account ID, which you can set once as an environment variable or pass per-command. Ads CLI resolves business IDs for catalog and dataset operations from your ad account when possible.

edit 
