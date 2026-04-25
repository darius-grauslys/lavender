"""
Message HUD for the editor_map.

Displays system, info, warning, and error messages in a
collapsible panel anchored to the bottom of the editor window.

Messages wrap to the width of the Message HUD panel.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List

import imgui


class MessageLevel(Enum):
    SYSTEM = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()


# Colors per message level (R, G, B, A)
_LEVEL_COLORS = {
    MessageLevel.SYSTEM: (0.7, 0.7, 1.0, 1.0),
    MessageLevel.INFO: (0.8, 0.8, 0.8, 1.0),
    MessageLevel.WARNING: (1.0, 0.8, 0.2, 1.0),
    MessageLevel.ERROR: (1.0, 0.3, 0.3, 1.0),
}

_LEVEL_PREFIXES = {
    MessageLevel.SYSTEM: "[SYS] ",
    MessageLevel.INFO: "[INFO] ",
    MessageLevel.WARNING: "[WARN] ",
    MessageLevel.ERROR: "[ERR] ",
}


@dataclass
class _Message:
    level: MessageLevel
    text: str
    timestamp: float = field(default_factory=time.time)


class MessageHUD:
    """
    Message HUD panel for the editor.

    Anchored to the bottom of the window. Collapsible.
    Messages wrap to the panel width.
    ERROR and SYSTEM messages auto-uncollapse the panel.
    """

    def __init__(self, max_messages: int = 200):
        self._messages: List[_Message] = []
        self._max_messages = max_messages
        self._collapsed: bool = False
        self._panel_height: float = 150.0
        self._auto_scroll: bool = True

    @property
    def panel_height(self) -> float:
        """Height consumed by the message HUD."""
        if self._collapsed:
            return 26.0  # Just the title bar
        return self._panel_height

    def _add(self, level: MessageLevel, text: str) -> None:
        self._messages.append(_Message(level=level, text=text))
        if len(self._messages) > self._max_messages:
            self._messages = self._messages[-self._max_messages:]
        self._auto_scroll = True
        # Auto-uncollapse on ERROR or SYSTEM
        if level in (MessageLevel.ERROR, MessageLevel.SYSTEM):
            self._collapsed = False

    def system(self, text: str) -> None:
        self._add(MessageLevel.SYSTEM, text)

    def info(self, text: str) -> None:
        self._add(MessageLevel.INFO, text)

    def warning(self, text: str) -> None:
        self._add(MessageLevel.WARNING, text)

    def error(self, text: str) -> None:
        self._add(MessageLevel.ERROR, text)

    def draw(self, window_width: float, window_height: float) -> None:
        """Draw the message HUD panel."""
        h = self.panel_height
        imgui.set_next_window_position(0, window_height - h)
        imgui.set_next_window_size(window_width, h)

        flags = (
            imgui.WINDOW_NO_MOVE
            | imgui.WINDOW_NO_SAVED_SETTINGS
        )

        expanded, _ = imgui.begin("Messages##msg_hud", flags=flags)

        # Collapse toggle via title bar
        if imgui.is_item_hovered() and imgui.is_mouse_clicked(0):
            pass  # imgui handles collapse via the window

        if not self._collapsed and expanded:
            # Allow vertical resize by dragging top edge
            self._panel_height = max(
                60.0, imgui.get_window_height())

            # Determine available width for text wrapping
            wrap_width = imgui.get_content_region_available_width()
            if wrap_width < 50.0:
                wrap_width = 50.0

            imgui.begin_child(
                "##msg_scroll", 0, 0, border=False)

            for msg in self._messages:
                color = _LEVEL_COLORS.get(
                    msg.level, (0.8, 0.8, 0.8, 1.0))
                prefix = _LEVEL_PREFIXES.get(msg.level, "")
                full_text = prefix + msg.text

                imgui.push_text_wrap_pos(
                    imgui.get_cursor_pos_x() + wrap_width)
                imgui.text_colored(full_text, *color)
                imgui.pop_text_wrap_pos()

            if self._auto_scroll:
                imgui.set_scroll_here_y(1.0)
                self._auto_scroll = False

            imgui.end_child()

        imgui.end()
