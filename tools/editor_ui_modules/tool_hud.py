"""Top-right TOOL HUD – tool palette, UI-span configuration, tileset picker,
and toolset management.

Toolsets are stored as individual JSON files in assets/ui/editor/toolsets/.
"""

from __future__ import annotations

import json
import os
import re
from typing import Dict, List, Optional, Tuple

import imgui

from tools.editor_ui_modules.constants import (
    ASSET_UI_ROOT,
    GRID_PX,
    TOOLSET_DIR,
    TOOLSET_PREFIX,
    TOOLSET_SUFFIX,
    TOOLSET_DEFAULT_NAME,
)
from tools.editor_ui_modules.ui_element_defs import (
    ALL_ELEMENT_DEFS,
    UIElementDef,
)

# Default tileset path (per tool-invocation-spec.md §5.1)
_DEFAULT_TILESET_PATH = os.path.join(
    ASSET_UI_ROOT, "default", "_ui_tileset_default.png"
)

_VALID_TOOLSET_NAME = re.compile(r'^[a-zA-Z0-9_]+$')


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


class Toolset:
    """One named toolset with its own span configurations."""

    def __init__(self, name: str):
        self.name: str = name
        self.span_configs: Dict[str, ToolSpanConfig] = {}
        # Ensure every known element def has a config entry
        for edef in ALL_ELEMENT_DEFS:
            if edef.tag not in self.span_configs:
                self.span_configs[edef.tag] = ToolSpanConfig(
                    supports_1x1=edef.supports_1x1,
                    supports_nxn=edef.supports_nxn,
                )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "spans": {tag: cfg.to_dict() for tag, cfg in self.span_configs.items()},
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Toolset":
        name = d.get("name", TOOLSET_DEFAULT_NAME)
        ts = cls(name)
        for tag, cfg_dict in d.get("spans", {}).items():
            ts.span_configs[tag] = ToolSpanConfig.from_dict(cfg_dict)
        return ts


