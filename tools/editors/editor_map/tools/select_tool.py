"""
Base selection tool (spec section 1.1 — Selection Tool).

Each mode's select tool inherits from this and defines
what constitutes a valid selection.
"""

from __future__ import annotations

from typing import Any, List, Optional

from tools.tool import Tool
from keybinds.keybind_manager import KeybindManager


class SelectTool(Tool):
    """Base selection tool with multi-select and copy/paste."""

    name = "Select"
    icon_label = "S"

    def __init__(self):
        self._selection: List[Any] = []
        self._clipboard: Optional[Any] = None
        self._is_active: bool = False

    def on_activate(self, keybind_manager: KeybindManager) -> None:
        """Mark tool as active."""
        super().on_activate(keybind_manager)
        self._is_active = True

    def on_deactivate(self) -> None:
        """Clear active state so selection overrides don't persist."""
        self._is_active = False

    @property
    def selection(self) -> List[Any]:
        return self._selection

    def clear_selection(self) -> None:
        self._selection.clear()

    def select(self, obj: Any) -> None:
        """Add an object to the selection."""
        if obj not in self._selection:
            self._selection.append(obj)

    def deselect(self, obj: Any) -> None:
        if obj in self._selection:
            self._selection.remove(obj)

    def copy(self) -> None:
        """Copy the first selected element to clipboard."""
        if self._selection:
            self._clipboard = self._selection[0]

    def paste(self) -> Optional[Any]:
        """Return the clipboard contents for pasting."""
        return self._clipboard
