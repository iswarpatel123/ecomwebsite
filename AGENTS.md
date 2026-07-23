# Multi-Tenant Dropshipping Platform Monorepo

**pnpm** + **Turborepo**. Niche storefronts under `sites/*` deploy as **static Cloudflare Pages** (SSG). No CF for SaaS / per-site Workers for storefronts.

```
├── .github/workflows/    # Deploy changed sites to CF Pages
├── scripts/deploy-site.sh
├── packages/             # Shared libs (commerce, stripe-client, UI, …)
├── sites/                # Independent SolidStart SSG apps
└── infra/                # Future: shared checkout API, D1 (saas-provision unused for v1)
```

- **Storefronts:** Nitro `preset: "static"` + prerender → `sites/<slug>/.output/public`
- **Deploy:** `./scripts/deploy-site.sh <slug>` → Pages project `ecom-dropship-<slug>`
- **Checkout (planned):** one shared CF Function/Worker for all sites — see `notes.md`
