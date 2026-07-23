# Clone verification scripts

These scripts are intentionally isolated from `packages/` and do not edit the
clone skill. They keep artifacts in `.cloning/<slug>/reference` and
`.cloning/<slug>/reports`.

```bash
# Responsive reference and interaction states (requires Python Playwright)
python tools/clone_workflow/verification/capture_states.py \
  --url https://reference.example --slug my-site \
  --viewports desktop=1440x900,tablet=768x1024,mobile=390x844

# Compare one pair, or use --reference-dir/--actual-dir for matching PNG trees
python tools/clone_workflow/verification/screenshot_diff.py --slug my-site \
  --reference .cloning/my-site/reference/my-site-desktop.png \
  --actual .cloning/my-site/reports/clone-desktop.png

# Compare one HTML snapshot pair and companion computed-style JSON files
python tools/clone_workflow/verification/dom_assertions.py --slug my-site \
  --reference .cloning/my-site/reference/states/desktop/baseline-full.html \
  --actual .cloning/my-site/reports/clone-desktop.html
```

`capture_states.py` captures responsive baselines, hover/focus/active controls,
reversible disclosure controls, and detectable theme toggles. State failures are
listed in `reference/capture-manifest.json`; one failed control does not discard
other captures. The other two scripts use only the Python standard library,
including a small PNG reader/writer, so no visual SaaS or paid service is
involved.
