# Multi-Tenant Dropshipping Platform Monorepo

An enterprise-grade, high-performance monorepo scaffold built on **pnpm** and **Turborepo** for deploying dozens to hundreds of niche-specific dropshipping and reselling e-commerce websites independently to **Cloudflare Pages**.

## Architecture & Structural Choices

```
├── .github/              # Independent site-by-site CI workflows
├── /packages             # Shared packages (Core logic, UI primitives)
│   ├── config-validation # Zod schemas for multi-tenant configurations
│   ├── core-commerce     # Generic cart, order, and tax calculations
│   ├── stripe-client     # Stripe (and Braintree-ready) payment interfaces
│   ├── analytics         # Standardized tracking event abstractions
│   └── ui-primitives     # Generic, low-style UI atoms (Buttons, PriceFormatter)
├── /sites                # Niche-specific apps (NOT shared, custom-tailored layout/UX)
│   ├── furniture         # Furniture niche SolidStart app with Stripe checkout
│   └── saunas            # Saunas niche SolidStart app with custom configuration options
└── /infra                # Databases, DNS provisioning and maintenance
    ├── d1/               # SQL schemas for tenant sites, wholesaler catalogs, and orders
    └── saas-provision/   # Cloudflare for SaaS custom domain onboarding script
```

### Why Independent Cloudflare Pages?
- **Per-Niche Autonomy:** Each niche (furniture, saunas, grills) requires distinct layout formats, conversion-funnel psychology, and customer interactions. They are purposely kept decoupled.
- **Micro-Deployments:** Each site deploys to its own dedicated Cloudflare Pages project. Avoids the risk of a single deploy introducing regression on unrelated sites.
- **Scales gracefully:** Turborepo enables independent pipeline targeting, rebuilding, and deploying *only* the affected templates on commit.

---

## Shared Business Logic & UI Primitives

1. **`@dropshipping/config-validation`**: Zod runtime schema validator for site and tenant attributes. Consumed by Edge and serverless runtime loaders.
2. **`@dropshipping/core-commerce`**: Implements state utilities and standard formulas (like shipping formulas and tax matrices) that remain uniform across all tenant lines.
3. **`@dropshipping/stripe-client`**: Abstracted wrapper exposing payment operations. This decoupled approach allows dropshipper owners to easily opt-in to alternatives (e.g. Braintree) on high-ticket niches.
4. **`@dropshipping/analytics`**: Standard analytics router supporting GA tracking and proprietary tracking nodes.
5. **`@dropshipping/ui-primitives`**: Exposes foundational atomic components (e.g., custom button attributes, standard prices) while leaving site layouts completely isolated.

---

## Scaling to 100+ Sites: Future Routing Architecture

While deploying individual Cloudflare Pages projects is ideal for dozens of sites, it may become complex as we scale to hundreds of custom domains.

### Future Extension: Gateway Worker Router with Service Bindings
To scale past hundreds of sites without registering individual Cloudflare Pages projects, a future routing layer can be inserted:

```
[User Request] ──> [Custom Domain] ──> [Cloudflare for SaaS Gateway Worker]
                                                  │
                      ┌───────────────────────────┴───────────────────────────┐
                      ▼ (Resolves Niche template from D1/KV cache)            ▼
        [Service Binding to Furniture App]                      [Service Binding to Sauna App]
```

#### How it works:
1. **Dynamic Custom Domain Resolution:** Create a single wildcard Cloudflare fallback zone routing to a Gateway Worker.
2. **Metadata Lookup:** The Gateway Worker reads the incoming domain, performs a quick query to the **Cloudflare KV cache** (synchronized from D1 database) to resolve the niche.
3. **High-Speed Service Bindings:** The Gateway Worker uses **Service Bindings** to route the request directly to the compiled SolidStart niche template handler, eliminating extra HTTP latency and avoiding the 100-project pages limit.

---

## Provisioning Custom SaaS Domains

We leverage **Cloudflare for SaaS** to support custom reseller domains (e.g. `reseller-domain.com`).
The helper under `infra/saas-provision` automates client domain onboarding via the Cloudflare API, setting up custom hostnames, provisioning SSL, and generating validation DNS records dynamically.

```bash
# Execute provisioning check dry-run
RUN_PROVISION_DRY=true npx tsx infra/saas-provision/src/index.ts
```

---

## Data Layer Architecture (Cloudflare Native)

1. **Source of Truth (D1):** Structured Relational SQL Store. Perfect for ACID-compliant customer orders, tenant mappings, and wholesaling inventory catalogs.
2. **Fast-Read Caching (KV):** Flat file key-value cache holding parsed tenant metadata configuration. Refreshed asynchronously upon D1 configuration edits to ensure sub-millisecond edge response times.
3. **Asset Storage (R2):** Amazon S3-compatible asset storage. Slices custom site logos, product cards, and media images natively on the Cloudflare global network.
