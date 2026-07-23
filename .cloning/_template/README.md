# Clone Workspace Template

This directory is the committed template for per-site clone workspaces. It is the
source of truth for the layout required by `setup-instructions.txt` (section 1.2).

When starting a new clone, copy this template to a slug-named directory:

```bash
cp -r .cloning/_template .cloning/<slug>
```

Then populate the subfolders below with per-slug artifacts. **Never edit shared
packages merely to match one reference site.** Clones always live under
`sites/<slug>`.

- `source/`      — extraction JSON, source URL, DOM/CSS notes.
- `reference/`   — original screenshots by viewport/state.
- `assets/`      — manifest and downloaded original assets.
- `contracts/`   — plan + one contract per section.
- `reports/`     — visual-diff and verification reports.

See `setup-instructions.txt` and `AGENTS.md` ("Website Cloning Workflow") for the
full pipeline, agent contracts, and required checks (`typecheck`, `build`,
Playwright visual checks).
