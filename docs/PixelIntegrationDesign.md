# Meta Pixel + Conversions API Integration Design

**Status:** Implemented in repository; production deployment pending
**Scope:** 100+ static SolidStart storefronts running Meta `OUTCOME_SALES` campaigns.  
**Related:** `docs/AdPublishingWorkflow.md`, `packages/analytics`, `packages/config-validation`.

## 1. Executive decision

The platform must support both **per-site datasets** and a **shared portfolio dataset**, but the default for independent storefronts is **one Meta dataset/pixel per site**.

A dataset is the attribution boundary for Meta event quality, optimization, diagnostics, audiences, and reporting. Sending purchases from 100 unrelated stores to one dataset can give Meta a larger aggregate signal, but it also makes the signal semantically mixed: campaigns can optimize against purchases from other brands/products and reporting no longer answers “which site produced this conversion?” A shared dataset is appropriate only when the sites are genuinely one advertiser/brand, have a shared customer and offer strategy, and deliberately optimize a portfolio-level outcome.

**Default policy:**

- `dataset_mode: per_site` for separate brands, domains, catalogs, ad accounts, or owners.
- `dataset_mode: shared` only by explicit platform/marketing approval, with a documented portfolio key and cross-site reporting safeguards.
- Never silently fall back from a missing site pixel to the shared pixel.
- A site may have multiple ad accounts using the same site dataset, subject to Meta permissions; an unrelated site may not reuse it.

This is a routing choice, not merely a script configuration. The same routing must be used by browser Pixel and server CAPI.

## 2. Prerequisites and delivery boundary

The shared checkout/analytics CAPI endpoint and dataset registry are **not implemented yet**. `infra/checkout-api` and the registry (planned D1/KV or equivalent) are prerequisites for server-side events. Until they exist, only the browser Pixel path is shippable; `Purchase` CAPI, server-side routing, retries, and the event ledger must remain disabled rather than approximated in static sites.

The implementation should therefore be delivered in two gates:

1. **Browser-only gate:** schema, consent-gated Pixel, event IDs, and site-level IDs; no CAPI token in sites.
2. **CAPI gate:** shared checkout endpoint, registry, idempotency ledger, secret storage, and webhook integration, followed by the rollout in §12.

## 3. Goals and non-goals

### Goals

1. Emit consistent `PageView`, `ViewContent`, `AddToCart`, `InitiateCheckout`, and `Purchase` events.
2. Route every event to the correct site/dataset, including server-side checkout events.
3. Deduplicate browser and CAPI copies reliably.
4. Preserve site-level reporting even when a shared dataset is approved.
5. Avoid exposing access tokens in static sites and avoid blocking SSG builds.
6. Make configuration, consent, rollout, health checks, and dataset migrations auditable.

### Non-goals

- Building a general-purpose tag manager.
- Using a shared dataset to pool audiences or “make a weak site look mature” without approval.
- Sending raw customer data to the browser or committing Meta credentials.
- Treating Meta reporting as the source of truth for orders; the commerce/checkout system remains authoritative.

## 4. Architecture

```text
Static site (Pixel, consent-gated) ──┐
                                     ├─ event_id + site_id + dataset_id ──> Meta
Checkout API / order webhook (CAPI) ─┘
          │
          └─ internal event ledger + delivery/retry/dead-letter metrics
```

The static storefront may load `fbevents.js` and call `fbq`. It must not call CAPI directly. CAPI calls go through the shared checkout/analytics service, which owns tokens, retries, hashing, and the event ledger. For a browser-only event, the browser can send Pixel only; for `Purchase`, the server is authoritative and should send CAPI after payment is confirmed.

The checkout API must receive or derive:

- `site_id` / tenant ID and canonical site origin;
- Meta click context (`fbclid`, and the `_fbc`/`_fbp` cookies where consent permits);
- a checkout/order-scoped `event_id` generated before payment;

