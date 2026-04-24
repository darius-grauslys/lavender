"""Top-right TOOL HUD – tool palette, UI-span configuration, and tileset picker.

Reads / writes ``tools.json`` from the assets/ui directory.
"""

from __future__ import annotations

import json
import os
from typing import Dict, List, Optional, Tuple

import imgui

from tools.editor_ui_modules.constants import ASSET_UI_ROOT, GRID_PX, TOOLS_JSON_RELPATH
from tools.editor_ui_modules.ui_element_defs import (
    ALL_ELEMENT_DEFS,
    UIElementDef,
)

# Default tileset path (per tool-invocation-spec.md §5.1)
_DEFAULT_TILESET_PATH = os.path.join(
    ASSET_UI_ROOT, "default", "_ui_tileset_default.png"
)


class ToolSpanConfig:
    """Persisted span configuration for one tool."""

    def __init__(
        self,
        supports_1x1: bool = False,
        supports_nxn: bool = False,
        span_1x1_index: int = 0,
        span_9_indices: Optional[List[int]] = None,
    ):
        self.supports_1x1 = supports_1x1
        self.supports_nxn = supports_nxn
        self.span_1x1_index = span_1x1_index
        self.span_9_indices = span_9_indices if span_9_indices is not None else [0] * 9

    def to_dict(self) -> dict:
        return {
            "supports_1x1": self.supports_1x1,
            "supports_nxn": self.supports_nxn,
            "span_1x1_index": self.span_1x1_index,
            "span_9_indices": list(self.span_9_indices),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ToolSpanConfig":
        return cls(
            supports_1x1=d.get("supports_1x1", False),
            supports_nxn=d.get("supports_nxn", False),
            span_1x1_index=d.get("span_1x1_index", 0),
            span_9_indices=d.get("span_9_indices", [0] * 9),
        )


class TilesetPicker:
    """Manages loading the default tileset and rendering a picker popup."""

    def __init__(self):
        self._gl_texture_id: Optional[int] = None
        self._tex_w: int = 0
        self._tex_h: int = 0
        self._cols: int = 0
        self._rows: int = 0
        self._loaded: bool = False
        # Which slot is being picked: ("1x1", tag) or ("9", tag, slot_index)
        self._picking_for: Optional[tuple] = None

    @property
    def is_loaded(self) -> bool:
        return self._loaded and self._gl_texture_id is not None

    def ensure_loaded(self) -> None:
        """Load the default tileset into a GL texture (once)."""
        if self._loaded:
            return
        self._loaded = True
        path = _DEFAULT_TILESET_PATH
        if not os.path.exists(path):
            return
        try:
            from OpenGL import GL as gl
            import pyglet

            img = pyglet.image.load(path)
            self._tex_w = img.width
            self._tex_h = img.height
            self._cols = max(1, self._tex_w // GRID_PX)
            self._rows = max(1, self._tex_h // GRID_PX)

            raw = img.get_image_data()
            fmt = "RGBA"
            pitch = self._tex_w * 4
            pixel_data = bytearray(raw.get_data(fmt, pitch))
            # Magenta-key transparency
            for i in range(len(pixel_data) // 4):
                r = pixel_data[i * 4]
                g = pixel_data[i * 4 + 1]
                b = pixel_data[i * 4 + 2]
                if r == 0xFF and b == 0xFF and g == 0x00:
                    pixel_data[i * 4 + 3] = 0x00

            # Flip rows so GL texture is right-side-up
            row_size = self._tex_w * 4
            flipped = bytearray(len(pixel_data))
            for row in range(self._tex_h):
                src_off = row * row_size
                dst_off = (self._tex_h - 1 - row) * row_size
                flipped[dst_off:dst_off + row_size] = pixel_data[src_off:src_off + row_size]

            tex_id = gl.glGenTextures(1)
            gl.glBindTexture(gl.GL_TEXTURE_2D, tex_id)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
            gl.glTexImage2D(
                gl.GL_TEXTURE_2D, 0, gl.GL_RGBA,
                self._tex_w, self._tex_h, 0,
                gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, bytes(flipped),
            )
            gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
            self._gl_texture_id = tex_id
        except Exception:
            self._gl_texture_id = None

    def begin_pick(self, pick_id: tuple) -> None:
        """Start picking for a given slot."""
        self._picking_for = pick_id

    def is_picking(self) -> bool:
        return self._picking_for is not None

    def get_tile_uv(self, tile_index: int) -> Tuple[float, float, float, float]:
        """Return (u0, v0, u1, v1) in [0..1] for a tile index.

        Texture rows have been pre-flipped so UVs are standard top-left origin.
        """
        if self._cols == 0 or self._tex_w == 0 or self._tex_h == 0:
            return (0, 0, 1, 1)
        col = tile_index % self._cols
        row = tile_index // self._cols
        u0 = col * GRID_PX / self._tex_w
        v0 = row * GRID_PX / self._tex_h
        u1 = (col + 1) * GRID_PX / self._tex_w
        v1 = (row + 1) * GRID_PX / self._tex_h
        return (u0, v0, u1, v1)

    def draw_tile_button(
        self,
        label: str,
        tile_index: int,
        pick_id: tuple,
        button_size: float = 32,
    ) -> bool:
        """Draw a button showing the tile.  Returns True if clicked."""
        clicked = False
        if self.is_loaded and self._gl_texture_id is not None:
            u0, v0, u1, v1 = self.get_tile_uv(tile_index)
            if imgui.image_button(
                self._gl_texture_id,
                button_size, button_size,
                uv0=(u0, v0), uv1=(u1, v1),
                frame_padding=2,
            ):
                self.begin_pick(pick_id)
                clicked = True
            # Tooltip with index
            if imgui.is_item_hovered():
                imgui.set_tooltip(f"{label}: tile {tile_index}")
        else:
            # Fallback: text button
            if imgui.button(f"{tile_index}##{label}", button_size, button_size):
                self.begin_pick(pick_id)
                clicked = True
        return clicked

    def draw_picker_popup(self) -> Optional[int]:
        """Draw the tileset picker overlay.  Returns selected index or None."""
        if self._picking_for is None:
            return None

        selected: Optional[int] = None
        scale = 2  # display tiles at 2× for easier clicking
        tile_display = GRID_PX * scale

        imgui.set_next_window_size(
            min(self._cols * tile_display + 32, 520),
            min(self._rows * tile_display + 64, 400),
        )
        imgui.set_next_window_position(
            imgui.get_io().display_size.x * 0.5 - 200,
            imgui.get_io().display_size.y * 0.5 - 150,
            condition=imgui.APPEARING,
        )

        opened = imgui.begin(
            "Tileset Picker##tileset_picker",
            closable=True,
            flags=imgui.WINDOW_NO_SAVED_SETTINGS,
        )
        if not opened[1]:
            # User closed the window
            self._picking_for = None
            imgui.end()
            return None

        imgui.text("Click a tile to select it:")
        imgui.separator()

        if self.is_loaded and self._gl_texture_id is not None:
            imgui.begin_child("##tileset_scroll", 0, 0, border=True)
            total_tiles = self._cols * self._rows
            for idx in range(total_tiles):
                col = idx % self._cols
                if col != 0:
                    imgui.same_line(spacing=0)
                u0, v0, u1, v1 = self.get_tile_uv(idx)
                imgui.push_id(f"tile_{idx}")
                if imgui.image_button(
                    self._gl_texture_id,
                    tile_display, tile_display,
                    uv0=(u0, v0), uv1=(u1, v1),
                    frame_padding=1,
                ):
                    selected = idx
                imgui.pop_id()
                if imgui.is_item_hovered():
                    imgui.set_tooltip(f"Tile {idx}")
            imgui.end_child()
        else:
            imgui.text("(tileset not found)")

        imgui.end()

        if selected is not None:
            self._picking_for = None  # close after selection

        return selected

    @property
    def picking_for(self) -> Optional[tuple]:
        return self._picking_for


class ToolHUD:
    """Top-right tool palette."""

    def __init__(self):
        self.selected_tool: Optional[UIElementDef] = None
        self._span_configs: Dict[str, ToolSpanConfig] = {}
        self._tileset_picker = TilesetPicker()
        self._load_tools_json()
        # Ensure every known element def has a config entry
        for edef in ALL_ELEMENT_DEFS:
            if edef.tag not in self._span_configs:
                self._span_configs[edef.tag] = ToolSpanConfig(
                    supports_1x1=edef.supports_1x1,
                    supports_nxn=edef.supports_nxn,
                )

    # -- persistence -------------------------------------------------------

    def _json_path(self) -> str:
        return os.path.join(ASSET_UI_ROOT, TOOLS_JSON_RELPATH)

    def _load_tools_json(self) -> None:
        path = self._json_path()
        if not os.path.exists(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            for tag, cfg_dict in data.items():
                self._span_configs[tag] = ToolSpanConfig.from_dict(cfg_dict)
        except (json.JSONDecodeError, OSError):
            pass

    def _save_tools_json(self) -> None:
        path = self._json_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        data = {tag: cfg.to_dict() for tag, cfg in self._span_configs.items()}
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)

    # -- accessors ---------------------------------------------------------

    def get_span_config(self, tag: str) -> ToolSpanConfig:
        return self._span_configs.get(tag, ToolSpanConfig())

    # -- drawing -----------------------------------------------------------

    def draw(
        self,
        window_width: float,
        window_height: float,
        panel_width: float = 220,
    ) -> Optional[UIElementDef]:
        """Draw the tool palette.  Returns the currently selected tool def."""
        self._tileset_picker.ensure_loaded()

        half_h = window_height * 0.5
        imgui.set_next_window_position(window_width - panel_width, 0)
        imgui.set_next_window_size(panel_width, half_h)

        flags = (
            imgui.WINDOW_NO_RESIZE
            | imgui.WINDOW_NO_MOVE
            | imgui.WINDOW_NO_SAVED_SETTINGS
        )
        imgui.begin("Tools##tool_hud", closable=False, flags=flags)

        imgui.text("Select a tool:")
        imgui.separator()

        for edef in ALL_ELEMENT_DEFS:
            is_sel = self.selected_tool is edef
            if imgui.selectable(
                f"{edef.display_name}##{edef.tag}", is_sel
            )[0]:
                self.selected_tool = edef

        imgui.separator()

        # Span config for selected tool
        if self.selected_tool is not None:
            tag = self.selected_tool.tag
            cfg = self._span_configs.setdefault(tag, ToolSpanConfig())
            changed = False

            imgui.text(f"Span: {self.selected_tool.display_name}")

            c1, cfg.supports_1x1 = imgui.checkbox("1x1 support", cfg.supports_1x1)
            changed = changed or c1
            c2, cfg.supports_nxn = imgui.checkbox("NxN support", cfg.supports_nxn)
            changed = changed or c2

            if cfg.supports_1x1:
                imgui.text("1x1 tile:")
                imgui.same_line()
                self._tileset_picker.draw_tile_button(
                    "1x1", cfg.span_1x1_index, ("1x1", tag), 32,
                )

            if cfg.supports_nxn:
                imgui.text("9-slice tiles:")
                labels = [
                    "TL", "T", "TR",
                    "L", "C", "R",
                    "BL", "B", "BR",
                ]
                for i, label in enumerate(labels):
                    if i % 3 != 0:
                        imgui.same_line()
                    self._tileset_picker.draw_tile_button(
                        label, cfg.span_9_indices[i], ("9", tag, i), 32,
                    )

            if changed:
                self._save_tools_json()

        imgui.end()

        # Draw the tileset picker overlay (if active)
        picked_index = self._tileset_picker.draw_picker_popup()
        if picked_index is not None and self._tileset_picker.picking_for is None:
            # Selection was just made — apply it
            self._apply_tile_pick(picked_index)

        return self.selected_tool

    def _apply_tile_pick(self, tile_index: int) -> None:
        """Apply a tile pick result to the appropriate span config slot."""
        # The picking_for was cleared by the picker, but we stored the
        # pick_id before the draw call.  We need to capture it before draw.
        # Refactor: capture pick_id before draw_picker_popup clears it.
        pass

    def draw_with_pick_capture(
        self,
        window_width: float,
        window_height: float,
        panel_width: float = 220,
    ) -> Optional[UIElementDef]:
        """Wrapper that properly captures tile picks."""
        self._tileset_picker.ensure_loaded()

        flags = (
            imgui.WINDOW_NO_MOVE
            | imgui.WINDOW_NO_SAVED_SETTINGS
        )
        imgui.begin("Tools##tool_hud", closable=False, flags=flags)

        imgui.text("Select a tool:")
        imgui.separator()

        for edef in ALL_ELEMENT_DEFS:
            is_sel = self.selected_tool is edef
            if imgui.selectable(
                f"{edef.display_name}##{edef.tag}", is_sel
            )[0]:
                self.selected_tool = edef

        imgui.separator()

        if self.selected_tool is not None:
            tag = self.selected_tool.tag
            cfg = self._span_configs.setdefault(tag, ToolSpanConfig())
            changed = False

            imgui.text(f"Span: {self.selected_tool.display_name}")

            c1, cfg.supports_1x1 = imgui.checkbox("1x1 support", cfg.supports_1x1)
            changed = changed or c1
            c2, cfg.supports_nxn = imgui.checkbox("NxN support", cfg.supports_nxn)
            changed = changed or c2

            if cfg.supports_1x1:
                imgui.text("1x1 tile:")
                imgui.same_line()
                self._tileset_picker.draw_tile_button(
                    "1x1", cfg.span_1x1_index, ("1x1", tag), 32,
                )

            if cfg.supports_nxn:
                imgui.text("9-slice tiles:")
                labels = [
                    "TL", "T", "TR",
                    "L", "C", "R",
                    "BL", "B", "BR",
                ]
                for i, label in enumerate(labels):
                    if i % 3 != 0:
                        imgui.same_line()
                    self._tileset_picker.draw_tile_button(
                        label, cfg.span_9_indices[i], ("9", tag, i), 32,
                    )

            if changed:
                self._save_tools_json()

        imgui.end()

        # Capture pick_id BEFORE drawing the popup (which clears it on select)
        pick_id = self._tileset_picker.picking_for
        picked_index = self._tileset_picker.draw_picker_popup()

        if picked_index is not None and pick_id is not None:
            # Apply the selection
            if pick_id[0] == "1x1":
                pick_tag = pick_id[1]
                pick_cfg = self._span_configs.get(pick_tag)
                if pick_cfg:
                    pick_cfg.span_1x1_index = picked_index
            elif pick_id[0] == "9":
                pick_tag = pick_id[1]
                slot = pick_id[2]
                pick_cfg = self._span_configs.get(pick_tag)
                if pick_cfg:
                    pick_cfg.span_9_indices[slot] = picked_index
            self._save_tools_json()

        return self.selected_tool
