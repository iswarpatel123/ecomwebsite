## DOM/Functional QA Report: hero

- **Status**: PASS
- **Scope**: hero (product section)
- **Viewport checks**: desktop / tablet / mobile

### Findings
All functional tests passed:

#### Semantic Structure
- ✓ h1 heading found: "Wanda Sofa Bed"
- ✓ Heading hierarchy correct (single h1 in hero)
- ✓ Semantic `<fieldset>` used for size and color selections

#### Accessibility
- ✓ All images have alt attributes
- ✓ ARIA labels present on all interactive elements (23 total)
- ✓ `aria-pressed` on variant buttons
- ✓ `aria-current` on selected thumbnail
- ✓ Focus-visible styles implemented

#### Interactive Functionality
- ✓ Gallery thumbnails clickable
- ✓ Prev/next navigation buttons work
- ✓ Size selection toggles between "75" and "99"
- ✓ Color swatches selectable (8 options)
- ✓ Quantity controls bounded (1–10)
- ✓ Add-to-cart button responsive and shows feedback

#### No Remote URLs
- ✓ No `https://` URLs present in hero HTML
- ✓ All assets resolved to `/assets/koala/` paths

### Evidence
- Server respond 200 at http://127.0.0.1:3001
- Build output shows no errors