Because storefronts are pure SSG and have no request handler, the browser-to-server handoff is explicit: the Pixel/analytics provider reads the consent-approved `_fbp` and `_fbc` cookies (and captures `fbclid` on landing when needed), then includes them in the authenticated checkout-create request. The checkout API persists them with the checkout/order and carries them into the payment-confirmation webhook. If checkout is hosted on another origin, pass these fields through the signed checkout session, not an ad-hoc query string. Missing click context is allowed; fabricated values are not.
- order value, currency, and line items;
- consent status and permitted customer identifiers.

The server must reject an event whose site is unknown, inactive, or not mapped to a dataset. It must not infer a site from an arbitrary client-provided dataset ID.

## 5. Configuration contract

Add a Meta integration block to the site configuration (validated centrally in `packages/config-validation`):

```json
{
  "analytics": {
    "meta": {
      "enabled": true,
      "dataset_mode": "per_site",
      "pixel_id": "123456789012345",
      "dataset_id": "123456789012345",
      "capi_route_key": "furniture-us",
      "test_event_code": null,
      "send_browser_events": true,
      "send_server_events": true,
      "consent_required": true
    }
  }
}
```

For v1 ergonomics, `dataset_id` may be omitted and resolves to `pixel_id` during validation/registry resolution. When it is present, it is explicitly authoritative; do not assume the IDs are equal in application code. For shared mode:

```json
{
  "dataset_mode": "shared",
  "shared_dataset_key": "portfolio-us-1",
  "pixel_id": "SHARED_PIXEL_ID",
  "dataset_id": "SHARED_DATASET_ID"
}
```

The platform registry, not a site bundle, is the source of truth for `shared_dataset_key → dataset/token/account`. Public site config contains only public IDs and a non-secret route key. CAPI tokens live in the checkout service secret manager.

Required validation:

- exact numeric-string format for IDs;
- `dataset_mode=per_site` requires site pixel and dataset IDs;
- `dataset_mode=shared` requires an approved registry key;
- no token, app secret, or system-user credential allowed in site config;
- site/domain/tenant mapping must be unique;
- production cannot use a test event code.

## 6. Event contract

All events have a stable `event_id`, `event_name`, `event_time`, `action_source=website`, `site_id`, and the routed dataset. Names and commerce fields follow Meta's standard event schema.

| Storefront action | Meta event | Required/important fields |
|---|---|---|
| route view | `PageView` | URL, site ID |
| product detail | `ViewContent` | `content_ids`, `content_type`, `content_name`, `content_category`, `value`, `currency` |
| cart add | `AddToCart` | product IDs, quantity, value, currency |
| checkout start | `InitiateCheckout` | contents, value, currency, order/checkout ID |
| paid order | `Purchase` | order ID, contents, value, currency, customer match data |

Use one event ID for the same logical conversion in both channels. Generate it at checkout creation, persist it with the order, and reuse it across retries. Do not use a random new ID on each webhook retry.

Recommended internal envelope:

```ts
{
  event_id: string,
  event_name: "Purchase" | "InitiateCheckout" | ...,
  site_id: string,
  tenant_id: string,
  occurred_at: string,
  event_source_url?: string,
  order_id?: string,
  value?: number,
  currency?: string,
  contents?: Array<{id: string, quantity: number, item_price?: number}>,
  consent: { advertising: boolean },
  browser: { fbp?: string, fbc?: string, user_agent?: string, ip?: string },
  user_data: { email?: string, phone?: string }
}
```

Normalize currency and monetary values once. Use product IDs stable within the routed site catalog. Never put email/phone in URL parameters or logs.

## 7. Browser Pixel implementation

Create a provider in `packages/analytics` rather than embedding Meta code in each site. The provider should:

1. initialize only when enabled and advertising consent exists;
2. initialize exactly the configured public pixel ID;
3. send standard events with `eventID: event_id` for events also sent by CAPI;
4. include `external_id` only according to the consent/privacy policy;
5. support SPA route changes without duplicate initialization;
6. no-op during SSR and when ad blockers/network failures occur;
7. expose diagnostics without logging personal data.

The integration is additive to the existing `AnalyticsManager`; it must not change SSG behavior. `PageView` should be emitted after hydration and on client route transitions, not during server rendering. Product/cart events must be emitted from the actual user action, not merely from a component render.

