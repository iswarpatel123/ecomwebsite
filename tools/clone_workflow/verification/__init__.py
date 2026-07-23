"""Offline-friendly verification helpers for SolidStart clone workspaces.

The command modules in this package intentionally have no project or package
manifest dependencies. Browser capture requires the Python Playwright package;
image comparison and DOM snapshot checks use only the Python standard library.
"""

from .common import Viewport, resolve_workspace

__all__ = ["Viewport", "resolve_workspace"]
