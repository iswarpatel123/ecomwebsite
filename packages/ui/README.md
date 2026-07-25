# UI Primitives

Shared stable UI primitives:
- Buttons, inputs, dialogs, accordions, tabs, carousel, rating, quantity selector, typography, layout primitives.
- Accessibility and interaction logic.
- Import path: `@repo/ui`

Usage:
```tsx
import { Button } from '@repo/ui';
```

Add new primitives to `src/`. Run `pnpm build:ui` in root if a bundler is needed.

Patterns belong in `packages/storefront-patterns`.