# Nav Mega-Menu vs Typical White Card Dropdown

- **Panel background** is `rgb(245, 246, 243)` — identical to page body `rgb(245, 246, 243)`; not a floating white card on gray.
- **Full-bleed layout:** `.mega-menu-wrapper` spans `1440px` under the header; position `absolute`.
- **No drop shadow** on panel (`boxShadow: none`); separation is via layout shift, not elevation.
- **No rounded outer container** — square full-width band, unlike typical card popovers.
- **Inner content** constrained with `padding: 32px 50px` inside `.mega-menu--inner` (page-width).
- **Header row** (`.mega-menu__complex-header`): flex row with `32px` title + olive `rgb(105, 108, 88)` pill button.
- **Category tiles:** 7-column grid, `32px 20px` gap; tiles are image+label links without card borders.
- **Second row** includes wider lifestyle/collection promo tiles (Bangalow, Tamarama, etc.) distinct from compact category thumbs.
- **Hover-triggered** via `.header__mega-menu`; body gets `mega-menu--active has-dropdown-menu` class.
- **Content pushes page down** rather than overlaying — mega-menu is in document flow below header, not a fixed overlay.
