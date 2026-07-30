## Run a site

```bash
cd sites/furniture && pnpm dev          # :3001
pnpm --filter @dropshipping/site-furniture build
```

Build = **SSG** (Nitro `static` + prerender). Output: `sites/<slug>/.output/public` (HTML/assets only — **no** Pages Functions / Workers for storefronts).

```bash
npx serve sites/furniture/.output/public   # local preview of static output
```

New routes: link them in the app (crawlLinks) or add to `prerender.routes` in that site’s `vite.config.ts`.

---

## Deploy storefronts (Cloudflare Pages, static)

One **Pages project per site**: `ecom-dropship-<slug>` (e.g. `ecom-dropship-furniture`).

```bash
export CLOUDFLARE_API_TOKEN=...   # Pages Edit
export CLOUDFLARE_ACCOUNT_ID=...

chmod +x scripts/deploy-site.sh
./scripts/deploy-site.sh furniture
# or: pnpm deploy:site furniture
```

First deploy creates the Pages project. URL: `https://ecom-dropship-furniture.pages.dev`.

**GitHub (optional):** push repo → secrets `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID` → workflow `.github/workflows/deploy.yml` deploys changed sites on `main`, or manual `workflow_dispatch` with `site=furniture`.

Custom domain: Pages project → Custom domains (no CF for SaaS required).

---

## Architecture (current plan)

| Layer | Hosting | Notes |
|--------|---------|--------|
| Storefronts `sites/*` | CF Pages **static only** | SSG; free page views; no Workers quota |
| Checkout API (shared) | **One** CF Worker/Pages Function | All sites call the same backend; not built yet |
| CF for SaaS / gateway Worker / per-site Functions | **Out of scope** | Do not use for v1 |

---

## Shared checkout backend (Implemented)

Goal: **one** Stripe checkout service reused by every storefront (not one function per site).

The checkout backend is implemented as a Cloudflare Worker at `infra/checkout-api` with the following characteristics:

1. **API Endpoints:**
   - `GET /health`: Returns `{ "status": "ok", "service": "shared-checkout-api" }` for simple health checks.
   - `POST /checkout/session`: Creates a checkout session.
     - **Request Body:**
       ```json
       {
         "siteId": "site_furn_01",
         "lineItems": [
           {
             "product": {
               "id": "p1",
               "name": "Modern Oak Dining Table",
               "price": 799.00,
               "sku": "FURN-OAK-TAB",
               "niche": "furniture"
             },
             "quantity": 1
           }
         ],
         "successUrl": "https://cozy-furniture.example.com/success",
         "cancelUrl": "https://cozy-furniture.example.com/cancel",
         "shippingRate": 15.00,
         "taxRate": 0.08
       }
       ```
     - **Response:** `{ "url": "https://...", "orderId": "ord_..." }`
     - **Behavior:**
       - Query the D1 `sites` database to dynamically fetch the `tenantId`. Fallback to preset mapping if D1 is not available.
       - Calculate the final totals using `@dropshipping/core-commerce`.
       - If D1 is present, insert a **pending** order to track began checkouts.
       - If `STRIPE_SECRET_KEY` is set to a real key (doesn't start with `mock_`), make a direct, high-performance HTTP call to the Stripe API (`/v1/checkout/sessions`) to build a real checkout session and return the Stripe URL.
       - Otherwise, return a **mock checkout session URL** (redirecting directly to `successUrl` with mock query parameters) for easy development and offline testing.
   - `POST /webhooks/stripe`: Handles webhook notifications from Stripe.
     - **Headers:** `Stripe-Signature`
     - **Behavior:**
       - Verifies the webhook signature using the native Web Crypto API (HMAC-SHA256) when a real `STRIPE_WEBHOOK_SECRET` is configured.
       - On `checkout.session.completed`, extracts the metadata (`siteId`, `tenantId`, `orderId`), and the customer/shipping details.
       - If D1 is bound, records the payment by upserting/updating the order status to `'paid'` and storing customer info, shipping addresses, and the payment intent transaction ID.

2. **Secrets Configuration (`wrangler.json` / wrangler secrets):**
   - `STRIPE_SECRET_KEY`: Stripe Private Secret API Key.
   - `STRIPE_WEBHOOK_SECRET`: Stripe Webhook Signature Secret.

3. **CORS Support:**
   - Dynamically reflects incoming origin if request comes from local, `.pages.dev` or custom domains, enabling seamless storefront calls without pre-flight blocks.

4. **Testing the checkout-api:**
   - Run tests specifically: `pnpm --filter @dropshipping/checkout-api test` or `npx vitest run infra/checkout-api`.

---

## Bootstrap empty site

```bash
./tools/init-site/init-site.sh <slug>
cd sites/<slug> && pnpm dev
```

Template already uses SSG `vite.config.ts`.

## Prerequisites (new laptop)

### Install Node.js
```bash
nvm install 26.5.0  # matches CI
nvm use 26.5.0
```

### Install pnpm
```bash
npm install -g pnpm
```

### Install Playwright
```bash
pnpm install -D -w @playwright/test
npx playwright install chromium
```

### Clone repo
```bash
git clone <repo-url> && cd ecomwebsite
```

---

## Clone workflow (brief)

- Workspace: `.cloning/_template` → `.cloning/<slug>/`
- Agents: planner-extractor → section-worker → integrator → visual-qa → dom-functional-qa
- Validate: `pnpm --filter @dropshipping/site-<slug> run typecheck|build|test:visual|test:e2e`

---

## Monorepo scripts

```bash
pnpm --filter @dropshipping/site-furniture dev|build
npx turbo run build --filter="@dropshipping/site-furniture"
pnpm deploy:site furniture
```

Ignore `infra/saas-provision` for v1 (CF for SaaS — not used).
