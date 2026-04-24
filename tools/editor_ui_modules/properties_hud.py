"""Bottom-right Properties HUD – edits attributes of the selected element."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Callable, Dict, Optional, Tuple

import imgui

from tools.editor_ui_modules.ui_element_defs import ELEMENT_DEF_BY_TAG, UIElementDef


class PropertiesHUD:
    """Draws an attribute editor for the currently selected XML element."""

    def __init__(self):
        self.selected_element: Optional[ET.Element] = None
        self._buf: Dict[str, str] = {}  # per-key input buffers

    def select(self, elem) -> None:
        if elem is not None and hasattr(elem, "xml_elem"):
            elem = elem.xml_elem
        self.selected_element = elem
        self._buf.clear()
        if elem is not None:
            for k, v in elem.attrib.items():
                self._buf[k] = v

    def draw(
        self,
        window_width: float,
        window_height: float,
        panel_width: float = 220,
        on_change: Optional[Callable[[], None]] = None,
    ) -> None:
        half_h = window_height * 0.5
        imgui.set_next_window_position(
            window_width - panel_width, half_h
        )
        imgui.set_next_window_size(panel_width, half_h)

        flags = (
            imgui.WINDOW_NO_RESIZE
            | imgui.WINDOW_NO_MOVE
            | imgui.WINDOW_NO_SAVED_SETTINGS
        )
        imgui.begin("Properties##prop_hud", closable=False, flags=flags)

        elem = self.selected_element
        if elem is None:
            imgui.text("(no selection)")
            imgui.end()
            return

        imgui.text(f"<{elem.tag}>")
        imgui.separator()

        edef = ELEMENT_DEF_BY_TAG.get(elem.tag)
        keys = edef.property_keys if edef else list(elem.attrib.keys())

        changed = False
        for key in keys:
            current = self._buf.get(key, elem.attrib.get(key, ""))
            imgui.text(key)
            imgui.same_line(120)
            c, new_val = imgui.input_text(
                f"##{key}_prop",
                current,
                256,
                imgui.INPUT_TEXT_ENTER_RETURNS_TRUE,
            )
            if c:
                self._buf[key] = new_val
                elem.set(key, new_val)
                changed = True

        # Show any extra attribs not in the schema
        for key in elem.attrib:
            if key not in keys:
                current = self._buf.get(key, elem.attrib.get(key, ""))
                imgui.text(key)
                imgui.same_line(120)
                c, new_val = imgui.input_text(
                    f"##{key}_extra",
                    current,
                    256,
                    imgui.INPUT_TEXT_ENTER_RETURNS_TRUE,
                )
                if c:
                    self._buf[key] = new_val
                    elem.set(key, new_val)
                    changed = True

        if changed and on_change:
            on_change()

        imgui.end()
