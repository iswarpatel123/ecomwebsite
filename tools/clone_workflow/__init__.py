"""Reusable, runtime-independent Python helpers for the clone workflow.

This package is a focused adaptation of the extraction, asset, source-query,
and section-contract patterns in ``Perfect-Web-Clone/backend``.  It deliberately
does not import that application's FastAPI, WebContainer, MCP, or LLM runtime.
"""

__all__ = [
    "ExtractOptions",
    "PlaywrightExtractor",
    "extract_url",
    "ImageDownloadConfig",
    "ImageDownloader",
    "SourceStore",
    "ToolResult",
    "query_source_json",
    "TaskContract",
    "create_task_contract",
    "generate_contracts",
    "SectionTask",
    "WorkerManager",
    "WorkerResult",
]


def __getattr__(name: str):
    """Lazily expose convenience imports without loading Playwright on import."""
    exports = {
        "ExtractOptions": ("extractor", "ExtractOptions"),
        "PlaywrightExtractor": ("extractor", "PlaywrightExtractor"),
        "extract_url": ("extractor", "extract_url"),
        "ImageDownloadConfig": ("image_downloader", "ImageDownloadConfig"),
        "ImageDownloader": ("image_downloader", "ImageDownloader"),
        "SourceStore": ("json_source_tools", "SourceStore"),
        "ToolResult": ("json_source_tools", "ToolResult"),
        "query_source_json": ("json_source_tools", "query_source_json"),
        "TaskContract": ("task_contract", "TaskContract"),
        "create_task_contract": ("task_contract", "create_task_contract"),
        "generate_contracts": ("task_contract", "generate_contracts"),
        "SectionTask": ("worker_manager", "SectionTask"),
        "WorkerManager": ("worker_manager", "WorkerManager"),
        "WorkerResult": ("worker_agent", "WorkerResult"),
    }
    if name not in exports:
        raise AttributeError(name)
    from importlib import import_module
    module_name, attribute = exports[name]
    value = getattr(import_module(f"{__name__}.{module_name}"), attribute)
    globals()[name] = value
    return value
