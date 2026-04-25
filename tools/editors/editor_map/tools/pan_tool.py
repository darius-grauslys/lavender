"""
Base panning tool (spec section 1.1 — Panning Tool).
"""

from __future__ import annotations

from tools.tool import Tool
from keybinds.keybind_manager import KeybindManager


class PanTool(Tool):
    """Base pan tool — moves the workspace viewport."""

    name = "Pan"
    icon_label = "P"

    def __init__(self):
        self._is_active: bool = False

    def on_activate(self, keybind_manager: KeybindManager) -> None:
        """Mark tool as active."""
        super().on_activate(keybind_manager)
        self._is_active = True

    def on_deactivate(self) -> None:
        """Clear active state."""
        self._is_active = False

    def on_workspace_drag(self, dx: float, dy: float) -> None:
        """Pan is handled by the workspace movement system."""
        # Actual panning is delegated to workspace.movement
        pass
