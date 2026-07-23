"""Scoped JSON/source querying for coding agents.

Adapted from ``Perfect-Web-Clone/backend/agent/tools/json_source_tools.py``.
The original functions depended on the backend memory cache; this version uses
ordinary extraction JSON files so Codex subagents can query a clone workspace
without loading a complete document into their prompt.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple, Union

logger = logging.getLogger(__name__)


@dataclass
class ToolResult:
    success: bool
    result: str
    action: Optional[Dict[str, Any]] = None

    def to_content(self) -> str:
        return self.result if self.success else f"Error: {self.result}"


@dataclass
class SourceRecord:
    id: str
    source_url: str
    page_title: str
    data: Dict[str, Any]
    created_at: str
    path: Optional[str] = None


class SourceStore:
    """File-backed source store; no FastAPI or global process cache required."""

    def __init__(self, directory: Union[str, Path]) -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def save(self, data: Dict[str, Any], source_url: str = "", page_title: str = "", source_id: Optional[str] = None) -> SourceRecord:
        source_id = source_id or "extraction"
        path = self.directory / f"{source_id}.json"
        metadata = data.get("metadata", {}) if isinstance(data, dict) else {}
        record = {
            "id": source_id,
            "source_url": source_url or metadata.get("url", ""),
            "page_title": page_title or metadata.get("title", ""),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "data": data,
        }
        path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
        return SourceRecord(record["id"], record["source_url"], record["page_title"], data, record["created_at"], str(path))

    def load(self, source_id: str) -> Optional[SourceRecord]:
        path = self.directory / (source_id if source_id.endswith(".json") else f"{source_id}.json")
        if not path.exists():
            return None
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
            data = record.get("data", record)
            return SourceRecord(record.get("id", path.stem), record.get("source_url", ""), record.get("page_title", ""), data, record.get("created_at", ""), str(path))
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Could not load source %s: %s", path, exc)
            return None

    def list(self, limit: int = 20) -> List[SourceRecord]:
        records = []
        for path in sorted(self.directory.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
            record = self.load(path.stem)
            if record:
                records.append(record)
            if len(records) >= limit:
                break
        return records

    def delete(self, source_id: str) -> bool:
        path = self.directory / f"{source_id}.json"
        if not path.exists():
            return False
        path.unlink()
        return True


def _load_source(source: Union[SourceRecord, Dict[str, Any], str, Path], store: Optional[SourceStore] = None) -> Tuple[Optional[Dict[str, Any]], str, str, str]:
    if isinstance(source, SourceRecord):
        return source.data, source.source_url, source.page_title, source.id
    if isinstance(source, dict):
        return source.get("data", source), source.get("source_url", ""), source.get("page_title", ""), source.get("id", "inline")
    if store is None:
        path = Path(source)
        store = SourceStore(path.parent)
        source = path.stem
    record = store.load(str(source))
    if not record:
        return None, "", "", str(source)
    return record.data, record.source_url, record.page_title, record.id


def _tokens(path: str) -> List[Union[str, int, None]]:
    path = path.strip()
    if path in ("", "$", "."):
        return []
    if path.startswith("$."):
        path = path[2:]
    elif path.startswith("$"):
        path = path[1:]
    result: List[Union[str, int, None]] = []
    for part in path.replace("[", ".").replace("]", "").split("."):
        if not part:
            continue
        if part in ("*", "[*]"):
            result.append(None)
        elif part.isdigit():
            result.append(int(part))
        else:
            result.append(part)
    return result


def json_path_values(data: Any, path: str) -> List[Any]:
    """Resolve basic JSONPath: fields, indexes, and ``[*]`` wildcards."""
    values = [data]
    for token in _tokens(path):
        next_values: List[Any] = []
        for value in values:
            if token is None:
                if isinstance(value, list):
                    next_values.extend(value)
                elif isinstance(value, dict):
                    next_values.extend(value.values())
            elif isinstance(token, int):
                if isinstance(value, list) and 0 <= token < len(value):
                    next_values.append(value[token])
            elif isinstance(value, dict) and token in value:
                next_values.append(value[token])
        values = next_values
    return values


def _format(value: Any, max_length: int = 4000) -> str:
    if isinstance(value, str):
        return json.dumps(value if len(value) <= max_length else value[:max_length] + " …(truncated)", ensure_ascii=False)
    text = json.dumps(value, indent=2, ensure_ascii=False, default=str)
    return text if len(text) <= max_length else text[:max_length] + "\n…(truncated)"


def list_saved_sources(store: SourceStore, limit: int = 20, selected_source_id: Optional[str] = None, **_: Any) -> ToolResult:
    records = [store.load(selected_source_id)] if selected_source_id else store.list(limit)
    records = [record for record in records if record]
    if not records:
        return ToolResult(True, "No saved website sources found.")
    lines = [f"## Saved Website Sources ({len(records)} found)", ""]
    for record in records:
        assert record is not None
        lines.extend([f"### {record.page_title or 'Untitled'}", f"- **ID**: `{record.id}`", f"- **URL**: {record.source_url or 'Unknown URL'}", f"- **Extracted**: {record.created_at[:19]}", f"- **Available data**: {', '.join(record.data.keys())}", ""])
    return ToolResult(True, "\n".join(lines))


def get_source_overview(source: Union[SourceRecord, Dict[str, Any], str, Path], store: Optional[SourceStore] = None, **_: Any) -> ToolResult:
    data, url, title, source_id = _load_source(source, store)
    if data is None:
        return ToolResult(False, f"Source not found: {source_id}")
    lines = [f"## Source Overview: {title or 'Untitled'}", f"- **ID**: `{source_id}`", f"- **URL**: {url or 'Unknown'}", "", "### Available Data Sections"]
    for key, value in data.items():
        kind = f"object ({len(value)} keys)" if isinstance(value, dict) else f"array ({len(value)} items)" if isinstance(value, list) else f"string ({len(value)} chars)" if isinstance(value, str) else type(value).__name__
        lines.append(f"- **$.{key}**: {kind}")
    return ToolResult(True, "\n".join(lines))


def query_source_json(source: Union[SourceRecord, Dict[str, Any], str, Path], jsonpath: str, store: Optional[SourceStore] = None, max_matches: int = 30, **_: Any) -> ToolResult:
    if not jsonpath:
        return ToolResult(False, "jsonpath is required, for example '$.metadata.title'")
    data, url, _, source_id = _load_source(source, store)
    if data is None:
        return ToolResult(False, f"Source not found: {source_id}")
    matches = json_path_values(data, jsonpath)
    if not matches:
        return ToolResult(True, f"No matches found for path: {jsonpath}")
    lines = [f"## Query Result: {jsonpath}", f"Source: {url or source_id}", ""]
    if len(matches) == 1:
        lines.append(_format(matches[0]))
    else:
        lines.append(f"Found {len(matches)} matches:")
        for index, match in enumerate(matches[:max_matches], 1):
            lines.append(f"{index}. {_format(match, 1000)}")
        if len(matches) > max_matches:
            lines.append(f"… and {len(matches) - max_matches} more matches")
    return ToolResult(True, "\n".join(lines))


def get_json_source_tool_definitions() -> List[Dict[str, Any]]:
    """Return agent-tool-shaped metadata without requiring an LLM runtime."""
    return [
        {"name": "list_saved_sources", "description": "List saved extraction JSON sources.", "input_schema": {"type": "object", "properties": {"limit": {"type": "integer"}}}},
        {"name": "get_source_overview", "description": "Show available sections in one extraction.", "input_schema": {"type": "object", "properties": {"source_id": {"type": "string"}}, "required": ["source_id"]}},
        {"name": "query_source_json", "description": "Return a scoped JSONPath result.", "input_schema": {"type": "object", "properties": {"source_id": {"type": "string"}, "jsonpath": {"type": "string"}}, "required": ["source_id", "jsonpath"]}},
    ]
