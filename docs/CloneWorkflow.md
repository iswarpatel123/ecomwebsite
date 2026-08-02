# Clone workflow (flexible, main-agent driven)

## Role of the main agent

You are the **coordinator**. You interpret the human task, pick the **minimum** set of subagents, and pass each one a **focused brief** so *your* context stays small (token savings).

Subagents do the heavy work: browsing, screenshots, downloads, implementing sections, wiring routes, QA. You decide **what** and **in what order**; they decide **how** within their guidelines.

There is **no fixed step ladder**. A task may need only media download, only one section rebuild, multi-site mashup into patterns, or a fuller site assemble. Skip agents that do not apply.

**Max turns per subagent:** ≥ 50 unless the task is trivially small.

---

## Goals (not pixel-perfect)

| Prefer | Avoid |
|--------|--------|
| Faithful **layout, hierarchy, copy intent, interactions** | Pixel-diff cloning |
| **Screenshots + vision** as primary reference | Full DOM dump for every job |
| **Section-level** work | Cloning entire PDPs when only a band is needed |
| Local media when the clone must ship files | Remote image/video URLs in `sites/*` |
| Patterns under shared/storefront libs when asked | Copy-pasting the same section into many sites by hand without a pattern |

Documented third-party **embeds** (YouTube/Vimeo) may keep embed URLs. Final product imagery/video files should be **local** under the target site (or pattern package) when the task requires them.

Site boundary: do not edit other sites or shared packages just to “match” a reference unless the task explicitly says so (e.g. “add to storefront patterns”).

---

## Example tasks → how you might orchestrate

These are **illustrative**, not checklists.

### A. “Clone section X from site1 and section Y from site2 into storefront patterns; use on `sites/furniture`”

1. **extractor** (or **general-vision**): screenshot + short notes for section X and Y only (two URLs, scoped viewports).
2. Optional **media** path: if patterns need real assets, run extraction/download for those sections only.
3. **section-worker** or **builder**: implement pattern components (paths given in your brief).
4. **builder** / **integrator**: wire patterns into `sites/furniture`.
5. **visual-qa** only if you care about acceptance; **not** pixel-perfect.
6. **fixer** only on real failures.

### B. “Download media from site X PDP and use them in site X”

1. **extractor** (structure/media mode) or scripts via **planner-extractor** / **general**: capture PDP, list `image_usages` / `media_usages`.
2. Scoped download → `sites/<slug>/public/assets/...` + manifest.
3. **builder** or **section-worker**: point components at local paths.
4. Skip full clone pipeline.

### C. “Rebuild hero with complex carousel transitions”

1. **extractor**: multi-shot — idle, after next/prev, key breakpoints; note transition behavior in notes (not every CSS rule).
2. **section-worker** + brief: approximate transitions in SolidJS/CSS (good enough, not frame-identical).
3. Light visual QA on states you care about.

### D. “Full-ish storefront from one URL”

1. Screenshots / section inventory first.
2. Contracts or freeform briefs per section.
3. Parallel **section-worker**s if independent.
4. **integrator** for shell/routes.
5. QA + **fixer** as needed.

---

## Decision tree (main agent)

```text
Task arrives
  │
  ├─ Need to SEE layout / states?     → extractor (screenshots default)
  │     └─ Complex UI / clicks?       → multi-screenshot / click journey
  │
  ├─ Need LOCAL media files?          → DOM/asset extract + scoped download
  │     (only then prefer full extract tools)
  │
  ├─ Need implement UI?               → section-worker (one section)
  │                                     builder (broader site/pattern work)
  │
  ├─ Need shell/routes/assembly?      → integrator
  │
  ├─ Need quality check?              → visual-qa (vision, structural)
  │     └─ Failures?                  → fixer
  │
  └─ None of the above fit?           → general / general-vision
```

**Default clone path = screenshots (+ optional short notes), not “download the whole site.”**  
Full Playwright extract + media download is an **opt-in** when the brief needs real files or structural selectors.

---

## Agent roster

Definitions live under `.pi/agents/`. Each file has **general guidelines**. Your dispatch prompt must add **task-specific guidance**: URLs, slug, target paths, section names, viewports, which screenshots matter, whether media download is required, acceptance bar, and what *not* to touch.

