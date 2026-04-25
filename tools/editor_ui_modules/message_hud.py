"""Bottom collapsible message HUD (INFO / ERROR)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List

import imgui


class MsgLevel(Enum):
    INFO = auto()
    ERROR = auto()


@dataclass
class Message:
    level: MsgLevel
    text: str


class MessageHUD:
    """Collapsible bottom panel that shows INFO and ERROR messages."""

    def __init__(self, max_messages: int = 512):
        self._messages: List[Message] = []
        self._max = max_messages
        self._collapsed: bool = False
        self._auto_scroll: bool = True
        self._new_message_added: bool = False
        self._expanded_height: float = 150.0

    # -- public API --------------------------------------------------------

    def info(self, text: str) -> None:
        self._append(Message(MsgLevel.INFO, text))

    def error(self, text: str) -> None:
        self._append(Message(MsgLevel.ERROR, text))
        self._collapsed = False

    def clear(self) -> None:
        self._messages.clear()

    # -- drawing -----------------------------------------------------------

    @property
    def panel_height(self) -> float:
        """Return the current height of the message panel."""
        return self._expanded_height if not self._collapsed else 26.0

    def draw(self, window_width: float, window_height: float) -> None:
        panel_h = self.panel_height
        # Always anchored to the very bottom of the window
        imgui.set_next_window_position(0, window_height - panel_h)
        imgui.set_next_window_size(window_width, panel_h)

        flags = (
            imgui.WINDOW_NO_MOVE
            | imgui.WINDOW_NO_SAVED_SETTINGS
            | imgui.WINDOW_NO_TITLE_BAR
        )
        if self._collapsed:
            flags |= imgui.WINDOW_NO_RESIZE

        imgui.begin("Messages##msg_hud", closable=False, flags=flags)

        # Detect user resize when expanded
        if not self._collapsed:
            new_h = imgui.get_window_height()
            if abs(new_h - self._expanded_height) > 1:
                self._expanded_height = max(60, min(window_height * 0.8, new_h))

        if self._collapsed:
            # Only show the toggle bar at the very bottom
            if imgui.button("Messages  [expand]##collapse_btn", width=window_width - 16):
                self._collapsed = False
        else:
            if imgui.button("Messages  [collapse]##collapse_btn", width=window_width - 16):
                self._collapsed = True
            imgui.separator()
            imgui.begin_child(
                "##msg_scroll",
                width=0,
                height=0,
                border=True,
            )
            for msg in self._messages:
                if msg.level == MsgLevel.ERROR:
                    imgui.push_style_color(
                        imgui.COLOR_CHILD_BACKGROUND, 0.4, 0.0, 0.0, 1.0
                    )
                    imgui.text_colored(msg.text, 1.0, 1.0, 1.0)
                    imgui.pop_style_color()
                else:
                    imgui.text(msg.text)

            # Only auto-scroll when a new message was added AND user is near bottom
            scroll_y = imgui.get_scroll_y()
            scroll_max = imgui.get_scroll_max_y()
            at_bottom = (scroll_max <= 0) or (scroll_y >= scroll_max - 20)
            if self._new_message_added and at_bottom:
                imgui.set_scroll_here_y(1.0)
            self._new_message_added = False
            imgui.end_child()

        imgui.end()

    # -- internal ----------------------------------------------------------

    def _append(self, msg: Message) -> None:
        self._messages.append(msg)
        self._new_message_added = True
        if len(self._messages) > self._max:
            self._messages = self._messages[-self._max:]
