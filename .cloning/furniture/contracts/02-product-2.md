# Contract 02: Product Detail

- **Section id:** `product-2`
- **Source fragment:** `$.extractions[desktop].dom_tree (section via main children[1])`
- **Images in this section:** 3

## Allowed paths
- `sites/furniture/src/components/sections/product-2`
- `sites/furniture/src/components/sections/product-2/*`

## Forbidden paths
- `sites/furniture/src/app.tsx`
- `sites/furniture/src/app.css`
- `sites/furniture/src/routes/**`
- `sites/furniture/package.json`
- `sites/furniture/vite.config.ts`
- `sites/furniture/tsconfig.json`

## Output files
- `sites/furniture/src/components/sections/product-2/Product2Section.tsx`
- `sites/furniture/src/components/sections/product-2/product-2.css`

## Section images (use these only)

- `/assets/koala/img-004-31bb2a9f.png`
  selector: `img.loaded` · alt: 'Wanda Sofa Bed - 99" Queen / Australia 01 (Pantone)' · hint: `product` · primary: True
- `/assets/koala/img-005-9c1f89ac.png`
  selector: `img.loaded` · alt: 'Wanda Sofa Bed - 99" Queen / Australia 01 (Pantone)' · hint: `product` · primary: True
- `/assets/koala/img-019-ca3174c0.png`
  selector: `img` · alt: 'Luxurious brown suede sectional sofa with chaise lounge, featuring plush cushioning and streamlined design. Ideal for spacious, modern living rooms.' · hint: `faq` · primary: False

## Acceptance criteria
- typecheck
- build
- visual check at desktop/tablet/mobile
- no remote final image URLs
- use only images listed in this contract (mapped via manifest)

## Scoped source

Read this fragment with the source query helper before editing:

`$.extractions[desktop].dom_tree (section via main children[1])`
