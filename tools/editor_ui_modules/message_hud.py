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

    # -- public API --------------------------------------------------------

    def info(self, text: str) -> None:
        self._append(Message(MsgLevel.INFO, text))

    def error(self, text: str) -> None:
        self._append(Message(MsgLevel.ERROR, text))

    def clear(self) -> None:
        self._messages.clear()

    # -- drawing -----------------------------------------------------------

    def draw(self, window_width: float, window_height: float) -> None:
        panel_h = 150 if not self._collapsed else 26
        imgui.set_next_window_position(0, window_height - panel_h)
        imgui.set_next_window_size(window_width, panel_h)

        flags = (
            imgui.WINDOW_NO_RESIZE
            | imgui.WINDOW_NO_MOVE
            | imgui.WINDOW_NO_SAVED_SETTINGS
        )

        imgui.begin("Messages##msg_hud", closable=False, flags=flags)

        # Title bar acts as collapse toggle
        if imgui.button("Messages  [toggle]##collapse_btn"):
            self._collapsed = not self._collapsed

        if not self._collapsed:
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

            if self._auto_scroll:
                imgui.set_scroll_here_y(1.0)
            imgui.end_child()

        imgui.end()

    # -- internal ----------------------------------------------------------

    def _append(self, msg: Message) -> None:
        self._messages.append(msg)
        if len(self._messages) > self._max:
            self._messages = self._messages[-self._max:]
