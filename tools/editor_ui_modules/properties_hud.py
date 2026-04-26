"""Bottom-right Properties HUD – edits attributes of the selected element."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Callable, Dict, List, Optional, Tuple

import imgui

from tools.editors.editor_ui.editor_ui_modules.ui_element_defs import ELEMENT_DEF_BY_TAG, UIElementDef

# Keys whose values must be integers
_NUMERIC_KEYS = frozenset({
    "x", "y", "width", "height", "size",
    "stride__x", "stride__y",
    "__width", "__height",
    "spanning_width", "spanning_height", "spanning_depth",
    "offset_window__x", "offset_window__y", "offset_window__z",
    "layer",
    "span_1x1_index",
})

# Keys whose values must be "true" or "false"
_BOOL_KEYS = frozenset({
    "is_toggleable", "is_toggled",
    "snapped_x_or__y",
})


def _find_parent_of(root: ET.Element, target: ET.Element) -> Optional[ET.Element]:
    """Find the direct parent of *target* in the tree."""
    for parent in root.iter():
        for child in parent:
            if child is target:
                return parent
    return None


def _validate_value(key: str, value: str) -> Tuple[str, Optional[str]]:
    """Validate and coerce a property value.

    Returns (coerced_value, error_message_or_None).
    """
    if key in _NUMERIC_KEYS:
        stripped = value.strip()
        if stripped == "" or stripped == "-":
            return "0", None
        try:
            int(stripped)
            return stripped, None
        except ValueError:
            return "0", f"Property '{key}' must be numeric, got '{value}'. Reset to 0."
    if key in _BOOL_KEYS:
        lower = value.strip().lower()
        if lower in ("true", "false"):
            return lower, None
        return "false", f"Property '{key}' must be true/false, got '{value}'. Reset to false."
    return value, None


class PropertiesHUD:
    """Draws an attribute editor for the currently selected XML element."""

    def __init__(self):
        self.selected_element: Optional[ET.Element] = None
        self._buf: Dict[str, str] = {}  # per-key input buffers
        self.on_view_parent: Optional[Callable[[ET.Element], None]] = None
        self.xml_root: Optional[ET.Element] = None
        self.on_error: Optional[Callable[[str], None]] = None  # error reporter

    def select(self, elem) -> None:
        if elem is not None and hasattr(elem, "xml_elem"):
            elem = elem.xml_elem
        self.selected_element = elem
        self._buf.clear()
        if elem is not None:
            for k, v in elem.attrib.items():
                self._buf[k] = v
            # Pre-populate code text buffer
            if elem.tag == "code" and elem.text:
                self._buf["__code_text__"] = elem.text

    def _report_error(self, msg: str) -> None:
        if self.on_error:
            self.on_error(msg)

    def _draw_field(self, key: str, elem: ET.Element, suffix: str = "prop") -> bool:
        """Draw a single property field. Returns True if the XML was changed."""
        current = self._buf.get(key, elem.attrib.get(key, ""))
        imgui.text(key)
        imgui.same_line(120)

        # Choose input type based on key
        if key in _NUMERIC_KEYS:
            # Allow typing minus and digits; validate on deactivation
            c, new_val = imgui.input_text(
                f"##{key}_{suffix}",
                current,
                256,
                imgui.INPUT_TEXT_CHARS_DECIMAL
                | imgui.INPUT_TEXT_CHARS_NO_BLANK,
            )
        elif key in _BOOL_KEYS:
            # Checkbox for booleans
            bool_val = current.strip().lower() == "true"
            cb_changed, new_bool = imgui.checkbox(f"##{key}_{suffix}", bool_val)
            if cb_changed:
                new_str = "true" if new_bool else "false"
                self._buf[key] = new_str
                elem.set(key, new_str)
                return True
            return False
        else:
            c, new_val = imgui.input_text(
                f"##{key}_{suffix}",
                current,
                256,
            )

        if c:
            # Always update the buffer so imgui sees the latest text
            self._buf[key] = new_val
            if new_val != current:
                # Validate on change
                coerced, err = _validate_value(key, new_val)
                if err:
                    self._report_error(err)
                    self._buf[key] = coerced
                    elem.set(key, coerced)
                else:
                    elem.set(key, new_val)
                return True
        return False

    def draw(
        self,
        window_width: float,
        window_height: float,
        panel_width: float = 220,
        on_change: Optional[Callable[[], None]] = None,
    ) -> None:
        """Draw properties contents (no window creation – expects to be in a child)."""
        imgui.text("Properties")
        imgui.separator()

        elem = self.selected_element
        if elem is None:
            imgui.text("(no selection)")
            return

        imgui.text(f"<{elem.tag}>")
        if self.xml_root is not None and self.on_view_parent is not None:
            imgui.same_line()
            if imgui.small_button("View Parent##vp"):
                parent = _find_parent_of(self.xml_root, elem)
                if parent is not None:
                    self.on_view_parent(parent)
        imgui.separator()

        edef = ELEMENT_DEF_BY_TAG.get(elem.tag)
        keys = edef.property_keys if edef else list(elem.attrib.keys())

        changed = False
        for key in keys:
            if self._draw_field(key, elem, "prop"):
                changed = True

        # Show any extra attribs not in the schema
        for key in elem.attrib:
            if key not in keys:
                if self._draw_field(key, elem, "extra"):
                    changed = True

        # Code element: multiline text editor for inner text
        if elem.tag == "code":
            imgui.separator()
            imgui.text("Code:")
            code_text = self._buf.get("__code_text__", elem.text or "")
            c, new_code = imgui.input_text_multiline(
                "##code_editor",
                code_text,
                4096,
                width=-1,
                height=150,
            )
            if c:
                self._buf["__code_text__"] = new_code
                if new_code != (elem.text or ""):
                    elem.text = new_code
                    changed = True

        if changed and on_change:
            on_change()
