"""Left-panel UI Hierarchy tab – tree view of XML elements.

Shows the XML element tree with:
* Collapsible nodes
* Conceal (_) button to hide from work area
* Delete (X) button
* Add child (+) button (uses selected tool)
* Indented children (4px per level)
* Container repetitions shown as single entry
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Callable, Dict, Optional, Set

import imgui

from tools.editors.editor_ui.editor_ui_modules.ui_element_defs import ELEMENT_DEF_BY_TAG
from tools.editors.editor_ui.editor_ui_modules.xml_backing import _CONTAINER_TAGS


class UIHierarchy:
    """Renders the XML element tree as an interactive hierarchy."""

    def __init__(self):
        self.selected_xml_elem: Optional[ET.Element] = None
        self.concealed_elements: Set[int] = set()  # id() of concealed ET.Elements
        self._collapsed: Set[int] = set()  # id() of collapsed ET.Elements
        self._initialized_concealed: Set[int] = set()  # track which elems got default conceal

    def is_concealed(self, xml_elem: ET.Element) -> bool:
        """Check if element or any ancestor is concealed."""
        return id(xml_elem) in self.concealed_elements

    def is_concealed_recursive(self, xml_elem: ET.Element, root: ET.Element) -> bool:
        """Check if element or any ancestor is concealed."""
        if id(xml_elem) in self.concealed_elements:
            return True
        # Check parents
        parent = _find_parent(root, xml_elem)
        if parent is not None and parent is not root:
            return self.is_concealed_recursive(parent, root)
        return False

    def initialize_concealment(self, root: Optional[ET.Element]) -> None:
        """Pre-conceal all container elements in the tree.
        
        Call this when a new XML document is loaded so containers
        start hidden without needing the hierarchy tab to be drawn first.
        """
        if root is None:
            return
        ui_node = root.find("ui")
        if ui_node is None:
            return
        self._initialized_concealed.clear()
        self.concealed_elements.clear()
        self._collapsed.clear()
        self._init_conceal_recursive(ui_node)

    def _init_conceal_recursive(self, node: ET.Element) -> None:
        for child in node:
            elem_id = id(child)
            if child.tag in _CONTAINER_TAGS:
                self._initialized_concealed.add(elem_id)
                self.concealed_elements.add(elem_id)
            self._init_conceal_recursive(child)

    def draw(
        self,
        root: Optional[ET.Element],
        on_select: Callable[[Optional[ET.Element]], None],
        on_delete: Callable[[ET.Element], None],
        on_add_child: Callable[[ET.Element], bool],
        selected_tool_name: str = "",
    ) -> None:
        if root is None:
            imgui.text("(no document loaded)")
            return

        ui_node = root.find("ui")
        if ui_node is None:
            imgui.text("(no <ui> node)")
            return

        self._draw_node(ui_node, root, 0, on_select, on_delete, on_add_child, selected_tool_name)

    def _draw_node(
        self,
        node: ET.Element,
        root: ET.Element,
        depth: int,
        on_select: Callable,
        on_delete: Callable,
        on_add_child: Callable,
        selected_tool_name: str,
    ) -> None:
        from tools.editors.editor_ui.editor_ui_modules.xml_backing import _REPEATING_TAGS

        for child in node:
            elem_id = id(child)
            tag = child.tag

            # Auto-conceal containers on first encounter
            if tag in _CONTAINER_TAGS and elem_id not in self._initialized_concealed:
                self._initialized_concealed.add(elem_id)
                self.concealed_elements.add(elem_id)

            name = child.attrib.get("name", "")
            display = name if name else f"<{tag}>"
            is_concealed = elem_id in self.concealed_elements
            is_collapsed = elem_id in self._collapsed
            has_children = len(child) > 0
            is_selected = child is self.selected_xml_elem

            # Indent
            indent = depth * 16
            imgui.indent(indent)

            # Collapse arrow
            if has_children:
                arrow = "v" if not is_collapsed else ">"
                if imgui.small_button(f"{arrow}##{elem_id}_col"):
                    if is_collapsed:
                        self._collapsed.discard(elem_id)
                    else:
                        self._collapsed.add(elem_id)
                imgui.same_line()

            # + button (add child)
            if imgui.small_button(f"+##{elem_id}_add"):
                on_add_child(child)
            imgui.same_line()

            # _ button (conceal/reveal)
            if is_concealed:
                if imgui.small_button(f"o##{elem_id}_vis"):
                    self.concealed_elements.discard(elem_id)
            else:
                if imgui.small_button(f"_##{elem_id}_vis"):
                    self.concealed_elements.add(elem_id)
            imgui.same_line()

            # X button (delete)
            imgui.push_style_color(imgui.COLOR_BUTTON, 0.6, 0.1, 0.1, 1.0)
            if imgui.small_button(f"X##{elem_id}_del"):
                on_delete(child)
                imgui.pop_style_color()
                imgui.unindent(indent)
                return  # element removed, stop iterating
            imgui.pop_style_color()
            imgui.same_line()

            # Selectable label
            if is_concealed:
                imgui.push_style_color(imgui.COLOR_TEXT, 0.5, 0.5, 0.5, 0.6)
            clicked, _ = imgui.selectable(
                f"{display}##{elem_id}_sel",
                is_selected,
                width=0,
            )
            if is_concealed:
                imgui.pop_style_color()
            if clicked:
                self.selected_xml_elem = child
                on_select(child)

            imgui.unindent(indent)

            # Recurse into children if not collapsed
            if has_children and not is_collapsed:
                if tag in _REPEATING_TAGS:
                    # For repeating containers, show children once
                    self._draw_node(
                        child, root, depth + 1,
                        on_select, on_delete, on_add_child, selected_tool_name,
                    )
                else:
                    self._draw_node(
                        child, root, depth + 1,
                        on_select, on_delete, on_add_child, selected_tool_name,
                    )


def _find_parent(root: ET.Element, target: ET.Element) -> Optional[ET.Element]:
    """Find the parent of target in the tree."""
    for parent in root.iter():
        for child in parent:
            if child is target:
                return parent
    return None
