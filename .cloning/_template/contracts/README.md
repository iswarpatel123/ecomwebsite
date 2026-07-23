# contracts/

Section contracts authored by the Planner/extractor.

Contents:
- `plan.md` — overall section plan and section ordering.
- `01-<section>.md`, `02-<section>.md`, ... — one contract per section.

Each contract defines a worker's:
- input (source fragment from `query-source`),
- allowed edit paths (only `sites/<slug>/src/components/<section>/` and its CSS),
- shared tokens,
- acceptance criteria,
- output files.

Section workers must not edit `App.tsx`, global CSS, or package manifests. The
integrator alone owns the app shell, routes, global styles, and section imports.
