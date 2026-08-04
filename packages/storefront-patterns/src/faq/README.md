# FAQ

Two-column FAQ accordion (title + expandable questions).

## When to use

- PDP / support FAQs

## Import

```tsx
import { Faq, type FaqItem } from "@repo/storefront-patterns";
```

## Accessibility

- Triggers expose `aria-expanded` / `aria-controls`
- Panels are `role="region"` and toggle `hidden`
