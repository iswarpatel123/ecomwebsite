"""Compatibility exports for verification scripts.

The canonical path and viewport helpers live one package level up so
extraction, asset, and verification code agree on workspace boundaries.
"""

import sys
from pathlib import Path

# Make the repository root importable so ``tools.clone_workflow.common``
# resolves both under package imports and direct ``python path/to/script.py``
# execution (where the parent package is not on the path automatically).
_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.clone_workflow.common import (  # noqa: F401
    Viewport,
    default_viewports,
    find_root,
    parse_viewport,
    resolve_workspace,
    safe_relative,
    validate_slug,
)

__all__ = [
    "Viewport", "default_viewports", "find_root", "parse_viewport",
    "resolve_workspace", "safe_relative", "validate_slug",
]
