# Contract 03: Section 3

- **Section id:** `section-3`
- **Source fragment:** `$.extractions[desktop].dom_tree (section via main children[2])`
- **Images in this section:** 16

## Allowed paths
- `sites/furniture/src/components/sections/section-3`
- `sites/furniture/src/components/sections/section-3/*`

## Forbidden paths
- `sites/furniture/src/app.tsx`
- `sites/furniture/src/app.css`
- `sites/furniture/src/routes/**`
- `sites/furniture/package.json`
- `sites/furniture/vite.config.ts`
- `sites/furniture/tsconfig.json`

## Output files
- `sites/furniture/src/components/sections/section-3/Section3Section.tsx`
- `sites/furniture/src/components/sections/section-3/section-3.css`

## Section images (use these only)

- `/assets/koala/img-004-31bb2a9f.png`
  selector: `img.loaded` · alt: 'Wanda Sofa Bed - 99" Queen / Australia 01 (Pantone)' · hint: `product` · primary: True
- `/assets/koala/img-005-9c1f89ac.png`
  selector: `img.loaded` · alt: 'Wanda Sofa Bed - 99" Queen / Australia 01 (Pantone)' · hint: `product` · primary: True
- `/assets/koala/img-006-553b3ba8.png`
  selector: `img.loaded` · alt: 'Wanda Sofa Bed - 99" Queen / Australia 01 (Pantone)' · hint: `product` · primary: False
- `/assets/koala/img-007-c460d576.png`
  selector: `img.loaded` · alt: 'Wanda Sofa Bed - 99" Queen / Australia 01 (Pantone)' · hint: `product` · primary: False
- `/assets/koala/img-008-9b032ead.png`
  selector: `img.loaded` · alt: 'Wanda Sofa Bed - 99" Queen / Australia 01 (Pantone)' · hint: `product` · primary: False
- `/assets/koala/img-009-??.png` (FAILED - check extraction.json)
  selector: `img.loaded` · alt: 'Wanda Sofa Bed - 99" Queen / Australia 01 (Pantone)' · hint: `product` · primary: False
- `/assets/koala/img-010-??.png` (FAILED - check extraction.json)
  selector: `img.loaded` · alt: 'Wanda Sofa Bed - 99" Queen / Australia 01 (Pantone)' · hint: `product` · primary: False
- `/assets/koala/img-011-e891cc8a.png`
  selector: `img.loaded` · alt: 'Luxurious olive green sectional sofa with plush upholstery and rounded armrests. Features a chaise lounge, perfect for modern living spaces.' · hint: `product` · primary: False
- `/assets/koala/img-019-ca3174c0.png`
  selector: `img` · alt: 'Luxurious brown suede sectional sofa with chaise lounge, featuring plush cushioning and streamlined design. Ideal for spacious, modern living rooms.' · hint: `faq` · primary: False
- `/assets/koala/img-020-8435cc25.png`
  selector: `img` · alt: 'Luxurious brown suede sectional sofa with spacious under-seat storage. Features plush cushions, streamlined design, and versatile functionality in modern living space.' · hint: `faq` · primary: False
- `/assets/koala/img-024-df90a771.png`
  selector: `video.infinite-carousel__item-video-desktop` · alt: 'a modern sofa bed in multiple different colors' · hint: `shopify-section-template--18674508366006__infinite_carousel_phgyux` · primary: False
- `/assets/koala/img-025-f928d801.png`
  selector: `video.infinite-carousel__item-video-desktop` · alt: 'two friends easily putting together a sofa bed and lounging' · hint: `shopify-section-template--18674508366006__infinite_carousel_phgyux` · primary: False
- `/assets/koala/img-026-bca1037b.png`
  selector: `video.infinite-carousel__item-video-desktop` · alt: 'a couple lounging on a brown sofa bed' · hint: `shopify-section-template--18674508366006__infinite_carousel_phgyux` · primary: False
- `/assets/koala/img-027-f51993a4.png`
  selector: `video.infinite-carousel__item-video-desktop` · alt: 'a dog and person lying down on a sofa bed' · hint: `shopify-section-template--18674508366006__infinite_carousel_phgyux` · primary: False
- `/assets/koala/img-028-1ccf9fab.png`
  selector: `video.infinite-carousel__item-video-desktop` · alt: 'close up of all different sofa bed fabric colors' · hint: `shopify-section-template--18674508366006__infinite_carousel_phgyux` · primary: False
- `/assets/koala/img-029-76a09829.png`
  selector: `video.infinite-carousel__item-video-desktop` · alt: 'two friends opening up the storage under a sofa bed' · hint: `shopify-section-template--18674508366006__infinite_carousel_phgyux` · primary: False

## Acceptance criteria
- typecheck
- build
- visual check at desktop/tablet/mobile
- no remote final image URLs
- use only images listed in this contract (mapped via manifest)

## Scoped source

Read this fragment with the source query helper before editing:

`$.extractions[desktop].dom_tree (section via main children[2])`
