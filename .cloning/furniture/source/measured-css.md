# Koala Measured CSS — Collection Grid & Nav Dropdown

Source: https://us.koala.com/collections/bangalow-modular-sofas · viewport 1440×900

## Page backgrounds
- **Page body:** `rgb(245, 246, 243)` (#F5F6F3)
- **Dropdown panel (`.mega-menu-wrapper`):** `rgb(245, 246, 243)`
- **Same value** — mega-menu is a full-bleed surface extension, not a white popover.

## Collection grid
- **display:** `grid`
- **gridTemplateColumns:** `324.656px 324.672px 324.656px`
- **gap:** `24px`
- **padding:** `0px`

## Product card (`.card`)
- **backgroundColor:** `rgb(255, 255, 255)`
- **borderRadius:** `16px`
- **border:** `0px solid rgb(223, 222, 213)`
- **boxShadow:** `none`

## Product image
- **borderRadius:** `16px 16px 0px 0px`
- **aspectRatio:** `auto 1920 / 1440`

## Title (`.card__heading`)
- **fontSize / weight / color:** `16px / 500 / rgb(38, 38, 38)`

## Border model
Live theme sets `--product-card-border-width: 0`; design token default is `1px solid #dfded5`.
White rounded cards (`16px`) + `24px` gap create the card silhouette. Clone uses the `1px` outline token so tiles read as bordered (matches user report + dropdown tile border color).

## Nav dropdown
- **Panel:** full-bleed `1440px` × `505.422px`, bg `rgb(245, 246, 243)`, no box-shadow
- **Inner padding:** `32px 50px`
- **Title:** `32px / 600`
- **Shop all button:** bg `rgb(105, 108, 88)`, radius `100.1px`, padding `16px 32px`
- **Tile grid:** `174.281px` ×7, gap `32px 20px`
- **Category tile (`lazy-image`):** `1px solid rgb(223, 222, 213)`, bg `#fff`, radius `8px`, image ~`172×131` (4:3)
- **Tile label:** `14px / 500 / rgb(82, 82, 82)`

## Notes
- Collection uses gap-separated white cards (24px gap), not shared grid border lines.
- Grid li/cell has 0px border; visual card is inner .card with white bg + 16px radius.
- Product image top corners rounded 16px; aspect ratio ~4:3 (1920/1440).
- Page background: rgb(245, 246, 243) (#F5F6F3).
- Page and dropdown panel share the same bg: rgb(245, 246, 243) (not a white floating card).
