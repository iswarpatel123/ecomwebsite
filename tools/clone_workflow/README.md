# Python clone workflow tooling

Focused Python adaptations of the reusable parts of
`Perfect-Web-Clone/backend`. The package is intended for Codex/pi subagents
and local clone-workspace scripts, not for running the old backend.

## Included modules

- `extractor.py` — `PlaywrightExtractor`, `ExtractOptions`, and `extract_url`.
  Captures page metadata, computed-style DOM tree, CSS, asset URLs, raw HTML,
  screenshots, and basic hover/focus state data. `extract_many` handles several
  viewports.
- `image_downloader.py` — `ImageDownloader`, `ImageDownloadConfig`, and
  `download_images`. Downloads/deduplicates images, preserves SVG, optionally
  resizes/compresses raster files, and can write a manifest.
- `json_source_tools.py` — `SourceStore`, `list_saved_sources`,
  `get_source_overview`, `query_source_json`, and `json_path_values`. Queries
  persisted extraction JSON without putting the whole document in a prompt.
- `task_contract.py` — `TaskContract`, `AcceptanceCriteria`,
  `create_task_contract`, and `generate_contracts`. Generates isolated
  `contracts/index.json`, Markdown contracts, and a plan for SolidStart sites.
- `section_tools.py` — compact layout and section-data selection helpers.
- `worker_agent.py` / `worker_manager.py` — callback-driven, path-validating
  section workers and bounded parallel execution. A Codex harness supplies the
  subagent callback; no LLM client is embedded.

## Examples

```python
from tools.clone_workflow.extractor import ExtractOptions, extract_url
from tools.clone_workflow.json_source_tools import SourceStore, query_source_json

result = await extract_url(
    "https://example.test",
    ExtractOptions(screenshot_path=".cloning/example/reference/desktop.png"),
)
if result.success:
    SourceStore(".cloning/example/source").save(
        result.to_dict(), source_url="https://example.test", page_title=result.metadata.title
    )

store = SourceStore(".cloning/example/source")
print(query_source_json("extraction", "$.style_summary.colors", store).to_content())
```

For direct existing-style use, the extractor also supports:

```bash
python -m tools.clone_workflow.extractor https://example.test \
  --output .cloning/example/source/extraction.json
```

This is a package-module entry point only; no new repository-level CLI or
package-manager command is added.

## Dependencies and caveats

- Core source querying, contracts, and worker orchestration use only the
  Python standard library.
- Extraction requires `playwright` and a browser install:
  `python -m pip install playwright && playwright install chromium`.
  Browser extraction is asynchronous and may be blocked by the target site's
  robots, authentication, CSP, or anti-bot controls.
- Asset downloads require `httpx`; raster optimization additionally uses
  `Pillow`. Without Pillow, raster bytes are retained without resizing or
  compression. SVG is always preserved.
- The package deliberately does **not** import or copy FastAPI, frontend or
  WebContainer code, Claude/Anthropic/OpenAI runtime code, MCP servers,
  DesignMD/designmd.me, or Figma integrations. It does not modify shared
  packages.

## Attribution

Behavior and comments were selectively adapted from the checked-in
`Perfect-Web-Clone/backend/extractor`, `backend/image_downloader`,
`backend/agent/tools/json_source_tools.py`, `backend/agent/task_contract.py`,
and worker support modules. The adaptation keeps the architecture while
removing application-specific runtime dependencies and WebContainer paths.
