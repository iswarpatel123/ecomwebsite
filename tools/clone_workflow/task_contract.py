"""Section contracts and scoped worker prompts.

Adapted from ``Perfect-Web-Clone/backend/agent/task_contract.py`` and
``agent/tools/section_tools.py``.  Contracts are framework-neutral metadata
for Codex subagents; they do not launch an LLM or write through WebContainer.
The generated paths follow this repository's SolidStart clone rules.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


SECTION_ALIASES = (
    ("header", ("header", "masthead", "topbar", "top-bar", "site-header"), "Header / Navigation"),
    ("nav", ("nav", "menu", "navbar", "site-nav", "primary-nav"), "Navigation"),
    ("hero", ("hero", "banner", "jumbotron", "above-the-fold"), "Hero"),
    ("footer", ("footer", "site-footer"), "Footer"),
    ("sidebar", ("sidebar", "aside"), "Sidebar"),
    ("features", ("feature", "benefits", "usps"), "Features"),
    ("testimonials", ("testimonial", "review", "social-proof"), "Testimonials"),
    ("cta", ("cta", "call-to-action"), "Call To Action"),
    ("faq", ("faq",), "FAQ"),
    ("contact", ("contact",), "Contact"),
    ("product", ("product", "pdp", "buy-box", "purchase", "product-form", "product-info"), "Product Detail"),
    ("gallery", ("gallery", "media-gallery", "product-gallery", "thumbnail"), "Product Gallery"),
    ("products", ("catalog", "product-grid", "collection"), "Product Grid"),
)

# Sections agents should skip when cloning a focused PDP body.
SKIP_SECTION_IDS = frozenset({"header", "nav", "footer"})
SKIP_HINTS = frozenset({"header-nav", "footer", "360-view"})


def classify_section(node: Dict[str, Any], index: int) -> Tuple[str, str]:
    haystack = " ".join([str(node.get("tag", "")), str(node.get("id", "")), *[str(c) for c in node.get("classes", [])]]).lower()
    for section_id, aliases, name in SECTION_ALIASES:
        if any(alias in haystack for alias in aliases):
            return section_id, name
    tag = str(node.get("tag", "")).lower()
    if tag in {"main", "article", "section"}:
        return f"{tag}-{index + 1}", f"{tag.capitalize()} {index + 1}"
    return f"section-{index + 1}", f"Section {index + 1}"


def _find_body(dom: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not dom:
        return None
    if str(dom.get("tag", "")).lower() == "body":
        return dom
    for child in dom.get("children") or []:
        found = _find_body(child)
        if found:
            return found
    return None


def _find_main(body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not body:
        return None
    stack = list(body.get("children") or [])
    while stack:
        node = stack.pop(0)
        tag = str(node.get("tag", "")).lower()
        role = str((node.get("attributes") or {}).get("role", "")).lower()
        if tag == "main" or role == "main":
            return node
        stack.extend(node.get("children") or [])
    return None


def _is_chrome_section(node: Dict[str, Any], section_id: str) -> bool:
    if section_id in SKIP_SECTION_IDS:
        return True
    haystack = " ".join(
        [str(node.get("tag", "")), str(node.get("id", "")), *[str(c) for c in node.get("classes", [])]]
    ).lower()
    return bool(re.search(r"\b(header|footer|site-nav|navbar|masthead|cookie|consent)\b", haystack))


def _node_area(node: Dict[str, Any]) -> float:
    rect = node.get("rect") or {}
    return float(rect.get("width") or 0) * float(rect.get("height") or 0)


def discover_visual_sections(
    dom_tree: Dict[str, Any],
    *,
    skip_chrome: bool = True,
    min_area: float = 20_000,
    max_sections: int = 24,
) -> List[Dict[str, Any]]:
    """Pick visual page sections suitable for parallel contracts.

    Prefer ``main`` children (or body children). Skip tiny nodes and, when
    ``skip_chrome`` is set, site chrome (header/nav/footer).
    """
    body = _find_body(dom_tree) or dom_tree
    main = _find_main(body) if body else None
    root = main or body or dom_tree
    candidates = list(root.get("children") or [])
    # If children are wrappers (single huge child), dig one level.
    if len(candidates) <= 2:
        expanded: List[Dict[str, Any]] = []
        for child in candidates:
            kids = child.get("children") or []
            if _node_area(child) > 80_000 and len(kids) >= 2:
                expanded.extend(kids)
            else:
                expanded.append(child)
        candidates = expanded

    sections: List[Dict[str, Any]] = []
    for index, node in enumerate(candidates):
        if not node.get("is_visible", True):
            continue
        if _node_area(node) < min_area and str(node.get("tag", "")).lower() not in {"section", "article", "main"}:
            continue
        section_id, display_name = classify_section(node, index)
        if skip_chrome and _is_chrome_section(node, section_id):
            continue
        sections.append({
            "index": index,
            "id": section_id,
            "display_name": display_name,
            "node": node,
            "source_root": "main" if main is not None else "body",
        })
        if len(sections) >= max_sections:
            break
    return sections


def attach_images_to_section(
    node: Dict[str, Any],
    image_usages: Sequence[Dict[str, Any]],
    *,
    skip_hints: Iterable[str] = SKIP_HINTS,
) -> List[Dict[str, Any]]:
    """Assign image usages whose vertical band overlaps this section's rect."""
    rect = node.get("rect") or {}
    top = float(rect.get("top") or rect.get("y") or 0)
    height = float(rect.get("height") or 0)
    bottom = top + max(height, 1)
    skip = set(skip_hints)
    matched: List[Dict[str, Any]] = []
    seen: set[str] = set()
    for usage in image_usages:
        hint = str(usage.get("section_hint") or "")
        if hint in skip:
            continue
        if usage.get("type") == "srcset-candidate":
            continue
        url = usage.get("url") or ""
        if not url or url in seen:
            continue
        u_top = float(usage.get("top") or 0)
        u_h = float(usage.get("height") or 0)
        u_bottom = u_top + max(u_h, 1)
        # Vertical overlap between image and section band
        if u_bottom < top - 40 or u_top > bottom + 40:
            continue
        if usage.get("is_visible") is False and not usage.get("is_primary"):
            continue
        seen.add(url)
        matched.append(dict(usage))
    return matched


