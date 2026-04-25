"""Pytest configuration — ensure the editor_map package is importable."""

import sys
from pathlib import Path

# Add the repo root so `tools.editors.editor_map.core` resolves,
# and also add the editor_map dir so `core.xxx` resolves directly.
_editor_map_dir = Path(__file__).resolve().parent.parent
_repo_root = _editor_map_dir.parents[2]

for _p in (str(_repo_root), str(_editor_map_dir)):
    if _p not in sys.path:
        sys.path.insert(0, _p)
