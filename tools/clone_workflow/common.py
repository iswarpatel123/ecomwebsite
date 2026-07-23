"""Shared, dependency-free helpers for clone-workflow modules.

The helpers deliberately keep all durable artifacts inside ``.cloning/<slug>``
and validate user supplied slugs before constructing paths.  Verification
modules re-export these definitions for backwards-compatible imports.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


@dataclass(frozen=True)
class Viewport:
    """A named browser viewport used by extraction and verification."""

    name: str
    width: int
    height: int


def parse_viewport(value: str, name: str | None = None) -> Viewport:
    """Parse ``desktop=1440x900`` or ``1440x900``."""
    raw = value.strip()
    if "=" in raw:
        supplied_name, raw = raw.split("=", 1)
        name = name or supplied_name.strip()
    match = re.fullmatch(r"(\d{2,5})x(\d{2,5})", raw.lower())
    if not match:
        raise ValueError(f"Invalid viewport {value!r}; expected WIDTHxHEIGHT")
    width, height = (int(part) for part in match.groups())
    if not (1 <= width <= 10000 and 1 <= height <= 10000):
        raise ValueError(f"Viewport is outside supported range: {value!r}")
    return Viewport(name or f"{width}x{height}", width, height)


def default_viewports() -> list[Viewport]:
    return [
        Viewport("desktop", 1440, 900),
        Viewport("tablet", 768, 1024),
        Viewport("mobile", 390, 844),
    ]


def validate_slug(slug: str) -> str:
    """Validate a slug before it is used in a filesystem path."""
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", slug):
        raise ValueError("slug must contain only letters, numbers, '_' or '-'")
    return slug


def find_root(explicit: str | None = None) -> Path:
    """Find the repository root from an optional path or workspace marker."""
    if explicit:
        return Path(explicit).expanduser().resolve()
    current = Path.cwd().resolve()
    for candidate in (current, *current.parents):
        if (candidate / "pnpm-workspace.yaml").exists():
            return candidate
    return current


def resolve_workspace(slug: str, root: str | None = None, create: bool = True) -> dict[str, Path]:
    """Return canonical clone artifact paths, safely scoped to one slug."""
    validate_slug(slug)
    base = find_root(root)
    cloning_dir = (base / ".cloning").resolve()
    slug_dir = (cloning_dir / slug).resolve()
    if slug_dir.parent != cloning_dir:
        raise ValueError("slug resolves outside the .cloning directory")
    paths = {
        "root": base,
        "slug": slug_dir,
        "source": slug_dir / "source",
        "reference": slug_dir / "reference",
        "assets": slug_dir / "assets",
        "contracts": slug_dir / "contracts",
        "reports": slug_dir / "reports",
        "site": base / "sites" / slug,
    }
    if create:
        for key in ("source", "reference", "assets", "contracts", "reports"):
            paths[key].mkdir(parents=True, exist_ok=True)
    return paths


def safe_relative(path: Path, root: Path) -> str:
    """Return a stable relative path without allowing traversal."""
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.name


__all__ = [
    "Viewport", "parse_viewport", "default_viewports", "validate_slug",
    "find_root", "resolve_workspace", "safe_relative",
]
