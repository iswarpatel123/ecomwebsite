# assets/

Downloaded original assets produced by `npm run download-assets`.

Contents:
- Downloaded images / fonts / media, deduplicated and (for raster images)
  resized/compressed. SVG is preserved.
- `manifest.json` — URL → local-path mapping. The clone's components must
  reference assets via these local paths.

**Rule:** the final clone output must not reference remote images. Every asset
used by `sites/<slug>` must be local and listed in this manifest.
