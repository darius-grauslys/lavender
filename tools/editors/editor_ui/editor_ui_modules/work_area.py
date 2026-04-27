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

from tools.editors.editor_ui.editor_ui_modules.constants import (
    COLOR_DELETE_X,
    COLOR_OUTLINE_FOCUSED,
    COLOR_OUTLINE_REVEAL,
    COLOR_OUTLINE_SELECTED,
    GRID_PX,
    OUTLINE_WIDTH,
    X_BUTTON_HEIGHT,
)
from tools.editors.editor_ui.editor_ui_modules.span_renderer import build_span_tile_grid
from tools.editors.editor_ui.editor_ui_modules.ui_element_defs import ELEMENT_DEF_BY_TAG, UIElementDef
from tools.editors.editor_ui.editor_ui_modules.xml_backing import ResolvedElement
from tools.editors.editor_ui.editor_ui_modules.xml_backing import (
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


def _parse_color_attrib(elem) -> Tuple[float, float, float]:
    """Parse color from an ET.Element or ResolvedElement."""
    if hasattr(elem, "xml_elem"):
        raw = elem.xml_elem.attrib.get("color", "55,55,55")
    else:
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
        self.selected_element = None
        self.hovered_element = None
        self.concealed_ids: set = set()  # set of id(xml_elem) for concealed elements
        self._drag_start: Optional[Tuple[int, int]] = None
        self._is_dragging: bool = False
        self._scroll_x: float = 0.0
        self._scroll_y: float = 0.0
        self._selection_frame: int = 0  # frame counter when selection happened
        self._frame_counter: int = 0    # monotonic frame counter
        self._x_consumed_click: bool = False
        self._pending_x_rect: Optional[Tuple[float, float, float, float]] = None  # (x0,y0,x1,y1)
        self._pending_x_elem = None  # the element whose X is shown
        # PNG preview
        self._preview_texture_id: Optional[int] = None
        self._preview_path: Optional[str] = None

    # ------------------------------------------------------------------
    # Main draw
    # ------------------------------------------------------------------

    def draw(
        self,
        elements: list,
        root: Optional[ET.Element],
        active_tool: Optional[UIElementDef],
        span_configs: dict,
        work_w: int,
        work_h: int,
        origin_x: float,
        origin_y: float,
        on_select: Callable,
        on_delete: Callable,
        on_create: Callable[[str, Dict[str, str]], None],
        ctrl_f_held: bool = False,
        backgrounds: Optional[list] = None,
        zoom: float = 1.0,
        tileset_picker=None,
    ) -> None:
        self._frame_counter += 1
        draw_list = imgui.get_window_draw_list()
        zw = int(work_w * zoom)
        zh = int(work_h * zoom)
        grid_step = max(1, int(GRID_PX * zoom))

        # Grid lines
        grid_col = _color4_to_u32(0.25, 0.25, 0.25, 0.3)
        gx = 0
        while gx <= zw:
            draw_list.add_line(
                origin_x + gx, origin_y,
                origin_x + gx, origin_y + zh,
                grid_col,
            )
            gx += grid_step
        gy = 0
        while gy <= zh:
            draw_list.add_line(
                origin_x, origin_y + gy,
                origin_x + zw, origin_y + gy,
                grid_col,
            )
            gy += grid_step

        # Background images (rendered under elements, over grid)
        if backgrounds:
            for bg_tex_id, bg_w, bg_h, bg_x, bg_y in backgrounds:
                if bg_tex_id is not None:
                    draw_list.add_image(
                        bg_tex_id,
                        (origin_x + bg_x * zoom, origin_y + bg_y * zoom),
                        (origin_x + (bg_x + bg_w) * zoom,
                         origin_y + (bg_y + bg_h) * zoom),
                    )

        # Mouse state
        mouse_pos = imgui.get_io().mouse_pos
        mx, my = mouse_pos[0], mouse_pos[1]
        # Convert screen coords to logical (unzoomed) coords
        rel_mx_screen = mx - origin_x
        rel_my_screen = my - origin_y
        rel_mx = rel_mx_screen / zoom if zoom != 0 else 0
        rel_my = rel_my_screen / zoom if zoom != 0 else 0
        in_bounds = 0 <= rel_mx <= work_w and 0 <= rel_my <= work_h

        # Hover detection (skip concealed)
        self.hovered_element = None
        if in_bounds:
            for elem in reversed(elements):
                xml_e = elem.xml_elem if isinstance(elem, ResolvedElement) else elem
                if id(xml_e) in self.concealed_ids:
                    continue
                ex, ey, ew, eh = elem_rect(elem)
                if ex <= rel_mx <= ex + ew and ey <= rel_my <= ey + eh:
                    self.hovered_element = elem
                    break

        # Check if the X delete button from previous frame was clicked
        self._x_consumed_click = False
        if (
            self._pending_x_rect is not None
            and self._pending_x_elem is not None
            and imgui.is_mouse_clicked(0)
        ):
            px0, py0, px1, py1 = self._pending_x_rect
            if px0 <= mx <= px1 and py0 <= my <= py1:
                # X was clicked — delete the element
                xml_elem = self._pending_x_elem
                if hasattr(xml_elem, "xml_elem"):
                    xml_elem = xml_elem.xml_elem
                on_delete(xml_elem)
                self.selected_element = None
                self._pending_x_rect = None
                self._pending_x_elem = None
                on_select(None)
                self._x_consumed_click = True

        # Click to select / deselect (skip if any imgui item is active, e.g. HUD resize)
        any_item_active = imgui.is_any_item_active()
        if imgui.is_mouse_clicked(0) and in_bounds and not self._x_consumed_click and not any_item_active:
            if self.hovered_element is not None:
                self.selected_element = self.hovered_element
                self._selection_frame = self._frame_counter
                xml_elem = self.selected_element
                if hasattr(xml_elem, "xml_elem"):
                    xml_elem = xml_elem.xml_elem
                on_select(xml_elem)
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

        # Deselect on right-click
        if imgui.is_mouse_clicked(1) and in_bounds:
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
                    origin_x + x0 * zoom,
                    origin_y + y0 * zoom,
                    origin_x + (x0 + w) * zoom,
                    origin_y + (y0 + h) * zoom,
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

        # Draw elements (skip concealed)
        selected_x_info = None  # will store (bx, by, elem) for top-layer X

        for elem in elements:
            # Check concealment
            xml_e = elem.xml_elem if isinstance(elem, ResolvedElement) else elem
            if id(xml_e) in self.concealed_ids:
                continue

            ex, ey, ew, eh = elem_rect(elem)
            if ew <= 0 or eh <= 0:
                continue

            is_container_elem = (
                isinstance(elem, ResolvedElement) and elem.is_container
            )

            r, g, b = _parse_color_attrib(elem)

            if is_container_elem:
                # Containers: pad top by X_BUTTON_HEIGHT so X is visible above children
                pad_top = X_BUTTON_HEIGHT * zoom
                fill = _color4_to_u32(r, g, b, 0.15)
                draw_list.add_rect_filled(
                    origin_x + ex * zoom,
                    origin_y + ey * zoom - pad_top,
                    origin_x + (ex + ew) * zoom,
                    origin_y + (ey + eh) * zoom,
                    fill,
                )
                border_col = _color4_to_u32(r, g, b, 0.6)
                draw_list.add_rect(
                    origin_x + ex * zoom,
                    origin_y + ey * zoom - pad_top,
                    origin_x + (ex + ew) * zoom,
                    origin_y + (ey + eh) * zoom,
                    border_col,
                    thickness=1,
                )
            else:
                fill = _color4_to_u32(r, g, b, 0.45)
                draw_list.add_rect_filled(
                    origin_x + ex * zoom,
                    origin_y + ey * zoom,
                    origin_x + (ex + ew) * zoom,
                    origin_y + (ey + eh) * zoom,
                    fill,
                )

            # Render UI span overlay if element has a span-capable type
            if not is_container_elem:
                elem_tag = elem.xml_elem.tag if isinstance(elem, ResolvedElement) else (
                    elem.tag if hasattr(elem, "tag") else ""
                )
            else:
                elem_tag = ""
            edef = ELEMENT_DEF_BY_TAG.get(elem_tag)
            if (
                edef is not None
                and edef.has_ui_span
                and not is_container_elem
                and tileset_picker is not None
                and tileset_picker.is_loaded
                and tileset_picker._gl_texture_id is not None
            ):
                # Check for per-element UI_Span attribute first
                xml_e_for_span = elem.xml_elem if isinstance(elem, ResolvedElement) else elem
                elem_span_str = xml_e_for_span.attrib.get("UI_Span", "") if hasattr(xml_e_for_span, 'attrib') else ""
                per_elem_9 = None
                if elem_span_str:
                    try:
                        # Multi-span: take first span (before ";")
                        first_span = elem_span_str.split(";")[0].strip()
                        parts = [int(p.strip()) for p in first_span.split(",")]
                        if len(parts) == 9:
                            per_elem_9 = parts
                    except ValueError:
                        pass

                span_cfg = span_configs.get(elem_tag)
                if span_cfg is not None or per_elem_9 is not None:
                    # Snap tile origin to grid
                    tile_x0 = (ex // GRID_PX) * GRID_PX
                    tile_y0 = (ey // GRID_PX) * GRID_PX
                    # Compute tile extent: round up to cover the element
                    tile_x1 = -(-((ex + ew) - tile_x0) // GRID_PX) * GRID_PX + tile_x0
                    tile_y1 = -(-((ey + eh) - tile_y0) // GRID_PX) * GRID_PX + tile_y0
                    tiles_w = max(1, (tile_x1 - tile_x0) // GRID_PX)
                    tiles_h = max(1, (tile_y1 - tile_y0) // GRID_PX)

                    if per_elem_9 is not None:
                        s1x1 = per_elem_9[0]
                        s9 = per_elem_9
                        sup1 = True
                        supn = True
                    elif span_cfg is not None:
                        s1x1 = span_cfg.span_1x1_index
                        s9 = span_cfg.span_9_indices
                        sup1 = span_cfg.supports_1x1
                        supn = span_cfg.supports_nxn
                    else:
                        s1x1 = 0
                        s9 = [0]*9
                        sup1 = False
                        supn = False

                    tile_grid = build_span_tile_grid(
                        tiles_w, tiles_h, s1x1, s9, sup1, supn,
                    )
                    tile_sz = GRID_PX * zoom
                    for row_idx, row_tiles in enumerate(tile_grid):
                        for col_idx, tile_index in enumerate(row_tiles):
                            u0, v0, u1, v1 = tileset_picker.get_tile_uv(tile_index)
                            tx = origin_x + (tile_x0 + col_idx * GRID_PX) * zoom
                            ty = origin_y + (tile_y0 + row_idx * GRID_PX) * zoom
                            draw_list.add_image(
                                tileset_picker._gl_texture_id,
                                (tx, ty),
                                (tx + tile_sz, ty + tile_sz),
                                uv_a=(u0, v0),
                                uv_b=(u1, v1),
                            )

            # Container label (in the padded area above)
            if is_container_elem:
                pad_top = X_BUTTON_HEIGHT * zoom
                label_tag = elem.xml_elem.tag if isinstance(elem, ResolvedElement) else "container"
                label_col = _color4_to_u32(r, g, b, 0.9)
                draw_list.add_text(
                    origin_x + ex * zoom + 2,
                    origin_y + ey * zoom - pad_top + 2,
                    label_col,
                    f"<{label_tag}>",
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

                top_y = origin_y + ey * zoom
                if is_container_elem:
                    top_y -= X_BUTTON_HEIGHT * zoom
                draw_list.add_rect(
                    origin_x + ex * zoom,
                    top_y,
                    origin_x + (ex + ew) * zoom,
                    origin_y + (ey + eh) * zoom,
                    ol_col,
                    thickness=OUTLINE_WIDTH,
                )

            # Record X button position for selected element (drawn on top later)
            is_owned = (
                isinstance(elem, ResolvedElement)
                and elem.is_container_owned
                and not elem.is_container
            )
            if elem is self.selected_element and not is_owned:
                bx = origin_x + (ex + ew) * zoom - 10
                if is_container_elem:
                    by = origin_y + ey * zoom - X_BUTTON_HEIGHT * zoom + 2
                else:
                    by = origin_y + ey * zoom + 2
                selected_x_info = (bx, by, elem)

        # Draw the X delete button on TOP of everything (for selected element)
        # Only clickable on a frame AFTER the selection frame (two-click system)
        if selected_x_info is not None:
            bx, by, sel_elem = selected_x_info
            x_is_active = (self._frame_counter > self._selection_frame)
            draw_list.add_rect_filled(
                bx - 2, by - 1, bx + 12, by + 14,
                _color4_to_u32(0.15, 0.15, 0.15, 0.85),
            )
            if x_is_active:
                draw_list.add_text(bx, by, _color4_to_u32(*COLOR_DELETE_X), "X")
                # Store rect for next frame's click check
                self._pending_x_rect = (bx - 2, by - 1, bx + 12, by + 14)
                self._pending_x_elem = sel_elem
            else:
                draw_list.add_text(bx, by, _color4_to_u32(0.5, 0.2, 0.2, 0.5), "X")
                self._pending_x_rect = None
                self._pending_x_elem = None
        else:
            self._pending_x_rect = None
            self._pending_x_elem = None

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
        # Flip UVs vertically: pyglet pixel data is top-to-bottom,
        # but GL texture origin is bottom-left.
        draw_list.add_image(
            texture_id,
            (origin_x, origin_y),
            (origin_x + tex_w, origin_y + tex_h),
        )
