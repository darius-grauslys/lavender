"""Central interactive work area – grid canvas with element rendering.

Handles:
* 8×8 grid rendering
* Element rectangle rendering with outlines
* Click-to-select, CTRL-F reveal-all, delete via X button
* Click / drag-to-create new elements from the active tool
* Snapping to grid
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Callable, Dict, List, Optional, Tuple

import imgui

from tools.editor_ui_modules.constants import (
    COLOR_DELETE_X,
    COLOR_OUTLINE_FOCUSED,
    COLOR_OUTLINE_REVEAL,
    COLOR_OUTLINE_SELECTED,
    GRID_PX,
    OUTLINE_WIDTH,
)
from tools.editor_ui_modules.span_renderer import build_span_tile_grid
from tools.editor_ui_modules.ui_element_defs import ELEMENT_DEF_BY_TAG, UIElementDef
from tools.editor_ui_modules.xml_backing import (
    add_element_to_ui,
    elem_rect,
    remove_element,
    set_elem_rect,
    snap_to_grid,
)


def _color4_to_u32(r: float, g: float, b: float, a: float) -> int:
    """Convert RGBA floats [0..1] to a packed ImU32 (ABGR)."""
    ri = int(max(0, min(255, r * 255)))
    gi = int(max(0, min(255, g * 255)))
    bi = int(max(0, min(255, b * 255)))
    ai = int(max(0, min(255, a * 255)))
    return (ai << 24) | (bi << 16) | (gi << 8) | ri


def _parse_color_attrib(elem: ET.Element) -> Tuple[float, float, float]:
    raw = elem.attrib.get("color", "55,55,55")
    parts = raw.split(",")
    try:
        return (
            int(parts[0]) / 255.0,
            int(parts[1]) / 255.0,
            int(parts[2]) / 255.0,
        )
    except (ValueError, IndexError):
        return (0.22, 0.22, 0.22)


class WorkArea:
    """Manages the interactive canvas region."""

    def __init__(self):
        self.selected_element: Optional[ET.Element] = None
        self.hovered_element: Optional[ET.Element] = None
        self._drag_start: Optional[Tuple[int, int]] = None
        self._is_dragging: bool = False
        self._scroll_x: float = 0.0
        self._scroll_y: float = 0.0
        # PNG preview
        self._preview_texture_id: Optional[int] = None
        self._preview_path: Optional[str] = None

    # ------------------------------------------------------------------
    # Main draw
    # ------------------------------------------------------------------

    def draw(
        self,
        elements: List[ET.Element],
        root: Optional[ET.Element],
        active_tool: Optional[UIElementDef],
        span_configs: dict,
        work_w: int,
        work_h: int,
        origin_x: float,
        origin_y: float,
        on_select: Callable[[Optional[ET.Element]], None],
        on_delete: Callable[[ET.Element], None],
        on_create: Callable[[str, Dict[str, str]], None],
        ctrl_f_held: bool = False,
    ) -> None:
        draw_list = imgui.get_window_draw_list()

        # Grid lines
        grid_col = _color4_to_u32(0.25, 0.25, 0.25, 0.3)
        for gx in range(0, work_w + 1, GRID_PX):
            draw_list.add_line(
                origin_x + gx, origin_y,
                origin_x + gx, origin_y + work_h,
                grid_col,
            )
        for gy in range(0, work_h + 1, GRID_PX):
            draw_list.add_line(
                origin_x, origin_y + gy,
                origin_x + work_w, origin_y + gy,
                grid_col,
            )

        # Mouse state
        mouse_pos = imgui.get_io().mouse_pos
        mx, my = mouse_pos[0], mouse_pos[1]
        rel_mx = mx - origin_x
        rel_my = my - origin_y
        in_bounds = 0 <= rel_mx <= work_w and 0 <= rel_my <= work_h

        # Hover detection
        self.hovered_element = None
        if in_bounds:
            for elem in reversed(elements):
                ex, ey, ew, eh = elem_rect(elem)
                if ex <= rel_mx <= ex + ew and ey <= rel_my <= ey + eh:
                    self.hovered_element = elem
                    break

        # Click to select / deselect
        if imgui.is_mouse_clicked(0) and in_bounds:
            if self.hovered_element is not None:
                self.selected_element = self.hovered_element
                on_select(self.selected_element)
            elif active_tool is not None:
                # Start drag-create
                self._drag_start = (
                    snap_to_grid(int(rel_mx)),
                    snap_to_grid(int(rel_my)),
                )
                self._is_dragging = True
            else:
                self.selected_element = None
                on_select(None)

        # Drag-create in progress
        if self._is_dragging and self._drag_start is not None:
            if imgui.is_mouse_down(0):
                sx, sy = self._drag_start
                ex_snap = snap_to_grid(int(rel_mx))
                ey_snap = snap_to_grid(int(rel_my))
                x0 = min(sx, ex_snap)
                y0 = min(sy, ey_snap)
                x1 = max(sx, ex_snap)
                y1 = max(sy, ey_snap)
                w = max(GRID_PX, x1 - x0)
                h = max(GRID_PX, y1 - y0)
                # Preview rectangle
                draw_list.add_rect(
                    origin_x + x0,
                    origin_y + y0,
                    origin_x + x0 + w,
                    origin_y + y0 + h,
                    _color4_to_u32(1, 1, 0, 0.7),
                    thickness=2,
                )
            else:
                # Mouse released – finalize creation
                self._finalize_create(
                    rel_mx, rel_my, active_tool, span_configs, on_create
                )
                self._is_dragging = False
                self._drag_start = None

        # Draw elements
        for elem in elements:
            ex, ey, ew, eh = elem_rect(elem)
            if ew <= 0 or eh <= 0:
                continue
            r, g, b = _parse_color_attrib(elem)
            fill = _color4_to_u32(r, g, b, 0.45)
            draw_list.add_rect_filled(
                origin_x + ex,
                origin_y + ey,
                origin_x + ex + ew,
                origin_y + ey + eh,
                fill,
            )

            # Outlines
            show_outline = (
                elem is self.selected_element
                or ctrl_f_held
            )
            if show_outline:
                if elem is self.selected_element:
                    ol_col = _color4_to_u32(*COLOR_OUTLINE_SELECTED)
                elif ctrl_f_held and elem is self.hovered_element:
                    ol_col = _color4_to_u32(*COLOR_OUTLINE_FOCUSED)
                else:
                    ol_col = _color4_to_u32(*COLOR_OUTLINE_REVEAL)

                draw_list.add_rect(
                    origin_x + ex,
                    origin_y + ey,
                    origin_x + ex + ew,
                    origin_y + ey + eh,
                    ol_col,
                    thickness=OUTLINE_WIDTH,
                )

            # Delete X button on selected
            if elem is self.selected_element:
                bx = origin_x + ex + ew - 10
                by = origin_y + ey + 2
                draw_list.add_text(bx, by, _color4_to_u32(*COLOR_DELETE_X), "X")
                # Check click on X region
                if (
                    imgui.is_mouse_clicked(0)
                    and bx <= mx <= bx + 10
                    and by <= my <= by + 12
                ):
                    on_delete(elem)
                    self.selected_element = None
                    on_select(None)

    # ------------------------------------------------------------------
    def _finalize_create(
        self,
        rel_mx: float,
        rel_my: float,
        tool: Optional[UIElementDef],
        span_configs: dict,
        on_create: Callable[[str, Dict[str, str]], None],
    ) -> None:
        if tool is None or self._drag_start is None:
            return
        sx, sy = self._drag_start
        ex = snap_to_grid(int(rel_mx))
        ey = snap_to_grid(int(rel_my))
        x0 = min(sx, ex)
        y0 = min(sy, ey)
        x1 = max(sx, ex)
        y1 = max(sy, ey)
        w = max(GRID_PX, x1 - x0)
        h = max(GRID_PX, y1 - y0)

        tiles_w = w // GRID_PX
        tiles_h = h // GRID_PX

        # Check 1x1 constraint
        cfg = span_configs.get(tool.tag)
        if tiles_w == 1 and tiles_h == 1:
            if cfg and not cfg.supports_1x1:
                return  # silently reject
            if not tool.supports_1x1:
                return

        attribs = dict(tool.default_attribs)
        attribs["x"] = str(x0)
        attribs["y"] = str(y0)
        attribs["width"] = str(w)
        attribs["height"] = str(h)

        on_create(tool.tag, attribs)

    # ------------------------------------------------------------------
    def draw_png_preview(
        self,
        texture_id: int,
        tex_w: int,
        tex_h: int,
        origin_x: float,
        origin_y: float,
    ) -> None:
        """Draw a read-only PNG preview in the work area."""
        draw_list = imgui.get_window_draw_list()
        draw_list.add_image(
            texture_id,
            (origin_x, origin_y),
            (origin_x + tex_w, origin_y + tex_h),
        )