@dataclass
class AcceptanceCriteria:
    required_exports: List[str] = field(default_factory=list)
    required_images: int = 0
    required_links: int = 0
    checks: List[str] = field(default_factory=list)

    def validate_files(self, files: Dict[str, str]) -> List[str]:
        warnings: List[str] = []
        content = "\n".join(files.values())
        image_count = len(re.findall(r"(?:src|href)=[\"'](?:/assets|https?://)", content))
        if image_count < self.required_images:
            warnings.append(f"Expected at least {self.required_images} image references, found {image_count}")
        link_count = len(re.findall(r"href=[\"']", content))
        if link_count < self.required_links:
            warnings.append(f"Expected at least {self.required_links} links, found {link_count}")
        for export in self.required_exports:
            if not re.search(rf"\b(?:export\s+(?:default\s+)?(?:function|const|class)|export\s*\{{[^}}]*\b){re.escape(export)}\b", content):
                warnings.append(f"Missing required export: {export}")
        return warnings


@dataclass
class TaskContract:
    contract_id: str
    worker_namespace: str
    display_name: str
    source_fragment: str
    allowed_paths: List[str]
    forbidden_paths: List[str]
    output_files: List[str]
    shared_tokens: Dict[str, Dict[str, int]] = field(default_factory=dict)
    acceptance: AcceptanceCriteria = field(default_factory=AcceptanceCriteria)
    allowed_extensions: List[str] = field(default_factory=lambda: [".tsx", ".jsx", ".css", ".md"])
    section_data: Dict[str, Any] = field(default_factory=dict)

    def is_path_allowed(self, path: str) -> bool:
        normalized = path.replace("\\", "/").lstrip("./")
        for forbidden in self.forbidden_paths:
            pattern = forbidden.replace("**", "").replace("*", "")
            if normalized == forbidden.lstrip("/") or (pattern and pattern.lstrip("/") in normalized):
                return False
        allowed = [item.replace("/*", "").lstrip("/") for item in self.allowed_paths]
        return any(normalized == item or normalized.startswith(item.rstrip("/") + "/") for item in allowed) and any(normalized.endswith(ext) for ext in self.allowed_extensions)

    def validate_files(self, files: Dict[str, str]) -> List[str]:
        errors = [f"Path is outside contract: {path}" for path in files if not self.is_path_allowed(path)]
        errors.extend(self.acceptance.validate_files(files))
        return errors

    def to_dict(self) -> Dict[str, Any]:
        value = asdict(self)
        value["acceptance"] = asdict(self.acceptance)
        return value

    def worker_prompt(self) -> str:
        """Build a concise prompt containing only this worker's source fragment."""
        source = json.dumps(self.section_data, ensure_ascii=False, indent=2)
        return f"""# Section contract: {self.contract_id}

You are the isolated implementer for **{self.display_name}** (`{self.worker_namespace}`).
You may write ONLY these paths:
{chr(10).join(f'- {p}' for p in self.allowed_paths)}
Do not edit: {', '.join(self.forbidden_paths)}.

Source fragment (do not invent content):
```json
{source[:12000]}
```

Output files: {', '.join(self.output_files)}
Use local `/assets/...` paths for downloaded images. Preserve semantics, text,
links, classes, and responsive behavior. The integrator owns the app shell,
routes, global CSS, and imports.
"""


