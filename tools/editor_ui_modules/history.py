"""Undo / Redo ring-buffer (128 records)."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Optional

from tools.editor_ui_modules.constants import HISTORY_MAX


@dataclass
class HistoryRecord:
    """One snapshot of the XML element tree (deep-copied)."""
    description: str
    xml_text: str  # serialised XML string


class HistoryManager:
    """Fixed-size ring-buffer undo/redo manager.

    * ``push`` stores a new record and invalidates any pending redos.
    * ``undo`` / ``redo`` move the cursor and return the stored XML text.
    """

    def __init__(self, capacity: int = HISTORY_MAX):
        self._buf: list[Optional[HistoryRecord]] = [None] * capacity
        self._cap = capacity
        # _start  – oldest valid index
        # _cursor – current position (points at the *active* record)
        # _end    – one-past the newest valid index
        self._start = 0
        self._cursor = -1
        self._end = 0
        self._count = 0

    # ------------------------------------------------------------------
    def push(self, description: str, xml_text: str) -> None:
        """Record a new state, invalidating any redo history."""
        idx = (self._cursor + 1) % self._cap if self._cursor >= 0 else 0
        self._buf[idx] = HistoryRecord(description, xml_text)
        self._cursor = idx
        self._end = (idx + 1) % self._cap

        if self._count < self._cap:
            self._count += 1
        else:
            # ring wrapped – advance start
            self._start = (self._start + 1) % self._cap

        # Invalidate anything after cursor (no more redo)
        self._end = (self._cursor + 1) % self._cap

    # ------------------------------------------------------------------
    def can_undo(self) -> bool:
        if self._count == 0:
            return False
        return self._cursor != self._start

    def undo(self) -> Optional[str]:
        if not self.can_undo():
            return None
        self._cursor = (self._cursor - 1) % self._cap
        rec = self._buf[self._cursor]
        return rec.xml_text if rec else None

    # ------------------------------------------------------------------
    def can_redo(self) -> bool:
        if self._count == 0:
            return False
        next_idx = (self._cursor + 1) % self._cap
        return next_idx != self._end

    def redo(self) -> Optional[str]:
        if not self.can_redo():
            return None
        self._cursor = (self._cursor + 1) % self._cap
        rec = self._buf[self._cursor]
        return rec.xml_text if rec else None
