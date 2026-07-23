"""Isolated section-worker protocol, with no LLM or WebContainer dependency.

The original ``worker_agent.py`` combined this contract with Claude API calls.
Here a Codex subagent (or a local deterministic callback) supplies the runner;
this module only prepares scoped input, validates output paths, and returns
portable results.
"""

from __future__ import annotations

import inspect
import logging
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union

from .task_contract import TaskContract

logger = logging.getLogger(__name__)

WorkerRunner = Callable[["WorkerConfig"], Union[Dict[str, str], "WorkerResult", Awaitable[Union[Dict[str, str], "WorkerResult"]]]]


@dataclass
class WorkerConfig:
    worker_id: str
    section_name: str
    task_description: str = ""
    design_requirements: str = ""
    section_data: Dict[str, Any] = field(default_factory=dict)
    layout_context: str = ""
    style_context: str = ""
    target_files: List[str] = field(default_factory=list)
    worker_namespace: str = ""
    base_path: str = "sites/<slug>/src/components/sections"
    allowed_extensions: List[str] = field(default_factory=lambda: [".tsx", ".jsx", ".css", ".md"])
    task_contract_prompt: str = ""
    display_name: str = ""
    contract: Optional[TaskContract] = None


@dataclass
class WorkerResult:
    worker_id: str
    section_name: str
    success: bool
    files: Dict[str, str] = field(default_factory=dict)
    summary: str = ""
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    duration_ms: int = 0


class WorkerAgent:
    """Run a supplied section callback while enforcing contract boundaries."""

    def __init__(self, config: WorkerConfig, runner: Optional[WorkerRunner] = None) -> None:
        self.config = config
        self.runner = runner

    async def run(self) -> WorkerResult:
        if self.runner is None:
            return WorkerResult(self.config.worker_id, self.config.section_name, False, error="No worker runner supplied; dispatch this contract to a Codex subagent.")
        try:
            value = self.runner(self.config)
            if inspect.isawaitable(value):
                value = await value
            if isinstance(value, WorkerResult):
                files = value.files
                result = value
            else:
                files = value
                result = WorkerResult(self.config.worker_id, self.config.section_name, True, files=dict(files or {}), summary=f"Generated {len(files or {})} files")
            path_errors = [f"Worker path is outside assigned namespace: {path}" for path in files if not allowed_worker_path(self.config, path)]
            if self.config.contract is not None:
                result.warnings.extend(self.config.contract.acceptance.validate_files(files))
            if path_errors:
                result.success = False
                result.error = "; ".join(path_errors)
                result.warnings.extend(path_errors)
            return result
        except Exception as exc:
            logger.exception("Section worker %s failed", self.config.worker_id)
            return WorkerResult(self.config.worker_id, self.config.section_name, False, error=str(exc))


def allowed_worker_path(config: WorkerConfig, path: str) -> bool:
    if config.contract is not None:
        return config.contract.is_path_allowed(path)
    normalized = path.replace("\\", "/").lstrip("./")
    namespace = config.worker_namespace or config.section_name.lower().replace(" ", "-")
    prefix = f"{config.base_path.rstrip('/')}/{namespace}/"
    return normalized.startswith(prefix.lstrip("/")) and any(normalized.endswith(ext) for ext in config.allowed_extensions)


def validate_worker_paths(config: WorkerConfig, files: Dict[str, str]) -> List[str]:
    errors = [f"Worker path is outside assigned namespace: {path}" for path in files if not allowed_worker_path(config, path)]
    if config.contract is not None:
        errors.extend(config.contract.acceptance.validate_files(files))
    return errors


def write_worker_files(config: WorkerConfig, files: Dict[str, str], project_root: str, *, overwrite: bool = True) -> List[str]:
    """Safely merge validated worker output into a local clone directory."""
    from pathlib import Path
    root = Path(project_root).resolve()
    errors = validate_worker_paths(config, files)
    if errors:
        raise ValueError("; ".join(errors))
    written = []
    for relative, content in files.items():
        target = (root / relative.lstrip("/")).resolve()
        if root not in target.parents and target != root:
            raise ValueError(f"Worker path escapes project root: {relative}")
        if target.exists() and not overwrite:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        written.append(str(target))
    return written