def _desktop_extraction(document: Dict[str, Any]) -> Tuple[Dict[str, Any], str, List[str]]:
    if "extractions" in document:
        extractions = document.get("extractions", [])
        if not extractions:
            return {}, document.get("url", ""), []
        selected = max(extractions, key=lambda item: item.get("viewport", {}).get("width", 0))
        return selected, document.get("url", ""), [item.get("viewport", {}).get("name", "") for item in extractions]
    return document, document.get("metadata", {}).get("url", document.get("url", "")), []


def create_task_contract(section_id: str, display_name: str, section_data: Dict[str, Any], *, source_fragment: str = "", site_slug: str = "<slug>", index: int = 0) -> TaskContract:
    namespace = re.sub(r"[^a-z0-9_-]+", "-", section_id.lower()).strip("-") or f"section-{index + 1}"
    section_dir = f"sites/{site_slug}/src/components/sections/{namespace}"
    images = section_data.get("images", [])
    links = section_data.get("links", [])
    component_name = "".join(part.capitalize() for part in re.split(r"[-_ ]+", namespace)) or "Section"
    if not component_name.endswith("Section"):
        component_name += "Section"
    image_lines = []
    if isinstance(images, list):
        for img in images[:40]:
            if isinstance(img, dict):
                image_lines.append(
                    f"- `{img.get('url', '')}` → selector `{img.get('selector', '')}` "
                    f"alt={img.get('alt')!r} hint={img.get('section_hint')!r} "
                    f"primary={img.get('is_primary')}"
                )
            else:
                image_lines.append(f"- `{img}`")
    return TaskContract(
        contract_id=f"{namespace}_contract",
        worker_namespace=namespace,
        display_name=display_name,
        source_fragment=source_fragment,
        allowed_paths=[section_dir, f"{section_dir}/*"],
        forbidden_paths=[
            f"sites/{site_slug}/src/app.tsx", f"sites/{site_slug}/src/app.css",
            f"sites/{site_slug}/src/routes/**", f"sites/{site_slug}/package.json",
            f"sites/{site_slug}/vite.config.ts", f"sites/{site_slug}/tsconfig.json",
        ],
        output_files=[f"{section_dir}/{component_name}.tsx", f"{section_dir}/{namespace}.css"],
        section_data=section_data,
        acceptance=AcceptanceCriteria(
            required_exports=[component_name],
            required_images=len(images) if isinstance(images, list) else 0,
            required_links=len(links) if isinstance(links, list) else 0,
            checks=[
                "typecheck",
                "build",
                "visual check at desktop/tablet/mobile",
                "no remote final image URLs",
                "use only images listed in this contract (mapped via manifest)",
            ],
        ),
    )


