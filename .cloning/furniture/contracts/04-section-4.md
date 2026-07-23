# Contract 04: Section 4

- **Section id:** `section-4`
- **Source fragment:** `$.extractions[desktop].dom_tree (section via main children[3])`
- **Images in this section:** 5

## Allowed paths
- `sites/furniture/src/components/sections/section-4`
- `sites/furniture/src/components/sections/section-4/*`

## Forbidden paths
- `sites/furniture/src/app.tsx`
- `sites/furniture/src/app.css`
- `sites/furniture/src/routes/**`
- `sites/furniture/package.json`
- `sites/furniture/vite.config.ts`
- `sites/furniture/tsconfig.json`

## Output files
- `sites/furniture/src/components/sections/section-4/Section4Section.tsx`
- `sites/furniture/src/components/sections/section-4/section-4.css`

## Section images (use these only)

- `/assets/koala/img-010-??.png` (FAILED - check extraction.json)
  selector: `img.loaded` · alt: 'Wanda Sofa Bed - 99" Queen / Australia 01 (Pantone)' · hint: `product` · primary: False
- `/assets/koala/img-011-e891cc8a.png`
  selector: `img.loaded` · alt: 'Luxurious olive green sectional sofa with plush upholstery and rounded armrests. Features a chaise lounge, perfect for modern living spaces.' · hint: `product` · primary: False
- `/assets/koala/img-013-??.png` (FAILED - check extraction.json)
  selector: `img.loaded` · alt: 'Wanda Sofa Bed - 99" Queen / Australia 01 (Pantone)' · hint: `product` · primary: False
- `/assets/koala/img-014-??.png` (FAILED - check extraction.json)
  selector: `img.loaded` · alt: 'Koala Sofa Bed [4th Gen]' · hint: `product` · primary: False
- `/assets/koala/img-015-179c25f4.png`
  selector: `img` · alt: 'Luxurious brown velvet sectional sofa with plush cushions, streamlined design, and right-hand chaise. Perfect for a sophisticated, modern living space.' · hint: `product` · primary: False
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

`$.extractions[desktop].dom_tree (section via main children[3])`
