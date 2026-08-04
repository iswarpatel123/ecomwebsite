# Storefront Patterns

Reusable commerce patterns for sites:
- PDP product gallery (site-local) + purchase panel (`ProductDescription`)
- Product details accordion (via `ProductDescription`)
- Tabbed media visualizer (`TabbedMedia`)
- Media-and-text storytelling (`MediaText`)
- Reviews summary/list (`Reviews`)
- FAQ block (`Faq`)
- Impact / sustainability cards (`ImpactCards`)
- Newsletter CTA (`NewsletterCta`)
- Site footer (`SiteFooter`)

Import patterns directly:
```tsx
import {
  ProductDescription,
  TabbedMedia,
  MediaText,
  Reviews,
  Faq,
  ImpactCards,
  NewsletterCta,
  SiteFooter,
} from '@repo/storefront-patterns';
```

When to use / avoid patterns documented in each component’s README.
When sites require custom layouts, copy and adapt the pattern.

This folder is NOT for UI primitives. Primitives belong in `@repo/ui`.
