# Workflow: clone a website from a URL and slug

## Mission and inputs

Receive a reference `URL`, produce an independent SolidStart/SolidJS clone at `sites/<slug>`. The site boundary is enforced: do not modify another site or shared package merely to match the reference.

The reference DOM, computed CSS, CSS rules/variables, assets, screenshots, and captured interaction data are the source of truth. The pipeline is:

```text
live URL -> Playwright DOM/CSS/assets/state data -> scoped contracts
          -> isolated SolidJS section workers -> integrator
          -> visual + DOM/functional QA -> automatic repair loops
```

Preserve semantic structure, responsive behavior, controls, links, and important transitions. Use a screenshot to aid implementation if needed.
Final imagery must be local; no browser image proxy or remote image URL may remain in `sites/<slug>`.

You are the coordinator and must dispatch the subagents below. Max turns per agent has to be 50 or more

### Tools
- `Playwright` - Browser automation for extraction
- `pnpm` - Package management and workspace execution
- Agents - Orchestrated by the coordinator, each agent has access to read, write, bash, and edit tools

## Required artifacts

`run-clone` creates the workspace from `.cloning/_template`:

```text
.cloning/<slug>/
  source/
    extraction.json       # extraction document
    section-notes.md      # section specifications
  reference/
    <slug>-desktop.png
    <slug>-tablet.png
    <slug>-mobile.png
    <slug>-desktop-popup.png  # user-provided popup screenshot
  assets/
    manifest.json         # URL -> local public asset mapping
  contracts/
    plan.md               # integration plan
    01-section1.md        # section contracts
    02-section2.md
    ...
    index.json            # contracts index
  reports/
    visual-qa.md          # visual comparison report (must write)
    dom-functional.md     # DOM/functional QA report (must write)
    repair-log.md         # repair attempts
    final.md              # final verification
```

## Agents orchestration protocol

### Step 1: Planner/Extractor Agent
**Agent to use**: `planner-extractor`
**Location**: `.pi/agents/planner-extractor.md`

**What it does**: Extracts DOM/CSS/assets from the target URL, handles popups/modals, generates **section-scoped** contracts, downloads **usage-mapped** assets, and sets up the workspace.

**Key responsibilities**:
- Dismiss popups/modals before screenshots (`dismiss_popups=True`; Escape, accept/close, hide residual overlays)
- If popup cannot be closed, request human screenshot and save it under `reference/<slug>-desktop-popup.png`
- Extract DOM/CSS/assets at desktop/tablet/mobile viewports with **image usage metadata**
- Discover visual sections under `main`/`body` (skip header/nav/footer for PDP-focused clones)
- Download only selected images via `download_from_extraction` (not full asset dump); write manifest `usage_index`
- Generate contracts with per-section image lists
- Create extraction.json and section-notes.md (including URL → local path → section map)

**Success criteria**: Clean multi-viewport extraction, scoped assets with usage_index, contracts with section images, workspace organized.

---

### Step 2: Section Worker Agent
**Agent**: `section-worker`
**Location**: `.pi/agents/section-worker.md`

**What it does**: Implements the page section components based on the contract and source extraction.

**Key responsibilities**:
- Read all input artifacts (contract, extraction, notes, manifest)
- Create section components (e.g., HeroSection, FeaturesSection, etc.) based on contracts
- Create section-specific CSS files with responsive layout
- Ensure all local assets are used, no remote URLs
- Support keyboard navigation and accessibility

**Success criteria**: Components exist, exports all sections, all assets rendered, all interactions work, responsive layout correct.

---

### Step 3: Integrator Agent
**Agent**: `integrator`

**What it does**: Assembles the page sections into a working SolidStart site by configuring app shell and routes.

**Key responsibilities**:
- Configure app.tsx (remove template navigation, add section shell)
- Configure app.css (reset defaults, add base styles)
- Create/update routes/index.tsx (render all sections)
- Verify no remote asset URLs exist
- Run typecheck, build, dev server, e2e and visual tests

**Success criteria**: App shell configured, routes render all sections, all tests pass.

---

### Step 4: Visual QA Agent
**Agent**: `visual-qa`

**What it does**: Compares source screenshots against clone screenshots to ensure pixel-accurate reproduction.

**Key responsibilities**:
- Check for popup artifacts (if popup screenshot exists, crop to clean section)
- Compare page section screenshots (crop to target area)
- Verify element counts, positions, sizes, colors, styling match exactly
- Report any extra/missing elements, styling differences
- Generate pixel diff PNGs and comparison reports

**Success criteria**: No popup artifacts, page matches source exactly, all acceptance criteria met.

---

### Step 5: DOM/Functional QA Agent
**Agent**: `dom-functional-qa` (general-purpose, high thinking)

**What it does**: Validates the cloned page sections' semantic structure, functionality, and accessibility.

**Key responsibilities**:
- Capture DOM snapshots at all viewports
- Verify semantic markup, headings, ARIA labels, alt attributes
- Test interactive functionality (buttons, forms, navigation, keyboard)
- Verify content (brand, title, product information, section-specific elements)
- Check console for errors, validate against source extraction

**Success criteria**: Semantic structure correct, all sections rendered, all interactions work, keyboard navigation functional, no console errors.

---

### Step 6: Fixer Agent (activated on QA failure)
**Agent**: `fixer`
**Location**: `.pi/agents/fixer.md`

**What it does**: Repairs clone failures identified by QA agents, using their written reports as contracts.

**Key responsibilities**:
- Read `.cloning/<slug>/reports/{visual-qa.md,dom-functional.md}` for failures.
- Identify the minimal owning file(s) to fix.
- Apply narrow changes (CSS, markup) without touching other sections.
- Re-run relevant QA checks and record progress in repair-log.md.
- Stop after 5 identical repair attempts or when all QA passes.

**Success criteria**: Failing QA transitions to PASS; no regressions introduced.

---

## Automatic repair loop

1. After QA agents complete, check `.cloning/<slug>/reports/{visual-qa.md,dom-functional.md}`.
2. If FAIL status present for any implemented section, **activate Fixer agent** (`fixer.md`).
3. Fixer reads reports and applies minimal bounded fixes.
4. Re-run only the failing checks for that section.
5. If fix succeeds, update reports; if identical repair attempted ≥ 5 times, record in final.md and stop.
6. Repeat until all QA passes or cap reached.

**Final gate**:
```bash
npm --workspace sites/<slug> run typecheck
npm --workspace sites/<slug> run build
npm --workspace sites/<slug> run test:visual
npm --workspace sites/<slug> run test:e2e
```

**Human input fallback**: When automation fails and human screenshot is needed, provide screenshot of page with popup visible. Visual QA will crop to clean section and report popup as intentional difference.