class ToolsetManager:
    """Manages multiple toolsets stored as individual JSON files."""

    def __init__(self):
        self.toolsets: List[Toolset] = []
        self.active_index: int = 0
        self._load_all()

    @property
    def active(self) -> Optional[Toolset]:
        if 0 <= self.active_index < len(self.toolsets):
            return self.toolsets[self.active_index]
        return None

    def select_by_name(self, name: str) -> bool:
        for i, ts in enumerate(self.toolsets):
            if ts.name == name:
                self.active_index = i
                return True
        if self.toolsets:
            self.active_index = 0
        return False

    def _toolset_path(self, name: str) -> str:
        return os.path.join(TOOLSET_DIR, f"{TOOLSET_PREFIX}{name}{TOOLSET_SUFFIX}")

    def _load_all(self) -> None:
        self.toolsets = []
        os.makedirs(TOOLSET_DIR, exist_ok=True)
        files = sorted(f for f in os.listdir(TOOLSET_DIR)
                        if f.startswith(TOOLSET_PREFIX) and f.endswith(TOOLSET_SUFFIX))
        if not files:
            # Create default
            ts = Toolset(TOOLSET_DEFAULT_NAME)
            self.toolsets.append(ts)
            self._save_toolset(ts)
        else:
            for f in files:
                path = os.path.join(TOOLSET_DIR, f)
                try:
                    with open(path, "r", encoding="utf-8") as fh:
                        data = json.load(fh)
                    ts = Toolset.from_dict(data)
                    self.toolsets.append(ts)
                except (json.JSONDecodeError, OSError):
                    pass
        if not self.toolsets:
            ts = Toolset(TOOLSET_DEFAULT_NAME)
            self.toolsets.append(ts)
            self._save_toolset(ts)
        self.active_index = 0

    def _save_toolset(self, ts: Toolset) -> None:
        os.makedirs(TOOLSET_DIR, exist_ok=True)
        path = self._toolset_path(ts.name)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(ts.to_dict(), fh, indent=2)

    def save_active(self) -> None:
        ts = self.active
        if ts:
            self._save_toolset(ts)

    def create_toolset(self, name: str) -> Optional[Toolset]:
        if not _VALID_TOOLSET_NAME.match(name):
            return None
        for ts in self.toolsets:
            if ts.name == name:
                return None  # already exists
        ts = Toolset(name)
        self.toolsets.append(ts)
        self._save_toolset(ts)
        self.active_index = len(self.toolsets) - 1
        return ts

    def delete_toolset(self, index: int) -> bool:
        if index < 0 or index >= len(self.toolsets):
            return False
        if len(self.toolsets) <= 1:
            return False  # can't delete last
        ts = self.toolsets.pop(index)
        path = self._toolset_path(ts.name)
        if os.path.exists(path):
            os.remove(path)
        if self.active_index >= len(self.toolsets):
            self.active_index = len(self.toolsets) - 1
        return True

    def rename_toolset(self, index: int, new_name: str) -> bool:
        if not _VALID_TOOLSET_NAME.match(new_name):
            return False
        if index < 0 or index >= len(self.toolsets):
            return False
        old_path = self._toolset_path(self.toolsets[index].name)
        self.toolsets[index].name = new_name
        if os.path.exists(old_path):
            os.remove(old_path)
        self._save_toolset(self.toolsets[index])
        return True


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
    """Top-right tool palette with toolset management."""

    def __init__(self):
        self.selected_tool: Optional[UIElementDef] = None
        self._tileset_picker = TilesetPicker()
        self.toolset_mgr = ToolsetManager()
        self._new_toolset_name: str = ""
        self._rename_buf: str = ""
        self._confirm_delete_index: int = -1  # -1 = no confirmation pending

    # -- accessors ---------------------------------------------------------

    @property
    def _span_configs(self) -> Dict[str, ToolSpanConfig]:
        ts = self.toolset_mgr.active
        return ts.span_configs if ts else {}

    def get_span_config(self, tag: str) -> ToolSpanConfig:
        return self._span_configs.get(tag, ToolSpanConfig())

    def get_active_toolset_name(self) -> str:
        ts = self.toolset_mgr.active
        return ts.name if ts else TOOLSET_DEFAULT_NAME

    def select_toolset_by_name(self, name: str) -> None:
        self.toolset_mgr.select_by_name(name)

    # -- drawing -----------------------------------------------------------

    def draw(self, *args, **kwargs):
        return self.draw_with_pick_capture(*args, **kwargs)

    def draw_with_pick_capture(
        self,
        window_width: float,
        window_height: float,
        panel_width: float = 220,
    ) -> Optional[UIElementDef]:
        """Draw tool contents (no window creation – expects to be in a child)."""
        self._tileset_picker.ensure_loaded()

        # --- Toolset tab bar ---
        imgui.text("Toolset:")
        imgui.begin_child("##toolset_tabs", 0, 24, border=False)
        for i, ts in enumerate(self.toolset_mgr.toolsets):
            if i > 0:
                imgui.same_line()
            is_active = (i == self.toolset_mgr.active_index)
            if is_active:
                imgui.push_style_color(imgui.COLOR_BUTTON, 0.3, 0.3, 0.7, 1.0)
            if imgui.small_button(f"{ts.name}##ts_{i}"):
                self.toolset_mgr.active_index = i
            if is_active:
                imgui.pop_style_color()
        # "+" tab for new toolset
        imgui.same_line()
        if imgui.small_button("+##new_ts"):
            imgui.open_popup("new_toolset_popup")
        # New toolset popup
        if imgui.begin_popup("new_toolset_popup"):
            imgui.text("New toolset name:")
            c, self._new_toolset_name = imgui.input_text(
                "##new_ts_name", self._new_toolset_name, 64,
                imgui.INPUT_TEXT_ENTER_RETURNS_TRUE,
            )
            if c and self._new_toolset_name:
                if _VALID_TOOLSET_NAME.match(self._new_toolset_name):
                    result = self.toolset_mgr.create_toolset(self._new_toolset_name)
                    if result is None:
                        pass  # name exists or invalid
                    self._new_toolset_name = ""
                    imgui.close_current_popup()
                else:
                    imgui.text_colored("Invalid name (alphanumeric + _)", 1, 0.3, 0.3)
            imgui.end_popup()
        imgui.end_child()

        # --- Toolset name + delete ---
        ts = self.toolset_mgr.active
        if ts is not None:
            imgui.separator()
            # Rename field
            if not hasattr(self, '_rename_buf_init') or self._rename_buf_init != ts.name:
                self._rename_buf = ts.name
                self._rename_buf_init = ts.name
            changed_name, new_name = imgui.input_text(
                "##ts_rename", self._rename_buf, 64,
                imgui.INPUT_TEXT_ENTER_RETURNS_TRUE,
            )
            if changed_name and new_name != ts.name:
                if _VALID_TOOLSET_NAME.match(new_name):
                    self.toolset_mgr.rename_toolset(
                        self.toolset_mgr.active_index, new_name
                    )
                    self._rename_buf = new_name
                    self._rename_buf_init = new_name
            else:
                self._rename_buf = new_name if changed_name else self._rename_buf

            imgui.same_line()
            imgui.push_style_color(imgui.COLOR_BUTTON, 0.6, 0.1, 0.1, 1.0)
            if imgui.small_button("X##del_ts"):
                self._confirm_delete_index = self.toolset_mgr.active_index
            imgui.pop_style_color()

        imgui.separator()

        # --- Tool list ---
        imgui.text("Tools:")
        for edef in ALL_ELEMENT_DEFS:
            is_sel = self.selected_tool is edef
            if imgui.selectable(
                f"{edef.display_name}##{edef.tag}", is_sel
            )[0]:
                self.selected_tool = edef

        imgui.separator()

        # --- Span config ---
        if self.selected_tool is not None and ts is not None:
            tag = self.selected_tool.tag

            if self.selected_tool.has_ui_span:
                cfg = ts.span_configs.setdefault(tag, ToolSpanConfig())
                changed = False

                imgui.text(f"Span: {self.selected_tool.display_name}")

                c1, cfg.supports_1x1 = imgui.checkbox("1x1 support##wpc", cfg.supports_1x1)
                changed = changed or c1
                c2, cfg.supports_nxn = imgui.checkbox("NxN support##wpc", cfg.supports_nxn)
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
                        imgui.push_id(f"span9wpc_{tag}_{i}")
                        self._tileset_picker.draw_tile_button(
                            label, cfg.span_9_indices[i], ("9", tag, i), 32,
                        )
                        imgui.pop_id()

                if changed:
                    self.toolset_mgr.save_active()
            else:
                imgui.text(f"{self.selected_tool.display_name}")
                imgui.text_colored("(no UI span)", 0.6, 0.6, 0.6)

        # --- Tileset picker popup ---
        pick_id = self._tileset_picker.picking_for
        picked_index = self._tileset_picker.draw_picker_popup()

        if picked_index is not None and pick_id is not None and ts is not None:
            if pick_id[0] == "1x1":
                pick_cfg = ts.span_configs.get(pick_id[1])
                if pick_cfg:
                    pick_cfg.span_1x1_index = picked_index
            elif pick_id[0] == "9":
                pick_cfg = ts.span_configs.get(pick_id[1])
                if pick_cfg:
                    pick_cfg.span_9_indices[pick_id[2]] = picked_index
            self.toolset_mgr.save_active()

        # --- Delete confirmation popup ---
        if self._confirm_delete_index >= 0:
            self._draw_delete_confirmation()

        return self.selected_tool

    def _draw_delete_confirmation(self) -> None:
        idx = self._confirm_delete_index
        if idx < 0 or idx >= len(self.toolset_mgr.toolsets):
            self._confirm_delete_index = -1
            return
        ts_name = self.toolset_mgr.toolsets[idx].name

        imgui.set_next_window_size(300, 120)
        io = imgui.get_io()
        imgui.set_next_window_position(
            io.display_size.x * 0.5 - 150,
            io.display_size.y * 0.5 - 60,
            condition=imgui.APPEARING,
        )
        imgui.begin(
            "Delete Toolset?##confirm_del",
            closable=False,
            flags=(
                imgui.WINDOW_NO_RESIZE
                | imgui.WINDOW_NO_SAVED_SETTINGS
                | imgui.WINDOW_NO_COLLAPSE
            ),
        )
        imgui.text(f"Delete toolset '{ts_name}'?")
        imgui.text("This cannot be undone.")
        imgui.separator()
        if imgui.button("Yes, delete##confirm_yes", 120, 0):
            self.toolset_mgr.delete_toolset(idx)
            self._confirm_delete_index = -1
            self._rename_buf_init = ""  # force rename buf refresh
        imgui.same_line()
        if imgui.button("Cancel##confirm_no", 120, 0):
            self._confirm_delete_index = -1
        imgui.end()
