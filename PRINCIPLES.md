# Development Principles

## Shared UI Patterns

- Maintain stable primitives in `packages/ui` (buttons, inputs, dialogs, etc.).
- Maintain reusable commerce patterns in `packages/storefront-patterns` (PDP gallery, buy box, product details accordion, reviews, FAQ, media-text sections, product cards, recommendation rows, etc.).
- Make patterns configurable with slots and props rather than forcing all variations into props.
- Keep patterns small and readable so sites can copy and adapt when needed.

## Component Design

- Build components with slots and clear prop interfaces.
- Provide minimal usage examples and documentation in the README.
- Document when to use a pattern and when to avoid it.
- Include responsive and accessibility expectations in the README.

## Page Composition

- Share stable commerce patterns, not entire pages.
- Let each site compose its own page layout and hero sections.
- Use site-local sections for niche-specific merchandising and unique layouts.
- Enable sites to fork patterns when requirements diverge.

## Documentation

- Maintain a pattern catalog README in `packages/storefront-patterns`.
- Include import paths, props, slots, variants, and customization guidance.
- Link directly to component source code.
- Provide minimal runnable examples.
- Document responsive and accessibility expectations.
- Avoid screenshots for every component; rely on visual QA and a few canonical examples.

## Agent Guidance

- Search the pattern catalog first.
- Read the README to discover and select a pattern.
- Read the selected component source before modifying or heavily customizing it.
- Use visual QA as the final authority on UI correctness.
