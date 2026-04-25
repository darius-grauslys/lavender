"""
Tilesheet manager — maintains a collection of loaded tilesheets.

Each tilesheet is identified by its project-relative path.
The manager handles loading, unloading, and GL texture lifecycle.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from core.tilesheet import Tilesheet, load_tilesheet

logger = logging.getLogger(__name__)


@dataclass
class TilesheetEntry:
    """A loaded tilesheet with its metadata."""
    relative_path: str
    tilesheet: Tilesheet
    gl_texture_id: int = 0


class TilesheetManager:
    """Manages multiple loaded tilesheets.

    Provides add/remove/get operations and tracks GL texture IDs
    for each tilesheet.
    """

    def __init__(self) -> None:
        self._entries: Dict[str, TilesheetEntry] = {}
        # Ordered list of relative paths for stable iteration
        self._order: List[str] = []
        self._active_path: str = ""

    @property
    def entries(self) -> List[TilesheetEntry]:
        """Return entries in insertion order."""
        return [self._entries[p] for p in self._order if p in self._entries]

    @property
    def active_entry(self) -> Optional[TilesheetEntry]:
        """Return the currently active tilesheet entry."""
        return self._entries.get(self._active_path)

    @property
    def active_path(self) -> str:
        return self._active_path

    @active_path.setter
    def active_path(self, path: str) -> None:
        self._active_path = path

    @property
    def count(self) -> int:
        return len(self._entries)

    def has(self, relative_path: str) -> bool:
        return relative_path in self._entries

    def get(self, relative_path: str) -> Optional[TilesheetEntry]:
        return self._entries.get(relative_path)

    def add(
            self,
            relative_path: str,
            tilesheet: Tilesheet,
            gl_texture_id: int = 0) -> TilesheetEntry:
        """Add a tilesheet. If it already exists, update it."""
        if relative_path in self._entries:
            entry = self._entries[relative_path]
            entry.tilesheet = tilesheet
            entry.gl_texture_id = gl_texture_id
            return entry
        entry = TilesheetEntry(
            relative_path=relative_path,
            tilesheet=tilesheet,
            gl_texture_id=gl_texture_id)
        self._entries[relative_path] = entry
        self._order.append(relative_path)
        # Auto-select first added as active
        if not self._active_path:
            self._active_path = relative_path
        return entry

    def remove(self, relative_path: str) -> Optional[TilesheetEntry]:
        """Remove a tilesheet by path. Returns the removed entry."""
        entry = self._entries.pop(relative_path, None)
        if entry is not None:
            self._order = [p for p in self._order if p != relative_path]
            if self._active_path == relative_path:
                self._active_path = self._order[0] if self._order else ""
        return entry

    def set_gl_texture(
            self, relative_path: str, gl_texture_id: int) -> None:
        """Update the GL texture ID for a tilesheet."""
        entry = self._entries.get(relative_path)
        if entry:
            entry.gl_texture_id = gl_texture_id

    def load_and_add(
            self,
            project_dir: Path,
            relative_path: str) -> Optional[TilesheetEntry]:
        """Load a tilesheet from disk and add it to the manager.

        Returns the entry on success, None on failure.
        """
        resolved = project_dir / relative_path
        if not resolved.exists():
            logger.error("Tilesheet not found: %s", resolved)
            return None
        tilesheet = load_tilesheet(resolved)
        if tilesheet is None:
            logger.error("Failed to load tilesheet: %s", resolved)
            return None
        return self.add(relative_path, tilesheet)

    def clear(self) -> None:
        """Remove all tilesheets."""
        self._entries.clear()
        self._order.clear()
        self._active_path = ""

    def all_paths(self) -> List[str]:
        """Return all loaded tilesheet paths in order."""
        return list(self._order)

    def sync_from_config(
            self,
            project_dir: Path,
            tilesheet_paths: List[str]) -> None:
        """Sync loaded tilesheets from a list of project-relative paths.

        Loads any paths not already present, removes any that are
        no longer in the list.
        """
        current = set(self._order)
        desired = set(tilesheet_paths)

        # Remove entries no longer in config
        for path in current - desired:
            self.remove(path)

        # Add new entries
        for path in tilesheet_paths:
            if path and not self.has(path):
                self.load_and_add(project_dir, path)

    def to_path_list(self) -> List[str]:
        """Return the list of tilesheet paths for config serialization."""
        return [p for p in self._order if p]
