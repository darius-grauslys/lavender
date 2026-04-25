"""
Base class for all editor tools.

Tools handle workspace interaction (click, drag, etc.)
and can override keybinds when active.

When implementing a new Tool subclass, you MUST also create
corresponding unit tests in:
    tools/editors/editor_map/tests/tools/test_<tool_module>.py

Tests should cover at minimum:
- Construction (with and without optional dependencies like movement)
- ``_build_keybinds()`` returns the expected KeyCombo→callback mapping
- ``on_activate()`` pushes overrides onto the keybind manager
- ``on_deactivate()`` pops overrides from the keybind manager
- Any tool-specific behaviour (selection, drawing, prompts, etc.)

See existing tests under ``tests/tools/`` for reference patterns.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from keybinds.keybind_manager import KeybindManager


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

    def on_workspace_drag_begin(
            self, world_x: float, world_y: float, world_z: int) -> None:
        """Handle the start of a click-and-drag on the workspace."""
        pass

    def on_workspace_drag_update(
            self, world_x: float, world_y: float, world_z: int) -> None:
        """Handle continued dragging on the workspace."""
        pass

    def on_workspace_drag_end(
            self, world_x: float, world_y: float, world_z: int) -> None:
        """Handle the end of a click-and-drag on the workspace."""
        pass

    def draw_properties(self) -> None:
        """Draw tool-specific properties in the Tool Properties panel."""
        pass

    def draw_overlay(
            self,
            workspace,
            draw_list=None,
            movement=None,
            window_pos=None,
            window_size=None) -> None:
        """Draw tool-specific overlays on the workspace.

        Args:
            workspace: The workspace object (may be None).
            draw_list: imgui draw list for the workspace window.
            movement: WorkspaceMovement for coordinate conversion.
            window_pos: (x, y) top-left of workspace window.
            window_size: (w, h) of workspace window.
        """
        pass
