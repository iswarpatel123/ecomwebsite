"""Framework-neutral section helpers for planner and worker subagents.

This keeps the useful data-scoping part of Perfect-Web-Clone's
``section_tools.py`` without its WebContainer callbacks or LLM orchestration.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from .json_source_tools import json_path_values
from .task_contract import classify_section


SECTION_TOOL_DEFINITIONS = [
    {
        "name": "get_section_data",
        "description": "Return only the requested source keys or JSON path for a section worker.",
        "input_schema": {
            "type": "object",
            "properties": {"data_keys": {"type": "array", "items": {"type": "string"}}},
            "required": ["data_keys"],
        },
    },
    {
        "name": "validate_section_paths",
        "description": "Validate generated files against an isolated section contract.",
        "input_schema": {"type": "object", "properties": {"paths": {"type": "array", "items": {"type": "string"}}}, "required": ["paths"]},
    },
]


def get_section_data(source_data: Dict[str, Any], data_keys: Iterable[str]) -> Dict[str, Any]:
    """Select top-level keys, or JSONPath expressions beginning with ``$.``."""
    selected: Dict[str, Any] = {}
    for key in data_keys:
        if key.startswith("$"):
            values = json_path_values(source_data, key)
            if values:
                selected[key] = values[0] if len(values) == 1 else values
        elif key in source_data:
            selected[key] = source_data[key]
    return selected


def top_level_sections(dom_tree: Optional[Dict[str, Any]], *, skip_chrome: bool = True) -> List[Dict[str, Any]]:
    """Return named visual sections (main/body children), not html children.

    Delegates to ``discover_visual_sections`` so contracts and planners share
    the same section boundaries.
    """
    if not dom_tree:
        return []
    try:
        from .task_contract import discover_visual_sections
        return discover_visual_sections(dom_tree, skip_chrome=skip_chrome)
    except Exception:
        result = []
        for index, node in enumerate(dom_tree.get("children", [])):
            section_id, display_name = classify_section(node, index)
            result.append({"index": index, "id": section_id, "display_name": display_name, "node": node})
        return result


def analyze_page_layout(dom_tree: Optional[Dict[str, Any]], *, max_depth: int = 3) -> Dict[str, Any]:
    """Produce a compact layout outline suitable for a planner prompt."""
    def outline(node: Dict[str, Any], depth: int) -> Dict[str, Any]:
        result = {
            "tag": node.get("tag", "div"), "id": node.get("id"), "classes": node.get("classes", []),
            "rect": node.get("rect", {}), "children": [],
        }
        if depth < max_depth:
            result["children"] = [outline(child, depth + 1) for child in node.get("children", [])]
        return result
    return {"sections": top_level_sections(dom_tree), "outline": outline(dom_tree, 0) if dom_tree else None}