Do not use `trackCustom` for standard commerce events. Do not fire `Purchase` on a thank-you page merely because it was viewed: the order confirmation must contain a server-confirmed order and an idempotent event ID.

## 8. CAPI implementation

The shared checkout/analytics endpoint sends events to the dataset configured for the authenticated site. It must:

- hash normalized email/phone and other permitted identifiers with SHA-256 server-side;
- send `client_user_agent`, `event_source_url`, `fbc`, and `fbp` when legally collected;
- use `action_source=website`;
- send `event_time` as Unix seconds and the original event ID;
- retry transient failures with bounded exponential backoff;
- deduplicate by `(site_id, event_id, event_name)` in an idempotency ledger;
- dead-letter permanent failures for inspection/replay;
- redact identifiers and tokens from logs.

`Purchase` is sent only after the payment/order state is final. Meta CAPI has no true generic `Refund` event; refunds/cancellations are recorded in the internal order ledger. Any Meta value-adjustment behavior is a separate approved feature, not an accidental second purchase. CAPI `event_time` has a maximum backfill window of seven days; older late webhooks are flagged to the dead-letter queue for review, never silently discarded.

## 9. Per-site vs shared dataset decision matrix

| Consideration | Per-site dataset | Shared portfolio dataset |
|---|---|---|
| Attribution/reporting | Clean site-level result | Requires mandatory `site_id` breakdown internally; Meta may not provide the desired dimension everywhere |
| Optimization | Learns that site's offer/catalog | Learns pooled behavior; may conflate brands and products |
| Cold start | Less signal per site | More aggregate signal, but only useful if behavior is comparable |
| Audiences | Site-specific and safer | Cross-site audience leakage/eligibility risk; requires explicit policy |
| Operations | 100+ IDs and permissions | Simpler routing/token management |
| Best fit | Independent stores | One brand, shared catalog/customer journey, portfolio campaigns |

A shared dataset does not magically preserve independent attribution. Every event still carries a site dimension in the internal ledger, and campaign/ad naming must include the site slug. If Meta cannot report or optimize the required site boundary, use per-site datasets.

## 10. Campaign and naming rules

`docs/AdPublishingWorkflow.md` must read the same registry/config. Every campaign/ad set/ad name includes the site slug and dataset mode, for example:

```text
[furniture][per_site][US] Prospecting | OUTCOME_SALES
```

The publishing worker refuses to publish when the campaign's configured dataset does not match the site's approved routing. It never overwrites a dataset because a pixel ID is present in an ad draft. Shared mode requires an approval record, owner, reason, review date, and list of participating sites.

## 11. Privacy, consent, and security

- Honor the site's consent mechanism before advertising cookies, Pixel, or non-essential CAPI user data.
- Respect applicable regional requirements and provide opt-out/deletion handling.
- Do not send payment card data, addresses unless explicitly approved, or unnecessary custom data.
- CAPI secrets are server-only, rotated, least-privilege, and never present in static output.
- Apply tenant isolation to event ingestion, registry lookup, dashboards, and replay tools.
- Retain raw event data only as long as the privacy/operations policy requires; store hashed/aggregated diagnostics where possible.

## 12. Observability and acceptance criteria

Track per site, dataset, event name, and channel:

- attempted, accepted, rejected, retried, dead-lettered events;
- browser/CAPI deduplication rate;
- event match quality and delivery latency;
- order ledger count/value versus CAPI `Purchase` count/value;
- unknown-site, wrong-dataset, consent-denied, and duplicate rates.

Dashboards must show both portfolio totals and site-level internal totals. Alerts fire on wrong routing, purchase variance, sudden zero delivery, and duplicate purchase spikes.

Acceptance tests:

1. Two sites with different configs emit different browser pixel IDs.
2. A server purchase for site A cannot route through site B's key.
3. Browser + CAPI purchase with the same event ID is one Meta conversion.
4. Webhook retry does not create another purchase.
5. Missing/invalid mapping fails closed and creates an actionable alert.
6. Consent denial emits no advertising event or identifier.
7. Build/prerender succeeds with Meta enabled, disabled, or unconfigured.
8. Shared mode is impossible without registry approval and remains site-auditable internally.

