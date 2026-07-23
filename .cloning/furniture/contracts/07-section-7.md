# Contract 07: Section 7

- **Section id:** `section-7`
- **Source fragment:** `$.extractions[desktop].dom_tree (section via main children[6])`
- **Images in this section:** 2

## Allowed paths
- `sites/furniture/src/components/sections/section-7`
- `sites/furniture/src/components/sections/section-7/*`

## Forbidden paths
- `sites/furniture/src/app.tsx`
- `sites/furniture/src/app.css`
- `sites/furniture/src/routes/**`
- `sites/furniture/package.json`
- `sites/furniture/vite.config.ts`
- `sites/furniture/tsconfig.json`

## Output files
- `sites/furniture/src/components/sections/section-7/Section7Section.tsx`
- `sites/furniture/src/components/sections/section-7/section-7.css`

## Section images (use these only)

- `/assets/koala/img-017-7fbc8168.png`
  selector: `video` · alt: 'a woman sitting on a light gray sofa bed' · hint: `product` · primary: False
- `/assets/koala/img-018-20a78d28.png`
  selector: `video` · alt: 'short woman lying down on the Wanda Sofa Bed' · hint: `product` · primary: False

## Acceptance criteria
- typecheck
- build
- visual check at desktop/tablet/mobile
- no remote final image URLs
- use only images listed in this contract (mapped via manifest)

## Scoped source

Read this fragment with the source query helper before editing:

`$.extractions[desktop].dom_tree (section via main children[6])`
