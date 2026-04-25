"""
Base class for all editor modes.

Each mode has a name, activation shortcut, a list of tools,
and manages keybind overrides via the keybind manager.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from tools.editors.editor_map.keybinds.keybind_manager import KeybindManager
    from tools.editors.editor_map.tools.tool import Tool


class EditorMode:
    """Base class for editor modes (spec section 4.1.1)."""

    name: str = "Unknown"
    shortcut_label: str = ""

    def __init__(self, keybind_manager: KeybindManager):
        self._keybind_manager = keybind_manager
        self._tools: List[Tool] = []
        self._active_tool_index: int = 0

    @property
    def tools(self) -> List[Tool]:
        return self._tools

    @property
    def active_tool(self) -> Optional[Tool]:
        if 0 <= self._active_tool_index < len(self._tools):
            return self._tools[self._active_tool_index]
        return None

    def select_tool(self, index: int) -> None:
        """Select a tool by index, managing keybind overrides."""
        old_tool = self.active_tool
        if old_tool:
            old_tool.on_deactivate(self._keybind_manager)

        self._active_tool_index = max(0, min(index, len(self._tools) - 1))

        new_tool = self.active_tool
        if new_tool:
            new_tool.on_activate(self._keybind_manager)

    def on_activate(self) -> None:
        """Called when this mode becomes the active mode."""
        self._keybind_manager.push_override(self._get_mode_keybinds())
        if self._tools:
            self.select_tool(0)

    def on_deactivate(self) -> None:
        """Called when this mode is deactivated."""
        old_tool = self.active_tool
        if old_tool:
            old_tool.on_deactivate(self._keybind_manager)
        self._keybind_manager.pop_override()

    def _get_mode_keybinds(self) -> dict:
        """Override to provide mode-level keybinds."""
        return {}

    def draw_workspace(self, workspace) -> None:
        """Override to draw mode-specific workspace content."""
        pass

    def draw_tool_properties(self) -> None:
        """Draw the active tool's properties panel."""
        tool = self.active_tool
        if tool:
            tool.draw_properties()
