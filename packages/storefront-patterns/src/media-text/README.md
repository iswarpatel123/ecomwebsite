# Media Text

Reusable storytelling row: copy beside image or video, with optional media-left / media-right layout.

## When to use

- PDP feature benefits (“Try it risk-free”, fabric stories, comfort claims)
- Any alternating media + text merchandising blocks

## When to avoid

- Dense comparison tables or multi-card grids (use a dedicated pattern)
- Hero / buy-box layouts (use site-local hero + `ProductDescription`)

## Import

```tsx
import { MediaText } from "@repo/storefront-patterns";
```

## Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `title` | `string` | yes | Feature headline |
| `body` | `string` | yes | Supporting paragraph |
| `media` | `{ type, src, alt?, poster? }` | yes | Image or video |
| `eyebrow` | `string` | no | Small label above title |
| `mediaPosition` | `"left" \| "right"` | no | Default `"right"` |
| `showPlayAffordance` | `boolean` | no | Play badge on videos |
| `renderMedia` | `() => JSXElement` | no | Replace default media |
| `class` / `id` | `string` | no | Root attributes |

## Example

```tsx
<MediaText
  title="Fabrics built for real life."
  body="Water-resistant, stain-resistant, and machine-washable covers."
  mediaPosition="left"
  media={{ type: "video", src: "/assets/video.mp4", poster: "/assets/poster.png", alt: "Fabric demo" }}
/>
```

## Responsive

- Two columns from 901px up; stacks with media on top below that.

## Accessibility

- Videos include `aria-label`; images use `alt`.
- Play badge is decorative (`aria-hidden`).
