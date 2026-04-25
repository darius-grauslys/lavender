"""XML read / write helpers and .xml.tmp management."""

from __future__ import annotations

import os
import shutil
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple
from xml.dom import minidom

from tools.editor_ui_modules.constants import GRID_PX


def _safe_int(value: str, default: int = 0) -> int:
    """Parse an integer from a string, returning default on failure."""
    try:
        return int(value.strip())
    except (ValueError, AttributeError):
        return default


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

# Tags that are logical containers (group, grid, allocate_ui_container, allocate_ui)
_CONTAINER_TAGS = frozenset({"group", "grid", "allocate_ui_container", "allocate_ui"})

# Default size for containers that have no children with dimensions
CONTAINER_DEFAULT_W = 32
CONTAINER_DEFAULT_H = 32


class ResolvedElement:
    """An XML element together with its computed absolute position."""
    __slots__ = ("xml_elem", "abs_x", "abs_y", "width", "height",
                 "is_container_owned", "iteration_index", "is_container")

    def __init__(self, xml_elem: ET.Element, abs_x: int, abs_y: int,
                 width: int, height: int,
                 is_container_owned: bool = False,
                 iteration_index: int = 0,
                 is_container: bool = False):
        self.xml_elem = xml_elem
        self.abs_x = abs_x
        self.abs_y = abs_y
        self.width = width
        self.height = height
        self.is_container_owned = is_container_owned
        self.iteration_index = iteration_index
        self.is_container = is_container


# Tags that repeat their children with stride offsets
_REPEATING_TAGS = frozenset({"grid", "allocate_ui_container"})


def _compute_children_bbox(
    node: ET.Element,
    parent_x: int,
    parent_y: int,
) -> Optional[Tuple[int, int, int, int]]:
    """Compute the bounding box (min_x, min_y, max_x, max_y) of all
    descendant elements that have width/height, accounting for stride
    and repetition.  Returns None if no visual descendants exist."""
    min_x = min_y = 999999
    max_x = max_y = -999999
    found = False

    tag = node.tag
    if tag in _REPEATING_TAGS:
        size = _safe_int(node.attrib.get("size", "1"), 1)
        stride_x = _safe_int(node.attrib.get("stride__x", "0"))
        stride_y = _safe_int(node.attrib.get("stride__y", "0"))
        for i in range(size):
            iter_x = parent_x + stride_x * i
            iter_y = parent_y + stride_y * i
            for child in node:
                bb = _compute_children_bbox_single(child, iter_x, iter_y)
                if bb is not None:
                    found = True
                    min_x = min(min_x, bb[0])
                    min_y = min(min_y, bb[1])
                    max_x = max(max_x, bb[2])
                    max_y = max(max_y, bb[3])
    else:
        node_stride_x = _safe_int(node.attrib.get("stride__x", "0"))
        node_stride_y = _safe_int(node.attrib.get("stride__y", "0"))
        for child_index, child in enumerate(node):
            cx = parent_x + node_stride_x * child_index
            cy = parent_y + node_stride_y * child_index
            bb = _compute_children_bbox_single(child, cx, cy)
            if bb is not None:
                found = True
                min_x = min(min_x, bb[0])
                min_y = min(min_y, bb[1])
                max_x = max(max_x, bb[2])
                max_y = max(max_y, bb[3])

    return (min_x, min_y, max_x, max_y) if found else None


