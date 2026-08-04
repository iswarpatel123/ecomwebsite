# TabbedMedia

Feature showcase with tabbed modes, optional people/height chips, and play/pause for video.

## When to use

- PDP “how it sits / sleeps” visualizers
- Mode switchers that swap the same stage media

## When to avoid

- Simple static media+text (use `MediaText`)
- Full product galleries (use site gallery)

## Import

```tsx
import { TabbedMedia } from "@repo/storefront-patterns";
```

## Accessibility

- Tabs use `role="tablist"` / `aria-selected`
- Video has `aria-label`; pause control is a real button
