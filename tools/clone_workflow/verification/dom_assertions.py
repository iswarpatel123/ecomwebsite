#!/usr/bin/env python3
"""Assert semantic DOM and computed-style parity for a clone.

The inputs are the ``*.html`` and companion ``*.json`` snapshots produced by
``capture_states.py``. The checker compares structural tags, ARIA semantics,
class shape, and computed values. Numeric CSS values ending in ``px`` tolerate
one pixel; transition durations are normalized to milliseconds.

Example:
  python .../dom_assertions.py --slug furniture \
    --reference .cloning/furniture/reference/states/desktop/baseline-full.html \
    --actual .cloning/furniture/reference/states/desktop/baseline-full.html
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from typing import Any

try:
    from .common import resolve_workspace
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from common import resolve_workspace  # type: ignore


@dataclass
class Node:
    tag: str
    attrs: dict[str, str]
    children: list["Node"] = field(default_factory=list)


class _TreeParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Node("#document", {})
        self.stack = [self.root]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        node = Node(tag.lower(), {key.lower(): value or "" for key, value in attrs})
        self.stack[-1].children.append(node)
        if tag.lower() not in {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}:
            self.stack.append(node)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if self.stack[-1].tag == tag.lower():
            self.stack.pop()

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag.lower():
                del self.stack[index:]
                break


def _elements(html: str) -> list[Node]:
    parser = _TreeParser()
    parser.feed(html)
    result: list[Node] = []
    def visit(node: Node) -> None:
        for child in node.children:
            result.append(child)
            visit(child)
    visit(parser.root)
    return result


def _semantic_attrs(node: Node) -> dict[str, str]:
    keys = {"role", "tabindex", "type", "name", "alt", "for", "disabled", "hidden", "open", "title"}
    return {key: value for key, value in node.attrs.items() if key in keys or key.startswith("aria-")}


def _class_shape(node: Node) -> tuple[bool, int]:
    raw = node.attrs.get("class", "").strip()
    return bool(raw), len(raw.split()) if raw else 0


def _numeric(value: str) -> tuple[float, str] | None:
    match = re.fullmatch(r"\s*(-?(?:\d+(?:\.\d*)?|\.\d+))\s*(px|ms|s)?\s*", value.lower())
    if not match:
        return None
    number, unit = float(match.group(1)), match.group(2) or ""
    if unit == "s":
        number *= 1000
        unit = "ms"
    return number, unit


def _same_value(reference: Any, actual: Any, key: str) -> bool:
    if reference == actual:
        return True
    if not isinstance(reference, str) or not isinstance(actual, str):
        return False
    left, right = _numeric(reference), _numeric(actual)
    if left and right and left[1] == right[1] and left[1] in {"px", "ms", ""}:
        tolerance = 0.01 if "transition" in key.lower() or left[1] == "ms" else 1.0
        return abs(left[0] - right[0]) <= tolerance
    return False


def _load_records(path: Path | None) -> list[dict[str, Any]]:
    if not path or not path.exists():
        return []
    value = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, dict):
        for key in ("elements", "nodes", "computedStyles"):
            if isinstance(value.get(key), list):
                return [item for item in value[key] if isinstance(item, dict)]
    return []


def assert_dom(reference_html: Path, actual_html: Path, reference_json: Path | None = None, actual_json: Path | None = None, ignore_class_shape: bool = False) -> dict[str, Any]:
    reference_nodes, actual_nodes = _elements(reference_html.read_text(encoding="utf-8")), _elements(actual_html.read_text(encoding="utf-8"))
    failures: list[dict[str, Any]] = []
    checks = 0
    for index in range(max(len(reference_nodes), len(actual_nodes))):
        if index >= len(reference_nodes):
            failures.append({"kind": "extra-element", "index": index, "actual": actual_nodes[index].tag})
            continue
        if index >= len(actual_nodes):
            failures.append({"kind": "missing-element", "index": index, "reference": reference_nodes[index].tag})
            continue
        reference, actual = reference_nodes[index], actual_nodes[index]
        checks += 1
        if reference.tag != actual.tag:
            failures.append({"kind": "tag", "index": index, "reference": reference.tag, "actual": actual.tag})
            continue
        expected_attrs = _semantic_attrs(reference)
        actual_attrs = _semantic_attrs(actual)
        for key in sorted(set(expected_attrs) | set(actual_attrs)):
            checks += 1
            if expected_attrs.get(key) != actual_attrs.get(key):
                failures.append({"kind": "semantic-attribute", "index": index, "tag": reference.tag, "attribute": key, "reference": expected_attrs.get(key), "actual": actual_attrs.get(key)})
        if not ignore_class_shape:
            checks += 1
            if _class_shape(reference) != _class_shape(actual):
                failures.append({"kind": "class-shape", "index": index, "tag": reference.tag, "reference": _class_shape(reference), "actual": _class_shape(actual)})

    reference_records, actual_records = _load_records(reference_json), _load_records(actual_json)
    if reference_records or actual_records:
        checks += max(len(reference_records), len(actual_records))
        actual_by_selector = {str(item.get("selector")): item for item in actual_records if item.get("selector")}
        for index, expected in enumerate(reference_records):
            selector = str(expected.get("selector", ""))
            received = actual_by_selector.get(selector) or (actual_records[index] if index < len(actual_records) else None)
            if received is None:
                failures.append({"kind": "missing-computed-element", "selector": selector})
                continue
            expected_style = expected.get("computed", expected.get("styles", {}))
            actual_style = received.get("computed", received.get("styles", {}))
            if not isinstance(expected_style, dict) or not isinstance(actual_style, dict):
                continue
            for key in sorted(set(expected_style) | set(actual_style)):
                if not _same_value(expected_style.get(key), actual_style.get(key), key):
                    failures.append({"kind": "computed-style", "selector": selector, "property": key, "reference": expected_style.get(key), "actual": actual_style.get(key)})
        expected_selectors = {str(item.get("selector")) for item in reference_records if item.get("selector")}
        for extra in actual_records:
            selector = str(extra.get("selector", ""))
            if selector and selector not in expected_selectors:
                failures.append({"kind": "extra-computed-element", "selector": selector})

    return {"passed": not failures, "checks": checks, "failures": failures, "referenceElements": len(reference_nodes), "actualElements": len(actual_nodes)}


def _pairs(args: argparse.Namespace) -> list[tuple[Path, Path, Path | None, Path | None, str]]:
    if args.reference and args.actual:
        ref, actual = Path(args.reference), Path(args.actual)
        return [(ref, actual, Path(args.reference_json) if args.reference_json else ref.with_suffix(".json"), Path(args.actual_json) if args.actual_json else actual.with_suffix(".json"), ref.stem)]
    if not args.reference_dir or not args.actual_dir:
        raise ValueError("provide either --reference/--actual or --reference-dir/--actual-dir")
    ref_root, actual_root = Path(args.reference_dir), Path(args.actual_dir)
    ref_files = {p.relative_to(ref_root).as_posix(): p for p in ref_root.rglob("*.html")}
    actual_files = {p.relative_to(actual_root).as_posix(): p for p in actual_root.rglob("*.html")}
    result = []
    for name in sorted(set(ref_files) | set(actual_files)):
        ref, actual = ref_files.get(name, ref_root / name), actual_files.get(name, actual_root / name)
        result.append((ref, actual, ref.with_suffix(".json"), actual.with_suffix(".json"), name))
    return result


def run(args: argparse.Namespace) -> int:
    paths = resolve_workspace(args.slug, args.root)
    pairs = _pairs(args)
    if not pairs:
        raise ValueError("no matching HTML snapshot pairs found")
    results = []
    for reference, actual, reference_json, actual_json, name in pairs:
        if not reference.exists() or not actual.exists():
            results.append({"name": name, "reference": str(reference), "actual": str(actual),
                            "passed": False, "checks": 0, "failures": [{"kind": "missing-snapshot"}],
                            "referenceElements": 0, "actualElements": 0})
            continue
        result = assert_dom(reference, actual, reference_json, actual_json, args.ignore_class_shape)
        result["name"], result["reference"], result["actual"] = name, str(reference), str(actual)
        results.append(result)
    if not results:
        raise ValueError("no HTML snapshot pairs found")
    passed = all(bool(item["passed"]) for item in results)
    report = {"slug": args.slug, "generatedAt": datetime.now(timezone.utc).isoformat(), "passed": passed, "snapshots": results}
    json_path = paths["reports"] / f"{args.slug}-dom-assertions.json"
    md_path = paths["reports"] / f"{args.slug}-dom-assertions.md"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = [f"# DOM assertions: {args.slug}", "", f"Result: {'PASS' if passed else 'FAIL'}", "", "| Snapshot | Checks | Failures |", "|---|---:|---:|"]
    for item in results:
        lines.append(f"| `{item['name']}` | {item['checks']} | {len(item['failures'])} |")
        for failure in item["failures"][:20]:
            lines.append(f"  - `{failure['kind']}` at index/selector `{failure.get('index', failure.get('selector', '?'))}`")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[dom-assertions] {'PASS' if passed else 'FAIL'}; report: {json_path}")
    return 0 if passed else 1


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--slug", required=True)
    result.add_argument("--reference")
    result.add_argument("--actual")
    result.add_argument("--reference-json")
    result.add_argument("--actual-json")
    result.add_argument("--reference-dir")
    result.add_argument("--actual-dir")
    result.add_argument("--root")
    result.add_argument("--ignore-class-shape", action="store_true")
    return result


if __name__ == "__main__":
    try:
        raise SystemExit(run(parser().parse_args()))
    except Exception as exc:
        print(f"[dom-assertions] error: {exc}", file=sys.stderr)
        raise SystemExit(2)
