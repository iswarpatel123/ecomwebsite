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

## Shared checkout backend (TODO — not built)

Goal: **one** Stripe checkout service reused by every storefront (not one function per site).

1. Create e.g. `infra/checkout-api` (or a single Pages Function project) with:
   - `POST /checkout/session` — body: `{ siteId, lineItems[], successUrl, cancelUrl }` → Stripe Checkout Session → `{ url }`
   - `POST /webhooks/stripe` — verify signature, record order
2. Secrets: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` (one Stripe account or map `siteId` → keys).
3. CORS: allow each storefront origin (`*.pages.dev` + custom domains).
4. Sites: cart in client; “Checkout” → `fetch(CHECKOUT_API + '/checkout/session')` → `location.href = url`.
5. Env per site: `VITE_CHECKOUT_API_URL`, `VITE_SITE_ID`.
6. Deploy that Worker **once**; storefront deploys stay static-only.

Until then, storefronts are content/marketing only.

---

## Bootstrap empty site

```bash
./tools/init-site/init-site.sh <slug>
cd sites/<slug> && pnpm dev
```

Template already uses SSG `vite.config.ts`.

---

## Clone workflow (brief)

- Workspace: `.cloning/_template` → `.cloning/<slug>/`
- Agents: planner-extractor → section-worker → integrator → visual-qa → dom-functional-qa
- Validate: `pnpm --filter @dropshipping/site-<slug> run typecheck|build|test:visual|test:e2e`

```bash
pnpm install -D -w sites/<slug> @playwright/test pixelmatch pngjs sharp
npx playwright install chromium
```

---

## Monorepo scripts

```bash
pnpm --filter @dropshipping/site-furniture dev|build
npx turbo run build --filter="@dropshipping/site-furniture"
pnpm deploy:site furniture
```

Ignore `infra/saas-provision` for v1 (CF for SaaS — not used).
