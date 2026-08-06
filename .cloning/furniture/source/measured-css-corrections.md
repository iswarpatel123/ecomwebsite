# Measured CSS corrections (border probe)

Follow-up to `measured-css.json` after walking card/mega descendants.

## Dropdown tiles (confirmed)
- Panel bg: `rgb(245, 246, 243)` = page body (`#F5F6F3`)
- Tile image wrapper (`lazy-image`): `1px solid rgb(223, 222, 213)` (`#DFDED5`), bg `#fff`, radius `8px`
- Aspect ~1920/1440 (not 1:1)
- Gap `32px 20px`; labels `14px / 500 / rgb(82, 82, 82)`
- Header: title `32px / 600`; Shop all `rgb(105, 108, 88)`, pill, `16px 32px`

## Collection cards
- Live theme sets `--product-card-border-width: 0.0rem` → computed border width `0`
- Stylesheet default token is still `1px solid #dfded5` (`.product-card-wrapper .card--standard`)
- White card shell + `16px` radius + `24px` grid gap are the dominant card silhouette
- Clone applies `1px solid #DFDED5` so cards read as outlined tiles (user-reported gap vs reference screenshots / design token)
