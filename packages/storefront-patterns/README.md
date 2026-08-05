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
- Top announcement banner (`TopBanner`) — centered, optional rotating `messages`, non-sticky
- Site header / category nav (`SiteHeader`)
- Nav subcategory dropdown (`NavDropdown`) — list or image cards
- Collection product card (`ProductCard`)
- Promo media tile with click-to-play (`PromoMediaTile`)
- Grid testimonial / quote tile (`QuoteTile`)
- Trust / policy tile (`TrustTile`)
- Mixed collection grid (`CollectionGrid`)

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
  TopBanner,
  SiteHeader,
  NavDropdown,
  ProductCard,
  PromoMediaTile,
  QuoteTile,
  TrustTile,
  CollectionGrid,
} from '@repo/storefront-patterns';
```

## Collection page building blocks

Compose a collection page from small, prop-driven tiles — sites own the data:

```tsx
<TopBanner
  messages={[
    "Free Shipping & 120 Day Free Returns",
    "Fast delivery to most metro areas",
  ]}
  intervalMs={4000}
  links={[
    { label: "Help Centre", href: "#faq" },
    { label: "Contact", href: "#" },
  ]}
/>

<SiteHeader
  brand="koala"
  brandHref="/"
  activeLabel="Modular Sofas"
  navItems={[
    { label: "Best Sellers", href: "/collections" },
    {
      label: "Modular Sofas",
      href: "/collections",
      dropdownVariant: "cards",
      children: [
        {
          id: "2-seater",
          label: "2-Seater Sofas",
          href: "/collections",
          imageSrc: "/assets/sofa.png",
        },
        {
          id: "chaise",
          label: "Chaise Sofas",
          href: "/collections",
          imageSrc: "/assets/chaise.png",
        },
      ],
    },
  ]}
/>

<CollectionGrid
  title="Bangalow Modular Sofas"
  items={[
    {
      type: "product",
      id: "p1",
      product: {
        href: "/",
        title: "Bangalow Modular Sofa",
        subtitle: "2 Sections • 12 Sizes",
        images: [{ src: "/assets/sofa.png", alt: "Sofa" }],
        rating: 5,
        reviewCount: 420,
        price: "$1,290",
        compareAtPrice: "$1,490",
        saveLabel: "SAVE $200",
        swatches: [{ name: "Fog", src: "/assets/swatch.png" }],
      },
    },
    {
      type: "promo",
      id: "promo1",
      promo: {
        title: "Removable & washable covers",
        imageSrc: "/assets/poster.png",
        videoSrc: "/assets/video.mp4",
        ctaLabel: "Shop now",
        ctaHref: "/",
      },
    },
    {
      type: "quote",
      id: "q1",
      quote: {
        rating: 5,
        quote: "Amazing couch! Great quality.",
        author: "Jamie T.",
      },
    },
    {
      type: "trust",
      id: "t1",
      trust: {
        items: [
          { id: "returns", label: "120 Day Free Returns", iconSrc: "/icon.svg" },
          { id: "ship", label: "Fast delivery", iconSrc: "/truck.svg" },
        ],
        ctaLabel: "Show more",
        ctaHref: "#faq",
      },
    },
  ]}
/>
```

### When to use
- **TopBanner / SiteHeader**: shared chrome across PDP + collection (or any page).
- **NavDropdown**: subcategory menus on a nav tab (`list` or image `cards`); also usable standalone.
- **CollectionGrid**: PLP / category merchandising with mixed product + promo tiles.
- **QuoteTile**: one featured review in a grid — not a replacement for `Reviews`.
- **PromoMediaTile**: lifestyle/video merchandising with optional click-to-play.

### When to avoid
- Do not bake site-specific filters, sort, cart, or checkout into these patterns.
- Prefer site-local wrappers for niche layout chrome; keep patterns prop/slot driven.
- Fork a pattern when a site’s requirements diverge heavily.

### Responsive / a11y
- Collection grid: 3 → 2 → 1 columns.
- Product image dots and promo play controls are keyboard-reachable buttons.
- Header marks `aria-current="page"` via `activeHref`.
- Banner is a landmark region; header exposes a labelled primary nav.

When sites require custom layouts, copy and adapt the pattern.

This folder is NOT for UI primitives. Primitives belong in `@repo/ui`.