## 13. Rollout and migration

1. Add schema and registry in report-only mode; inventory every site, ad account, pixel, dataset, and owner.
2. Implement the provider and event ledger; send test events using Meta's test event code in non-production.
3. Launch one per-site pilot and compare confirmed orders to Pixel/CAPI diagnostics.
4. Enable CAPI `Purchase` after dedupe and idempotency tests pass; keep browser purchase temporarily for dedupe verification.
5. Migrate sites in batches, with a routing audit before each batch.
6. For an approved shared portfolio, create a new explicit shared key and migrate deliberately; do not mix historical per-site and shared events without annotating the reporting boundary.

Changing a live site's dataset is a measurement migration. Record the cutover timestamp, old/new IDs, campaign IDs, and expected learning/reporting impact. Keep the old mapping available for late webhook replay only when it is still authorized; new events must use the new mapping.

## 14. Implementation checklist

- [x] Extend `packages/config-validation` with the Meta schema and safe defaults.
- [x] Add `MetaPixelProvider` and consent/event-ID support to `packages/analytics`.
- [x] Add D1 dataset registry and checkout CAPI route with an idempotency ledger.
- [x] Update bootstrap/template scaffolding to generate disabled analytics config.
- [x] Update ad publishing and clone workflow requirements.
- [ ] Add complete automated routing, retry/replay, consent, and SSG test coverage.
- [ ] Add dashboards and a per-site/dataset audit report.

## 15. Operator actions and remaining production work

The code path is present, but it cannot deliver production events until the following are completed:

1. Apply `infra/d1/0003_meta_pixel.sql` to the Cloudflare D1 database.
2. Replace `infra/checkout-api/wrangler.json` `database_id` with the real D1 database ID.
3. Insert one `meta_dataset_registry` row per live site with the real pixel/dataset IDs and canonical origin.
4. Configure Worker secret `META_CAPI_ACCESS_TOKEN`; keep it out of Git and static site builds.
5. Configure Stripe webhook delivery to the deployed checkout Worker and verify checkout metadata includes the event context.
6. Provide real Meta pixel/dataset IDs and shared approvals where applicable.
7. Run a test purchase and confirm the browser event and CAPI event share the same `event_id`.

Pending engineering work includes bounded retry scheduling/dead-letter replay tooling, dashboard metrics, complete line-item CAPI payloads, and automated production routing tests. Privacy/consent enforcement is intentionally excluded from this implementation per request.

**Final recommendation:** start with per-site datasets for all independently branded storefronts. Revisit shared datasets only for a clearly unified business where pooled learning is the intended optimization target—not as a default convenience for managing 100+ sites.

# Implemented the full repository path

  Completed:
  • Browser Pixel provider and checkout attribution/event IDs.
  • Bootstrap analytics config generation.
  • D1 dataset registry and Meta event ledger migration.
  • Checkout Worker registry validation and CAPI Purchase.
  • Server-side email hashing and duplicate prevention.
  • Ad publishing validation updates.
  • Clone workflow requirements.
  • Pixel design status, pending work, and operator actions.

  Verification:
  • Config validation typecheck passed.
  • Analytics typecheck passed.
  • Checkout API tests passed: 7/7.
  • Furniture and sauna builds passed.
  • git diff --check passed.

  Your remaining actions:
  1. Apply infra/d1/0003_meta_pixel.sql.
  2. Set the real D1 database_id in infra/checkout-api/wrangler.json.
  3. Populate meta_dataset_registry with real site/pixel/dataset mappings.
  4. Configure META_CAPI_ACCESS_TOKEN as a Worker secret.
  5. Configure and test the Stripe webhook.
  6. Provide real Meta IDs before enabling campaigns.

  Known pending engineering items are documented: retry scheduling/replay tooling, dashboards, full line-item CAPI payloads, and
  expanded automated routing tests.