def _compute_children_bbox_single(
    node: ET.Element,
    parent_x: int,
    parent_y: int,
) -> Optional[Tuple[int, int, int, int]]:
    """Recursive bbox computation for a single node."""
    local_x = _safe_int(node.attrib.get("x", "0"))
    local_y = _safe_int(node.attrib.get("y", "0"))
    abs_x = parent_x + local_x
    abs_y = parent_y + local_y

    min_x = min_y = 999999
    max_x = max_y = -999999
    found = False

    # If this node itself has dimensions, include it
    if "width" in node.attrib and "height" in node.attrib:
        w = _safe_int(node.attrib["width"])
        h = _safe_int(node.attrib["height"])
        found = True
        min_x = min(min_x, abs_x)
        min_y = min(min_y, abs_y)
        max_x = max(max_x, abs_x + w)
        max_y = max(max_y, abs_y + h)

    # Recurse into children
    tag = node.tag
    if tag in _REPEATING_TAGS:
        size = _safe_int(node.attrib.get("size", "1"), 1)
        stride_x = _safe_int(node.attrib.get("stride__x", "0"))
        stride_y = _safe_int(node.attrib.get("stride__y", "0"))
        for i in range(size):
            iter_x = abs_x + stride_x * i
            iter_y = abs_y + stride_y * i
            for child in node:
                bb = _compute_children_bbox_single(child, iter_x, iter_y)
                if bb is not None:
                    found = True
                    min_x = min(min_x, bb[0])
                    min_y = min(min_y, bb[1])
                    max_x = max(max_x, bb[2])
                    max_y = max(max_y, bb[3])
    else:
        node_stride_x = _safe_int(node.attrib.get("stride__x", "0"))
        node_stride_y = _safe_int(node.attrib.get("stride__y", "0"))
        for child_index, child in enumerate(node):
            cx = abs_x + node_stride_x * child_index
            cy = abs_y + node_stride_y * child_index
            bb = _compute_children_bbox_single(child, cx, cy)
            if bb is not None:
                found = True
                min_x = min(min_x, bb[0])
                min_y = min(min_y, bb[1])
                max_x = max(max_x, bb[2])
                max_y = max(max_y, bb[3])

    return (min_x, min_y, max_x, max_y) if found else None


def find_ui_elements(root: ET.Element) -> List[ResolvedElement]:
    """Return all visual elements inside ``<ui>`` with absolute positions.

    Walks the tree, accumulating parent ``x``/``y`` offsets.  For repeating
    containers (``grid``, ``allocate_ui_container``) children are expanded
    ``size`` times with the appropriate stride applied per iteration.
    """
    ui_node = root.find("ui")
    if ui_node is None:
        return []
    results: List[ResolvedElement] = []
    _collect_positioned(ui_node, 0, 0, results)
    return results


def _collect_positioned(
    node: ET.Element,
    parent_x: int,
    parent_y: int,
    out: List[ResolvedElement],
    container_owned: bool = False,
) -> None:
    # The parent node may define stride that applies to its children
    parent_stride_x = _safe_int(node.attrib.get("stride__x", "0"))
    parent_stride_y = _safe_int(node.attrib.get("stride__y", "0"))

    for child_index, child in enumerate(node):
        tag = child.tag
        local_x = _safe_int(child.attrib.get("x", "0"))
        local_y = _safe_int(child.attrib.get("y", "0"))
        # Apply parent stride per child index (like group stride__y)
        abs_x = parent_x + local_x + parent_stride_x * child_index
        abs_y = parent_y + local_y + parent_stride_y * child_index

        if tag in _REPEATING_TAGS:
            # Emit a container element with computed bounding box
            bbox = _compute_children_bbox(child, abs_x, abs_y)
            if bbox is not None:
                out.append(ResolvedElement(
                    child, bbox[0], bbox[1],
                    bbox[2] - bbox[0], bbox[3] - bbox[1],
                    is_container_owned=container_owned,
                    is_container=True,
                ))
            else:
                # No children with dimensions; use __width/__height or defaults
                cw = _safe_int(child.attrib.get("__width", str(CONTAINER_DEFAULT_W)), CONTAINER_DEFAULT_W)
                ch = _safe_int(child.attrib.get("__height", str(CONTAINER_DEFAULT_H)), CONTAINER_DEFAULT_H)
                out.append(ResolvedElement(
                    child, abs_x, abs_y, cw, ch,
                    is_container_owned=container_owned,
                    is_container=True,
                ))

            # Repeating container: expand children `size` times with stride
            size = _safe_int(child.attrib.get("size", "1"), 1)
            stride_x = _safe_int(child.attrib.get("stride__x", "0"))
            stride_y = _safe_int(child.attrib.get("stride__y", "0"))
            for i in range(size):
                iter_x = abs_x + stride_x * i
                iter_y = abs_y + stride_y * i
                for grandchild in child:
                    _collect_positioned_single(
                        grandchild, iter_x, iter_y, out,
                        container_owned=True, iteration_index=i,
                    )
        elif tag in _CONTAINER_TAGS:
            # Non-repeating container (e.g. group with stride)
            bbox = _compute_children_bbox(child, abs_x, abs_y)
            if bbox is not None:
                out.append(ResolvedElement(
                    child, bbox[0], bbox[1],
                    bbox[2] - bbox[0], bbox[3] - bbox[1],
                    is_container_owned=container_owned,
                    is_container=True,
                ))
            else:
                cw = _safe_int(child.attrib.get("__width", str(CONTAINER_DEFAULT_W)), CONTAINER_DEFAULT_W)
                ch = _safe_int(child.attrib.get("__height", str(CONTAINER_DEFAULT_H)), CONTAINER_DEFAULT_H)
                out.append(ResolvedElement(
                    child, abs_x, abs_y, cw, ch,
                    is_container_owned=container_owned,
                    is_container=True,
                ))
            _collect_positioned(child, abs_x, abs_y, out, container_owned)
        else:
            # Non-repeating: emit self if visual, then recurse
            if "width" in child.attrib and "height" in child.attrib:
                w = _safe_int(child.attrib["width"])
                h = _safe_int(child.attrib["height"])
                out.append(ResolvedElement(
                    child, abs_x, abs_y, w, h,
                    is_container_owned=container_owned,
                ))

            # Recurse into children
            _collect_positioned(child, abs_x, abs_y, out, container_owned)


