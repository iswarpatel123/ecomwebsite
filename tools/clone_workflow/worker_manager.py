"""Parallel, callback-driven section worker manager.

This is the useful orchestration portion of Perfect-Web-Clone's
``worker_manager.py`` without WebSocket events, Claude runtime, or frontend
state.  A Codex harness can pass a callback that invokes a subagent or simply
runs a local generator.
"""

from __future__ import annotations

import asyncio
import inspect
import time
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union

from .worker_agent import WorkerAgent, WorkerConfig, WorkerResult, WorkerRunner


@dataclass
class SectionTask:
    section_name: str
    task_description: str = ""
    design_requirements: str = ""
    section_data: Dict[str, Any] = field(default_factory=dict)
    target_files: List[str] = field(default_factory=list)
    layout_context: str = ""
    style_context: str = ""
    worker_namespace: str = ""
    base_path: str = "sites/<slug>/src/components/sections"
    task_contract_prompt: str = ""
    display_name: str = ""
    contract: Any = None


@dataclass
class WorkerManagerConfig:
    max_concurrent: int = 0
    worker_timeout: float = 1200.0
    continue_on_failure: bool = True


@dataclass
class WorkerManagerResult:
    success: bool
    total_workers: int
    successful_workers: int
    failed_workers: int
    files: Dict[str, str] = field(default_factory=dict)
    worker_results: List[WorkerResult] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    total_duration_ms: int = 0


ProgressCallback = Callable[[str, str], Union[None, Awaitable[None]]]


class WorkerManager:
    def __init__(self, config: Optional[WorkerManagerConfig] = None, on_progress: Optional[ProgressCallback] = None) -> None:
        self.config = config or WorkerManagerConfig()
        self.on_progress = on_progress
        limit = self.config.max_concurrent if self.config.max_concurrent > 0 else 10_000
        self._semaphore = asyncio.Semaphore(limit)

    async def run_workers(self, tasks: List[SectionTask], runner: Optional[WorkerRunner] = None, shared_context: Optional[Dict[str, Any]] = None) -> WorkerManagerResult:
        started = time.monotonic()
        shared_context = shared_context or {}
        if not tasks:
            return WorkerManagerResult(True, 0, 0, 0)

        async def run_one(index: int, task: SectionTask) -> WorkerResult:
            async with self._semaphore:
                if self.on_progress:
                    await _maybe_await(self.on_progress(task.section_name, "started"))
                config = WorkerConfig(
                    worker_id=f"worker_{index}_{task.section_name}", section_name=task.section_name,
                    task_description=task.task_description, design_requirements=task.design_requirements,
                    section_data=task.section_data, target_files=task.target_files,
                    layout_context=task.layout_context or shared_context.get("layout_context", ""),
                    style_context=task.style_context or shared_context.get("style_context", ""),
                    worker_namespace=task.worker_namespace, base_path=task.base_path,
                    task_contract_prompt=task.task_contract_prompt, display_name=task.display_name or task.section_name,
                    contract=task.contract,
                )
                try:
                    result = await asyncio.wait_for(WorkerAgent(config, runner).run(), timeout=self.config.worker_timeout)
                except asyncio.TimeoutError:
                    result = WorkerResult(config.worker_id, config.section_name, False, error=f"Worker timed out after {self.config.worker_timeout}s")
                if self.on_progress:
                    await _maybe_await(self.on_progress(task.section_name, "completed" if result.success else "failed"))
                return result

        results = await asyncio.gather(*(run_one(index, task) for index, task in enumerate(tasks)), return_exceptions=True)
        processed: List[WorkerResult] = []
        for index, result in enumerate(results):
            if isinstance(result, Exception):
                processed.append(WorkerResult(f"worker_{index}_{tasks[index].section_name}", tasks[index].section_name, False, error=str(result)))
            else:
                processed.append(result)

        files: Dict[str, str] = {}
        errors: List[str] = []
        for result in processed:
            if result.success:
                files.update(result.files)
            elif result.error:
                errors.append(f"[{result.section_name}] {result.error}")
        failed = len(processed) - sum(result.success for result in processed)
        return WorkerManagerResult(
            # continue_on_failure controls whether sibling workers are
            # allowed to finish; it must not turn a failed batch into a pass.
            success=failed == 0,
            total_workers=len(processed), successful_workers=len(processed) - failed,
            failed_workers=failed, files=files, worker_results=processed, errors=errors,
            total_duration_ms=int((time.monotonic() - started) * 1000),
        )


async def _maybe_await(value: Any) -> Any:
    return await value if inspect.isawaitable(value) else value


async def run_section_workers(tasks: List[SectionTask], runner: Optional[WorkerRunner] = None, *, max_concurrent: int = 0, worker_timeout: float = 1200.0, on_progress: Optional[ProgressCallback] = None, shared_context: Optional[Dict[str, Any]] = None) -> WorkerManagerResult:
    manager = WorkerManager(WorkerManagerConfig(max_concurrent=max_concurrent, worker_timeout=worker_timeout), on_progress)
    return await manager.run_workers(tasks, runner=runner, shared_context=shared_context)
