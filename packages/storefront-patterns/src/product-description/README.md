# Product Description

A reusable, configurable product description panel for product detail pages (PDPs). Displays product info, benefits, purchase controls, and expandable detail sections (accordion) — all configurable via props and slots.

## When to use

- **PDP buy box / detail panel** — the right-hand column summarising a product and offering "Add to cart".
- Any page that needs a product summary with expandable spec sheets, shipping info, care instructions, etc.

## When to avoid

- Landing pages with no purchase intent (use `MediaText` section instead).
- Comparison tables or spec grids (build a dedicated spec-table pattern).

## Import

```tsx
import {
  ProductDescription,
  type AccordionSection,
  type ProductDescriptionProps,
} from "@repo/storefront-patterns";
```

## Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `title` | `string` | **yes** | Product name (rendered as `<h1>`) |
| `price` | `string` | **yes** | Display price, e.g. `"$1,950"` |
| `sections` | `AccordionSection[]` | no | Ordered list of expandable detail sections |
| `breadcrumbLabel` | `string` | no | Breadcrumb text, e.g. `"Sofa Beds"` |
| `breadcrumbHref` | `string` | no | Breadcrumb link (default `#`) |
| `rating` | `number` | no | Star rating 0–5 |
| `reviewCount` | `number` | no | Number of reviews |
| `reviewHref` | `string` | no | Link target for review count |
| `compareAtPrice` | `string` | no | Original price shown struck-through |
| `paymentPlan` | `string` | no | Payment plan blurb |
| `benefits` | `Array<{icon?: string; label: string}>` | no | Trust badges / benefits bar |
| `renderOptions` | `() => JSXElement` | no | Slot for size / colour / variant selectors |
| `renderPurchase` | `() => JSXElement` | no | Slot replacing the default quantity + add-to-cart |
| `children` | `JSXElement` | no | Extra content injected below the accordion |
| `class` | `string` | no | Additional CSS class on root |

### AccordionSection

```ts
type AccordionSection = {
  id: string;                // unique key
  title: string;             // heading text
  content?: string;          // HTML string for simple content
  renderContent?: () => JSXElement;  // slot for rich content
  renderTitle?: () => JSXElement;    // slot for custom title (icon + text)
  defaultOpen?: boolean;     // start expanded (default: false)
};
```

## Basic usage

```tsx
import { ProductDescription } from "@repo/storefront-patterns";

const details: AccordionSection[] = [
  { id: "description", title: "Product Description", content: "<p>Comfiest sofa bed around…</p>" },
  { id: "features",   title: "Key Features",       content: "<ul><li>Flip-to-bed design</li></ul>" },
  { id: "dimensions", title: "Dimensions",         content: "<p>W 99 × D 85 × H 82 cm</p>" },
  { id: "care",       title: "Care",               content: "<p>Spot clean with mild soap.</p>" },
  { id: "shipping",   title: "Delivery & Returns", content: "<p>Free delivery. 120-day trial.</p>" },
];

function ProductPage() {
  return (
    <ProductDescription
      title="Wanda Sofa Bed"
      price="$3,295"
      rating={4.9}
      reviewCount={222}
      breadcrumbLabel="Sofa beds"
      breadcrumbHref="/sofa-beds"
      benefits={[
        { icon: "/icons/truck.svg", label: "Free delivery" },
        { icon: "/icons/trial.svg", label: "120-night trial" },
        { icon: "/icons/warranty.svg", label: "10-year warranty" },
      ]}
      sections={details}
    />
  );
}
```

## Slot examples

### Custom colour swatches

```tsx
<ProductDescription
  title="Wanda Sofa Bed"
  price="$3,295"
  renderOptions={() => (
    <div class="swatches">
      <button class="swatch is-selected" aria-label="Olive Green" />
      <button class="swatch" aria-label="Sandy Beige" />
    </div>
  )}
/>
```

### Rich accordion content

```tsx
{
  id: "assembly",
  title: "Assembly Instructions",
  renderTitle: () => (
    <>
      <img src="/icons/wrench.svg" alt="" aria-hidden="true" />
      Assembly Instructions
    </>
  ),
  renderContent: () => (
    <ol>
      <li>Unbox all parts on a soft surface.</li>
      <li>Attach the backrest to the seat frame.</li>
    />
  ),
}
```

### Custom purchase area

```tsx
<ProductDescription
  title="Wanda Sofa Bed"
  price="$3,295"
  renderPurchase={() => (
    <div class="custom-buy">
      <select>
        <option>Select size</option>
        <option>75"</option>
        <option>99"</option>
      </select>
      <button class="buy-btn">Add to cart</button>
    </div>
  )}
/>
```

## CSS custom properties

Override via CSS custom properties on the root or ancestor:

| Property | Default | Description |
|----------|---------|-------------|
| `--pd-font` | `inherit` | Base font family |
| `--pd-text` | `#1a1a1a` | Primary text colour |
| `--pd-muted` | `#6b6b6b` | Muted / secondary text |
| `--pd-border` | `#e5e5e5` | Border colour for dividers and quantity control |
| `--pd-star` | `#f5a623` | Star rating colour |
| `--pd-cta-bg` | `#1a1a1a` | Add-to-cart background |
| `--pd-cta-text` | `#fff` | Add-to-cart text |
| `--pd-cta-hover` | `#333` | Add-to-cart hover |
| `--pd-focus` | `#005fcc` | Focus-visible ring |
| `--pd-max-width` | `32rem` | Max width of root |
| `--pd-title-size` | `1.5rem` | Product title font size |
| `--pd-price-size` | `1.25rem` | Price font size |

## Responsive

- Default layout is single-column (fits the right-hand column of a two-column PDP hero).
- On small screens (< 640px) the component flows naturally into a full-width layout — no breakpoint changes needed.
- The benefits bar wraps via `flex-wrap`.
- The accordion panels use `max-height` transition for smooth expand/collapse.

## Accessibility

- Accordion buttons have `aria-expanded`, `aria-controls`, and `aria-labelledby`.
- Accordion panels have `role="region"` and `aria-labelledby`.
- Star rating has `aria-label` describing the rating.
- Quantity control uses `aria-label` and `aria-live="polite"` for the count.
- Focus-visible outline on accordion triggers and buttons.