| Agent | File | When to use |
|-------|------|-------------|
| **extractor** | `extractor.md` | Screenshots, multi-state captures, click journeys, optional DOM/CSS/asset listing. Vision-capable. Default for “look at the reference.” |
| **planner-extractor** | `planner-extractor.md` | When you want contracts + scoped media download + workspace notes in one pass (heavier). Prefer only if that packaging helps workers. |
| **section-worker** | `section-worker.md` | Implement **one** section under `sites/<slug>/src/components/sections/<name>/` (or paths you specify). |
| **builder** | `builder.md` | Broader implementation: multi-file site work, storefront patterns, wiring product data, non-section paths. |
| **integrator** | `integrator.md` | App shell, routes, global CSS, compose sections into a page. |
| **visual-qa** | `visual-qa.md` | Structural/visual comparison (layout, hierarchy, obvious mismatches)—**not** pixel-perfect gate. |
| **fixer** | `fixer.md` | Minimal repairs from QA reports or your failure list. |
| **general** | `general.md` | Catch-all when no specialist fits (scripts, packaging, docs, odd glue). |
| **general-vision** | `general-vision.md` | Catch-all that needs to **see** images/screenshots. |

Use **general** / **general-vision** freely when a specialized agent would fight its own scope rules.

---


Ask subagents to **write artifacts to disk** (`.cloning/<slug>/...` or site paths) and return **paths + short summary**, not full extraction dumps.

Parallelize independent section-workers. Serialize when one agent’s outputs are another’s inputs.

---

## Artifacts (use what you need)

Workspace is optional scaffolding, not a mandatory tree for every job.

```text
.cloning/<slug>/                    # optional run workspace
  source/                           # notes, extraction.json if used
  reference/                        # screenshots (primary reference)
  assets/                           # copy of manifest if useful
  contracts/                        # only if you generate contracts
  reports/                          # QA / extraction reports
```

Sites still own runtime assets, e.g. `sites/<slug>/public/assets/...`.

For multi-source mashups, use clear names:  
`.cloning/<run-id>/reference/site1-hero-desktop.png`, etc.

`run-clone` / `.cloning/_template` may still bootstrap a workspace when useful; do not invent a full tree if a one-off media pull is enough.

---

## Modes of extraction

### 1. Screenshot-first (default)

- Capture relevant viewports / scroll positions / UI states.
- Dismiss popups when possible; document if stuck.
- Short notes: section list, key interactions, colors/fonts if obvious.
- **No** full asset download.

### 2. Media download (when needed)

- Extract with asset listing (`image_usages`, `media_usages`).
- Download **scoped** URLs only (`download_from_extraction` / curated `download_from_url_list`).
- Never dump every image on the page.
- Manifest + `usage_index`; embeds recorded, not downloaded.

### 3. Interaction / multi-state (when needed)

- Click carousels, tabs, variant swatches, expanders.
- Save one screenshot per meaningful state.
- Note behavior for implementers (autoplay, loop, swipe)—approximate in CSS/JS is fine.

Tools: `tools/clone_workflow/` (Playwright extractor, image downloader, contracts helpers). System Python: `/usr/bin/python3`. Prefer file-path screenshots, not base64 in JSON.

---

## Implementation guidelines (for briefs)

- SolidStart / SolidJS under `sites/<slug>` (or packages if the task says patterns).
- Section isolation when using **section-worker**: only that section’s directory.
- Local media paths from manifest; no hotlinked product images.
- Responsive enough for desktop + mobile unless scoped otherwise.
- A11y: labels, keyboard for interactive controls you implement.
- **Good enough** visual match: structure, spacing rhythm, type hierarchy, CTA emphasis—not 1:1 pixels.

---

## QA and repair (optional loops)

Only run QA when the task needs a quality bar.

1. **visual-qa**: compare reference screenshots vs clone; report structural issues; write `reports/visual-qa.md` if using `.cloning`.
3. **fixer**: minimal edits; re-check only what failed; log attempts; stop after ~5 identical failed attempts.

Final gates when a full site was assembled (adjust filter to the site):

```bash
pnpm --filter @dropshipping/site-<slug> run typecheck
pnpm --filter @dropshipping/site-<slug> run build
# tests only if the site has them and the task cares
```

---

## Tools available to the ecosystem

- **Playwright** / `tools/clone_workflow` — browse, screenshot, extract, download
- **pnpm** / Turborepo — workspace install, typecheck, build, deploy scripts
- **Vision models** — extractor, visual-qa, general-vision (read image files)
- **Subagents** — isolated contexts; main agent orchestrates

---

## Anti-patterns

- Running the entire Step-1…Step-6 pipeline for a media-only or single-section task
- Pixel-diff as a hard gate
- Full-page image dumps “just in case”
- Pasting multi-MB `extraction.json` into the main agent chat
- Editing shared packages or other sites without an explicit task
- Forcing **section-worker** when the work is multi-package / pattern library (**builder** or **general** instead)
- Skipping **general** / **general-vision** when specialists’ scopes block the real task

---

## Human fallback

If automation cannot clear a popup or captcha, ask for a human screenshot. Continue from that file path; do not block the whole job on perfect automation.