def _collect_positioned_single(
    node: ET.Element,
    parent_x: int,
    parent_y: int,
    out: List[ResolvedElement],
    container_owned: bool = False,
    iteration_index: int = 0,
) -> None:
    """Process a single element and recurse — used by repeating expansion."""
    tag = node.tag
    local_x = _safe_int(node.attrib.get("x", "0"))
    local_y = _safe_int(node.attrib.get("y", "0"))
    abs_x = parent_x + local_x
    abs_y = parent_y + local_y

    if tag in _REPEATING_TAGS:
        size = _safe_int(node.attrib.get("size", "1"), 1)
        stride_x = _safe_int(node.attrib.get("stride__x", "0"))
        stride_y = _safe_int(node.attrib.get("stride__y", "0"))
        for i in range(size):
            iter_x = abs_x + stride_x * i
            iter_y = abs_y + stride_y * i
            for child in node:
                _collect_positioned_single(
                    child, iter_x, iter_y, out,
                    container_owned=True, iteration_index=i,
                )
    else:
        if "width" in node.attrib and "height" in node.attrib:
            w = _safe_int(node.attrib["width"])
            h = _safe_int(node.attrib["height"])
            out.append(ResolvedElement(
                node, abs_x, abs_y, w, h,
                is_container_owned=container_owned,
                iteration_index=iteration_index,
            ))

        # Apply this node's stride to its children
        node_stride_x = _safe_int(node.attrib.get("stride__x", "0"))
        node_stride_y = _safe_int(node.attrib.get("stride__y", "0"))
        for child_index, child in enumerate(node):
            child_abs_x = abs_x + node_stride_x * child_index
            child_abs_y = abs_y + node_stride_y * child_index
            _collect_positioned_single(
                child, child_abs_x, child_abs_y, out,
                container_owned=container_owned,
                iteration_index=iteration_index,
            )


def snap_to_grid(value: int, grid: int = GRID_PX) -> int:
    return round(value / grid) * grid


def elem_rect(elem) -> Tuple[int, int, int, int]:
    """Return (x, y, w, h) for an element.

    Accepts either a ``ResolvedElement`` (with absolute coords) or a raw
    ``ET.Element`` (falls back to reading attributes directly).
    """
    if isinstance(elem, ResolvedElement):
        return (elem.abs_x, elem.abs_y, elem.width, elem.height)
    return (
        _safe_int(elem.attrib.get("x", "0")),
        _safe_int(elem.attrib.get("y", "0")),
        _safe_int(elem.attrib.get("width", "0")),
        _safe_int(elem.attrib.get("height", "0")),
    )


def set_elem_rect(
    elem: ET.Element, x: int, y: int, w: int, h: int
) -> None:
    elem.set("x", str(x))
    elem.set("y", str(y))
    elem.set("width", str(w))
    elem.set("height", str(h))


def remove_element(root: ET.Element, target) -> bool:
    """Remove *target* from anywhere in the tree.  Returns True on success.

    *target* may be an ``ET.Element`` or a ``ResolvedElement``.
    """
    xml_target = target
    if hasattr(target, "xml_elem"):
        xml_target = target.xml_elem
    for parent in root.iter():
        for child in list(parent):
            if child is xml_target:
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


def add_element_under(
    parent: ET.Element,
    tag: str,
    attribs: Dict[str, str],
) -> ET.Element:
    """Append a new element under *parent* and return it."""
    return ET.SubElement(parent, tag, attribs)
