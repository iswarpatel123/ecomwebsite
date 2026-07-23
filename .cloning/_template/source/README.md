# source/

Extraction artifacts produced by `npm run extract-site`.

Contents:
- `extraction.json` — DOM, computed styles/CSS, asset URLs, page HTML, viewport
  metadata, and captured interaction states (desktop / tablet / mobile).
- `source-url.txt` — the original reference URL that was extracted.
- `notes.md` — DOM/CSS observations and structural annotations used by the
  Planner to write section contracts.

This directory is the raw input. Agents must use `query-source` to read scoped
fragments rather than injecting the whole extraction JSON into a prompt.
