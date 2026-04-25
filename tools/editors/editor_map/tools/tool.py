"""
Base class for all editor tools.

Tools handle workspace interaction (click, drag, etc.)
and can override keybinds when active.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools.editors.editor_map.keybinds.keybind_manager import KeybindManager


class Tool:
    """Base class for editor tools (spec section 4.1.2)."""

    name: str = "Unknown Tool"
    icon_label: str = "?"

    def on_activate(self, keybind_manager: KeybindManager) -> None:
        """Called when this tool becomes active. Push keybind overrides."""
        overrides = self._get_tool_keybinds()
        if overrides:
            keybind_manager.push_override(overrides)

    def on_deactivate(self, keybind_manager: KeybindManager) -> None:
        """Called when this tool is deactivated. Pop keybind overrides."""
        if self._get_tool_keybinds():
            keybind_manager.pop_override()

    def _get_tool_keybinds(self) -> dict:
        """Override to provide tool-level keybinds."""
        return {}

    def on_workspace_click(self, world_x: float, world_y: float, world_z: int) -> None:
        """Handle a left-click on the workspace at world coordinates."""
        pass

    def on_workspace_drag(self, dx: float, dy: float) -> None:
        """Handle a drag on the workspace."""
        pass

    def draw_properties(self) -> None:
        """Draw tool-specific properties in the Tool Properties panel."""
        pass

    def draw_overlay(self, workspace) -> None:
        """Draw tool-specific overlays on the workspace."""
        pass
