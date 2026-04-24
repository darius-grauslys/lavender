"""XML read / write helpers and .xml.tmp management."""

from __future__ import annotations

import os
import shutil
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple
from xml.dom import minidom

from tools.editor_ui_modules.constants import GRID_PX


# ---------------------------------------------------------------------------
# Pretty-print helpers
# ---------------------------------------------------------------------------

def _indent_xml(elem: ET.Element, level: int = 0) -> None:
    """In-place indent an ElementTree (for Python < 3.9 compat)."""
    indent = "\n" + "  " * level
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = indent + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = indent
        for child in elem:
            _indent_xml(child, level + 1)
        if not child.tail or not child.tail.strip():
            child.tail = indent
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = indent


def serialize_tree(root: ET.Element) -> str:
    """Return a pretty-printed XML string."""
    _indent_xml(root)
    return ET.tostring(root, encoding="unicode", xml_declaration=True)


# ---------------------------------------------------------------------------
# File management
# ---------------------------------------------------------------------------

def tmp_path_for(xml_path: str) -> str:
    return xml_path + ".tmp"


def load_xml(xml_path: str) -> Optional[ET.Element]:
    """Load XML, preferring .xml.tmp if it exists."""
    tmp = tmp_path_for(xml_path)
    path = tmp if os.path.exists(tmp) else xml_path
    if not os.path.exists(path):
        return None
    try:
        return ET.parse(path).getroot()
    except ET.ParseError:
        return None


def save_tmp(xml_path: str, root: ET.Element) -> None:
    """Write current state to .xml.tmp."""
    tmp = tmp_path_for(xml_path)
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(serialize_tree(root))


def save_final(xml_path: str, root: ET.Element) -> None:
    """Write .xml.tmp content into the real .xml file."""
    with open(xml_path, "w", encoding="utf-8") as fh:
        fh.write(serialize_tree(root))
    # Also update .tmp so they stay in sync
    save_tmp(xml_path, root)


# ---------------------------------------------------------------------------
# Element helpers
# ---------------------------------------------------------------------------

def find_ui_elements(root: ET.Element) -> List[ET.Element]:
    """Return all elements inside <ui> that have x/y/width/height."""
    ui_node = root.find("ui")
    if ui_node is None:
        return []
    results: List[ET.Element] = []
    _collect_positioned(ui_node, results)
    return results


def _collect_positioned(node: ET.Element, out: List[ET.Element]) -> None:
    for child in node:
        if "width" in child.attrib and "height" in child.attrib:
            out.append(child)
        _collect_positioned(child, out)


def snap_to_grid(value: int, grid: int = GRID_PX) -> int:
    return round(value / grid) * grid


def elem_rect(elem: ET.Element) -> Tuple[int, int, int, int]:
    """Return (x, y, w, h) for an element, defaulting to 0."""
    return (
        int(elem.attrib.get("x", "0")),
        int(elem.attrib.get("y", "0")),
        int(elem.attrib.get("width", "0")),
        int(elem.attrib.get("height", "0")),
    )


def set_elem_rect(
    elem: ET.Element, x: int, y: int, w: int, h: int
) -> None:
    elem.set("x", str(x))
    elem.set("y", str(y))
    elem.set("width", str(w))
    elem.set("height", str(h))


def remove_element(root: ET.Element, target: ET.Element) -> bool:
    """Remove *target* from anywhere in the tree.  Returns True on success."""
    for parent in root.iter():
        for child in list(parent):
            if child is target:
                parent.remove(child)
                return True
    return False


def add_element_to_ui(
    root: ET.Element,
    tag: str,
    attribs: Dict[str, str],
) -> Optional[ET.Element]:
    """Append a new element under <ui> and return it."""
    ui_node = root.find("ui")
    if ui_node is None:
        return None
    elem = ET.SubElement(ui_node, tag, attribs)
    return elem