def generate_contracts(
    document: Dict[str, Any],
    output_dir: str,
    *,
    site_slug: Optional[str] = None,
    skip_chrome: bool = True,
) -> List[TaskContract]:
    """Generate machine-readable and Markdown contracts from visual sections.

    Uses ``main``/``body`` children (not ``html`` children) and attaches
    section-scoped image usages so workers know which local assets apply.
    """
    selected, source_url, viewports = _desktop_extraction(document)
    slug = site_slug or document.get("slug", "<slug>")
    dom = selected.get("dom_tree") or {}
    summary = selected.get("style_summary") or {}
    assets = selected.get("assets") or {}
    image_usages = assets.get("image_usages") or []
    if not image_usages:
        # Fall back to flat image list with any usage metadata already on items.
        image_usages = assets.get("images") or []
    tokens = {
        "colors": summary.get("colors", {}),
        "fonts": summary.get("font_families", summary.get("fontFamilies", {})),
        "spacing": {**summary.get("margins", {}), **summary.get("paddings", {})},
    }
    discovered = discover_visual_sections(dom, skip_chrome=skip_chrome)
    contracts: List[TaskContract] = []
    used: set[str] = set()
    for entry in discovered:
        index = entry["index"]
        section_id = entry["id"]
        display_name = entry["display_name"]
        node = dict(entry["node"])  # shallow copy so we can attach images
        if section_id in used:
            section_id = f"{section_id}-{index + 1}"
        used.add(section_id)
        section_images = attach_images_to_section(node, image_usages)
        node["images"] = section_images
        node["image_urls"] = [img.get("url") for img in section_images if img.get("url")]
        root_name = entry.get("source_root", "body")
        fragment = f"$.extractions[desktop].dom_tree (section via {root_name} children[{index}])"
        contract = create_task_contract(
            section_id, display_name, node,
            source_fragment=fragment, site_slug=slug, index=index,
        )
        contract.shared_tokens = tokens
        contracts.append(contract)

    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    index_payload = {
        "slug": slug,
        "source_url": source_url,
        "skip_chrome": skip_chrome,
        "section_count": len(contracts),
        "sections": [c.to_dict() for c in contracts],
    }
    (directory / "index.json").write_text(
        json.dumps(index_payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    for index, contract in enumerate(contracts, 1):
        images = contract.section_data.get("images") or []
        lines = [
            f"# Contract {index:02d}: {contract.display_name}",
            "",
            f"- **Section id:** `{contract.worker_namespace}`",
            f"- **Source fragment:** `{contract.source_fragment}`",
            f"- **Images in this section:** {len(images)}",
            "",
            "## Allowed paths",
        ]
        lines.extend(f"- `{item}`" for item in contract.allowed_paths)
        lines.extend(["", "## Forbidden paths"])
        lines.extend(f"- `{item}`" for item in contract.forbidden_paths)
        lines.extend(["", "## Output files"])
        lines.extend(f"- `{item}`" for item in contract.output_files)
        lines.extend(["", "## Section images (use these only)", ""])
        if images:
            for img in images:
                if isinstance(img, dict):
                    lines.append(
                        f"- `{img.get('url', '')}`  \n"
                        f"  selector: `{img.get('selector', '')}` · "
                        f"alt: {img.get('alt')!r} · hint: `{img.get('section_hint', '')}` · "
                        f"primary: {img.get('is_primary')}"
                    )
                else:
                    lines.append(f"- `{img}`")
        else:
            lines.append("_No images mapped to this section._")
        lines.extend(["", "## Acceptance criteria"])
        lines.extend(f"- {item}" for item in contract.acceptance.checks)
        lines.extend([
            "",
            "## Scoped source",
            "",
            "Read this fragment with the source query helper before editing:",
            "",
            f"`{contract.source_fragment}`",
            "",
        ])
        (directory / f"{index:02d}-{contract.worker_namespace}.md").write_text(
            "\n".join(lines), encoding="utf-8"
        )
    plan = [
        f"# Clone plan: {slug}",
        "",
        f"Source: {source_url}",
        f"Viewports: {', '.join(viewports) or 'single extraction'}",
        f"Chrome skipped: {skip_chrome}",
        "",
        "## Parallel sections",
    ]
    for index, c in enumerate(contracts, 1):
        n_img = len(c.section_data.get("images") or [])
        plan.append(f"- **{index:02d} {c.display_name}** (`{c.worker_namespace}`) — {n_img} images")
    plan.extend([
        "",
        "The integrator alone owns the app shell, routes, global styles, and section imports.",
        "Each section worker must use only the images listed in its contract, resolved via `public/assets/manifest.json`.",
    ])
    (directory / "plan.md").write_text("\n".join(plan) + "\n", encoding="utf-8")
    return contracts
