"""
Keybind definitions.

A keybind is a (modifier_flags, key) tuple mapped to a callback.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntFlag, auto
from typing import Callable, Optional


class Modifier(IntFlag):
    NONE = 0
    CTRL = auto()
    SHIFT = auto()
    ALT = auto()
    CTRL_SHIFT = CTRL | SHIFT
    ALT_SHIFT = ALT | SHIFT


@dataclass(frozen=True)
class KeyCombo:
    """An immutable key combination."""
    key: int  # imgui key constant or ord('X')
    modifiers: Modifier = Modifier.NONE

    def __hash__(self):
        return hash((self.key, int(self.modifiers)))

    def __eq__(self, other):
        if not isinstance(other, KeyCombo):
            return NotImplemented
        return self.key == other.key and self.modifiers == other.modifiers


# Virtual key constants for scroll and zoom events.
# These are NOT real GLFW key codes — they live above KEY_LAST
# so they never collide with physical keys.
VIRTUAL_KEY_SCROLL_UP: int = 0x10000
VIRTUAL_KEY_SCROLL_DOWN: int = 0x10001
VIRTUAL_KEY_ZOOM_IN: int = 0x10002
VIRTUAL_KEY_ZOOM_OUT: int = 0x10003

# Type alias for keybind callbacks
KeybindCallback = Callable[[], None]
