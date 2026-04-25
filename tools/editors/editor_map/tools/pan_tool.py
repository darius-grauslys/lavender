"""
Base panning tool (spec section 1.1 — Panning Tool).
"""

from __future__ import annotations

from .tool import Tool


class PanTool(Tool):
    """Base pan tool — moves the workspace viewport."""

    name = "Pan"
    icon_label = "P"

    def on_workspace_drag(self, dx: float, dy: float) -> None:
        """Pan is handled by the workspace movement system."""
        # Actual panning is delegated to workspace.movement
        pass
