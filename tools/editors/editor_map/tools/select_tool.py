"""
Base selection tool (spec section 1.1 — Selection Tool).

Each mode's select tool inherits from this and defines
what constitutes a valid selection.
"""

from __future__ import annotations

from typing import Any, List, Optional

from .tool import Tool


class SelectTool(Tool):
    """Base selection tool with multi-select and copy/paste."""

    name = "Select"
    icon_label = "S"

    def __init__(self):
        self._selection: List[Any] = []
        self._clipboard: Optional[Any] = None

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
