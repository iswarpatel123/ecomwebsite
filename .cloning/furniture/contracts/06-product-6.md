# Contract 06: Product Detail

- **Section id:** `product-6`
- **Source fragment:** `$.extractions[desktop].dom_tree (section via main children[5])`
- **Images in this section:** 1

## Allowed paths
- `sites/furniture/src/components/sections/product-6`
- `sites/furniture/src/components/sections/product-6/*`

## Forbidden paths
- `sites/furniture/src/app.tsx`
- `sites/furniture/src/app.css`
- `sites/furniture/src/routes/**`
- `sites/furniture/package.json`
- `sites/furniture/vite.config.ts`
- `sites/furniture/tsconfig.json`

## Output files
- `sites/furniture/src/components/sections/product-6/Product6Section.tsx`
- `sites/furniture/src/components/sections/product-6/product-6.css`

## Section images (use these only)

- `/assets/koala/img-017-7fbc8168.png`
  selector: `video` · alt: 'a woman sitting on a light gray sofa bed' · hint: `product` · primary: False

## Acceptance criteria
- typecheck
- build
- visual check at desktop/tablet/mobile
- no remote final image URLs
- use only images listed in this contract (mapped via manifest)

## Scoped source

Read this fragment with the source query helper before editing:

`$.extractions[desktop].dom_tree (section via main children[5])`
