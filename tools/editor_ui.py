#!/usr/bin/env python3
"""editor_ui – interactive XML-based UI editor for Lavender engine projects.

Usage:
    python tools/editor_ui.py

Requires: pyglet, imgui[pyglet]

See tools/tool-gen-prompts/editor_ui.py.md for the full specification.
"""

from __future__ import annotations

import os
import sys
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_TOOLS_DIR)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

import pyglet
from pyglet import gl as pgl
import ctypes
import imgui
from imgui.integrations.pyglet import PygletProgrammablePipelineRenderer as PygletRenderer
from OpenGL import GL as gl
from typing import Tuple

from tools.editor_ui_modules.constants import (
    ASSET_UI_ROOT,
    DEFAULT_WINDOW_H,
    DEFAULT_WINDOW_W,
    DEFAULT_WORK_H,
    DEFAULT_WORK_W,
    GRID_PX,
)
from tools.editor_ui_modules.file_browser import FileBrowser
from tools.editor_ui_modules.history import HistoryManager
from tools.editor_ui_modules.message_hud import MessageHUD
from tools.editor_ui_modules.properties_hud import PropertiesHUD
from tools.editor_ui_modules.tool_hud import ToolHUD
from tools.editor_ui_modules.work_area import WorkArea
from tools.editor_ui_modules.xml_backing import (
    add_element_to_ui,
    find_ui_elements,
    load_xml,
    remove_element,
    save_final,
    save_tmp,
    serialize_tree,
)


# ===================================================================
# Application state
# ===================================================================

class EditorApp:
    """Top-level application object that owns all sub-modules."""

    def __init__(self):
        # Sub-modules
        self.file_browser = FileBrowser()
        self.message_hud = MessageHUD()
        self.tool_hud = ToolHUD()
        self.properties_hud = PropertiesHUD()
        self.work_area = WorkArea()
        self.history = HistoryManager()

        # Current document
        self._xml_path: Optional[str] = None
        self._xml_root: Optional[ET.Element] = None
        self._elements: List[ET.Element] = []

        # PNG preview state
        self._png_path: Optional[str] = None
        self._png_texture_id: Optional[int] = None
        self._png_w: int = 0
        self._png_h: int = 0

        # Background textures: list of (gl_tex_id, w, h, x, y)
        self._bg_textures: List[Tuple] = []

        # Work area dimensions (from XML config or defaults)
        self.work_w: int = DEFAULT_WORK_W
        self.work_h: int = DEFAULT_WORK_H

        # Keyboard state
        self._ctrl_f_held: bool = False

        # Panel widths (resizable)
        self.left_panel_w: float = 200.0
        self.right_panel_w: float = 220.0

        # Zoom / pan
        self._zoom: float = 1.0
        self._pan_x: float = 0.0
        self._pan_y: float = 0.0

    # ------------------------------------------------------------------
    # File callbacks
    # ------------------------------------------------------------------

    def on_open_xml(self, path: str) -> None:
        """Called when a .xml file is selected in the file browser."""
        self._png_path = None
        self._png_texture_id = None
        self._xml_path = path
        root = load_xml(path)
        if root is None:
            self.message_hud.error(f"Failed to load: {path}")
            self._xml_root = None
            self._elements = []
            return
        self._xml_root = root
        self._elements = find_ui_elements(root)
        self._read_work_size_from_config()
        self._load_backgrounds_from_config(path)
        self.history = HistoryManager()
        self.history.push("open", serialize_tree(root))
        self.message_hud.info(f"Opened: {path}")
        self.properties_hud.select(None)
        self.work_area.selected_element = None

    def on_open_png(self, path: str) -> None:
        """Called when a .png file is selected – read-only preview."""
        self._xml_path = None
        self._xml_root = None
        self._elements = []
        self._png_path = path
        self._load_png_texture(path)
        self.message_hud.info(f"Viewing PNG: {path}")

    # ------------------------------------------------------------------
    # Element manipulation callbacks
    # ------------------------------------------------------------------

    def on_select_element(self, elem: Optional[ET.Element]) -> None:
        self.properties_hud.select(elem)

    def on_delete_element(self, elem: ET.Element) -> None:
        if self._xml_root is None:
            return
        if remove_element(self._xml_root, elem):
            self._elements = find_ui_elements(self._xml_root)
            self._commit("delete element")
            self.message_hud.info("Deleted element")

    def on_create_element(self, tag: str, attribs: Dict[str, str]) -> None:
        if self._xml_root is None:
            return
        new_elem = add_element_to_ui(self._xml_root, tag, attribs)
        if new_elem is not None:
            self._elements = find_ui_elements(self._xml_root)
            self._commit(f"create {tag}")
            self.work_area.selected_element = new_elem
            self.properties_hud.select(new_elem)
            self.message_hud.info(f"Created <{tag}>")

    def on_property_changed(self) -> None:
        """Called by PropertiesHUD when an attribute is edited."""
        if self._xml_root is not None:
            self._elements = find_ui_elements(self._xml_root)
            self._commit("edit property")

    # ------------------------------------------------------------------
    # History helpers
    # ------------------------------------------------------------------

    def _commit(self, desc: str) -> None:
        if self._xml_root is None or self._xml_path is None:
            return
        xml_text = serialize_tree(self._xml_root)
        self.history.push(desc, xml_text)
        save_tmp(self._xml_path, self._xml_root)

    def _restore_from_history(self, xml_text: Optional[str]) -> None:
        if xml_text is None or self._xml_path is None:
            return
        try:
            self._xml_root = ET.fromstring(xml_text)
        except ET.ParseError:
            self.message_hud.error("History record corrupt")
            return
        self._elements = find_ui_elements(self._xml_root)
        save_tmp(self._xml_path, self._xml_root)
        self.properties_hud.select(None)
        self.work_area.selected_element = None

    def undo(self) -> None:
        txt = self.history.undo()
        if txt:
            self._restore_from_history(txt)
            self.message_hud.info("Undo")
        else:
            self.message_hud.info("Nothing to undo")

    def redo(self) -> None:
        txt = self.history.redo()
        if txt:
            self._restore_from_history(txt)
            self.message_hud.info("Redo")
        else:
            self.message_hud.info("Nothing to redo")

    def save(self) -> None:
        if self._xml_root is not None and self._xml_path is not None:
            save_final(self._xml_path, self._xml_root)
            self.message_hud.info(f"Saved: {self._xml_path}")

    # ------------------------------------------------------------------
    # Config helpers
    # ------------------------------------------------------------------

    def _read_work_size_from_config(self) -> None:
        if self._xml_root is None:
            return
        cfg = self._xml_root.find("config")
        if cfg is None:
            return
        for elem in cfg:
            if elem.tag == "platform":
                size_str = elem.attrib.get("size", "")
                if "," in size_str:
                    parts = size_str.split(",")
                    try:
                        self.work_w = int(parts[0])
                        self.work_h = int(parts[1])
                    except ValueError:
                        pass

    # ------------------------------------------------------------------
    # Background loading from XML <config>
    # ------------------------------------------------------------------

    def _load_backgrounds_from_config(self, xml_path: str) -> None:
        """Parse <background> elements from <config> and load textures."""
        # Free old textures
        for tex_id, *_ in self._bg_textures:
            if tex_id is not None:
                try:
                    gl.glDeleteTextures([tex_id])
                except Exception:
                    pass
        self._bg_textures = []

        if self._xml_root is None:
            return
        cfg = self._xml_root.find("config")
        if cfg is None:
            return

        # Resolve paths relative to the XML file's directory
        xml_dir = os.path.dirname(os.path.abspath(xml_path))

        # Collect backgrounds sorted by layer
        bg_specs: List[Tuple[int, str, int, int]] = []  # (layer, path, x, y)
        for elem in cfg:
            if elem.tag == "background":
                layer = int(elem.attrib.get("layer", "0"))
                bg_path = elem.attrib.get("path", "")
                bg_x = int(elem.attrib.get("x", "0"))
                bg_y = int(elem.attrib.get("y", "0"))
                if bg_path:
                    bg_specs.append((layer, bg_path, bg_x, bg_y))

        bg_specs.sort(key=lambda t: t[0])

        for layer, bg_path, bg_x, bg_y in bg_specs:
            # Try resolving relative to xml dir first, then cwd
            full_path = os.path.join(xml_dir, bg_path)
            if not os.path.exists(full_path):
                full_path = bg_path
            if not os.path.exists(full_path):
                self.message_hud.error(f"Background not found: {bg_path}")
                continue
            tex_id, w, h = self._load_bg_texture(full_path)
            if tex_id is not None:
                self._bg_textures.append((tex_id, w, h, bg_x, bg_y))
                self.message_hud.info(
                    f"Loaded background layer {layer}: {bg_path}"
                )

    def _load_bg_texture(self, path: str) -> Tuple[Optional[int], int, int]:
        """Load a PNG into a GL texture with magenta-key transparency.

        Returns (texture_id, width, height) or (None, 0, 0) on failure.
        """
        try:
            img = pyglet.image.load(path)
            w = img.width
            h = img.height

            raw = img.get_image_data()
            fmt = "RGBA"
            pitch = w * 4
            pixel_data = bytearray(raw.get_data(fmt, pitch))

            # Apply magenta-key transparency
            for i in range(len(pixel_data) // 4):
                r = pixel_data[i * 4]
                g = pixel_data[i * 4 + 1]
                b = pixel_data[i * 4 + 2]
                if r == 0xFF and b == 0xFF and g == 0x00:
                    pixel_data[i * 4 + 3] = 0x00
                else:
                    pixel_data[i * 4 + 3] = 0xFF

            # Flip rows so GL texture is right-side-up (GL origin = bottom)
            row_size = w * 4
            flipped = bytearray(len(pixel_data))
            for row in range(h):
                src_off = row * row_size
                dst_off = (h - 1 - row) * row_size
                flipped[dst_off:dst_off + row_size] = pixel_data[src_off:src_off + row_size]
            pixel_data = flipped

            tex_id = gl.glGenTextures(1)
            gl.glBindTexture(gl.GL_TEXTURE_2D, tex_id)
            gl.glTexParameteri(
                gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST
            )
            gl.glTexParameteri(
                gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST
            )
            gl.glTexParameteri(
                gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE
            )
            gl.glTexParameteri(
                gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE
            )
            gl.glTexImage2D(
                gl.GL_TEXTURE_2D, 0, gl.GL_RGBA,
                w, h, 0,
                gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, bytes(pixel_data),
            )
            gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
            return (tex_id, w, h)
        except Exception as exc:
            self.message_hud.error(f"BG load error: {exc}")
            return (None, 0, 0)

    # ------------------------------------------------------------------
    # PNG texture loading (pyglet)
    # ------------------------------------------------------------------

    def _load_png_texture(self, path: str) -> None:
        """Load a PNG into a plain GL texture compatible with imgui."""
        try:
            img = pyglet.image.load(path)
            self._png_w = img.width
            self._png_h = img.height

            # Get raw RGBA pixel data
            raw = img.get_image_data()
            fmt = "RGBA"
            pitch = raw.width * 4
            pixel_data = raw.get_data(fmt, pitch)

            # Flip rows so GL texture is right-side-up
            pixel_data = bytearray(pixel_data)
            row_size = self._png_w * 4
            flipped = bytearray(len(pixel_data))
            for row in range(self._png_h):
                src_off = row * row_size
                dst_off = (self._png_h - 1 - row) * row_size
                flipped[dst_off:dst_off + row_size] = pixel_data[src_off:src_off + row_size]

            # Create a plain OpenGL texture
            tex_id = gl.glGenTextures(1)
            gl.glBindTexture(gl.GL_TEXTURE_2D, tex_id)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
            gl.glTexImage2D(
                gl.GL_TEXTURE_2D, 0, gl.GL_RGBA,
                self._png_w, self._png_h, 0,
                gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, bytes(flipped),
            )
            gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

            # Clean up old texture if any
            if self._png_texture_id is not None:
                gl.glDeleteTextures([self._png_texture_id])

            self._png_texture_id = tex_id
        except Exception as exc:
            self.message_hud.error(f"PNG load error: {exc}")
            self._png_texture_id = None

    # ------------------------------------------------------------------
    # Main frame
    # ------------------------------------------------------------------

    def draw_frame(self, win_w: float, win_h: float) -> None:
        io = imgui.get_io()

        # Keyboard shortcuts
        ctrl = io.key_ctrl
        shift = io.key_shift

        # imgui key indices (safe, always < 512)
        key_idx_z = io.key_map[imgui.KEY_Z] if io.key_map[imgui.KEY_Z] >= 0 else -1

        # For keys not in imgui's key_map we clamp to buffer size
        _KD_LEN = 512

        def _is_down(pyglet_key: int) -> bool:
            return pyglet_key < _KD_LEN and io.keys_down[pyglet_key]

        key_f = pyglet.window.key.F
        key_z = pyglet.window.key.Z
        key_s = pyglet.window.key.S

        self._ctrl_f_held = ctrl and _is_down(key_f)

        if ctrl and key_idx_z >= 0 and imgui.is_key_pressed(key_idx_z):
            if shift:
                self.redo()
            else:
                self.undo()
        if ctrl and _is_down(key_s):
            self.save()

        # Arrow key panning — use imgui mapped arrow keys
        pan_speed = 16.0
        arrow_up = io.key_map[imgui.KEY_UP_ARROW]
        arrow_down = io.key_map[imgui.KEY_DOWN_ARROW]
        arrow_left = io.key_map[imgui.KEY_LEFT_ARROW]
        arrow_right = io.key_map[imgui.KEY_RIGHT_ARROW]

        def _arrow_down_check(mapped_key: int) -> bool:
            return mapped_key >= 0 and mapped_key < _KD_LEN and io.keys_down[mapped_key]

        if ctrl:
            # Ctrl + Up/Down = zoom
            if _arrow_down_check(arrow_up):
                self._zoom = min(8.0, self._zoom * 1.05)
            if _arrow_down_check(arrow_down):
                self._zoom = max(0.125, self._zoom / 1.05)
        else:
            if _arrow_down_check(arrow_up):
                self._pan_y -= pan_speed
            if _arrow_down_check(arrow_down):
                self._pan_y += pan_speed
            if _arrow_down_check(arrow_left):
                self._pan_x -= pan_speed
            if _arrow_down_check(arrow_right):
                self._pan_x += pan_speed

        # Mouse wheel: Ctrl = zoom, Shift = horizontal pan, else vertical pan
        wheel = io.mouse_wheel
        if wheel != 0:
            if ctrl:
                factor = 1.1 if wheel > 0 else 1.0 / 1.1
                self._zoom = max(0.125, min(8.0, self._zoom * factor))
            elif shift:
                self._pan_x -= wheel * 40.0
            else:
                self._pan_y -= wheel * 40.0

        # Left panel – file browser (resizable via drag on right edge)
        left_w = self.left_panel_w
        imgui.set_next_window_position(0, 0)
        imgui.set_next_window_size(left_w, win_h - self.message_hud.panel_height)
        imgui.begin(
            "Files##file_browser",
            closable=False,
            flags=(
                imgui.WINDOW_NO_MOVE
                | imgui.WINDOW_NO_SAVED_SETTINGS
            ),
        )
        # Detect resize from imgui
        new_left_w = imgui.get_window_width()
        if new_left_w != left_w:
            self.left_panel_w = max(100, min(win_w * 0.4, new_left_w))
        if os.path.isdir(ASSET_UI_ROOT):
            self.file_browser._draw_dir(
                self.file_browser.root_dir,
                self.on_open_xml,
                self.on_open_png,
            )
        else:
            imgui.text_colored("(missing assets/ui)", 1, 0.3, 0.3)
        imgui.end()

        # Right panels
        right_w = self.right_panel_w
        msg_h = self.message_hud.panel_height
        half_h = (win_h - msg_h) * 0.5

        # Tool HUD (top-right, resizable width)
        imgui.set_next_window_position(win_w - right_w, 0)
        imgui.set_next_window_size(right_w, half_h)
        active_tool = self.tool_hud.draw_with_pick_capture(win_w, win_h, right_w)

        # Properties HUD (bottom-right)
        imgui.set_next_window_position(win_w - right_w, half_h)
        imgui.set_next_window_size(right_w, half_h)
        self.properties_hud.draw(
            win_w, win_h, right_w,
            on_change=self.on_property_changed,
        )

        # Central work area
        work_x = self.left_panel_w
        work_y = 0.0
        work_region_w = win_w - self.left_panel_w - right_w
        work_region_h = win_h - msg_h

        imgui.set_next_window_position(work_x, work_y)
        imgui.set_next_window_size(work_region_w, work_region_h)
        flags = (
            imgui.WINDOW_NO_TITLE_BAR
            | imgui.WINDOW_NO_RESIZE
            | imgui.WINDOW_NO_MOVE
            | imgui.WINDOW_NO_SAVED_SETTINGS
        )
        imgui.begin("##work_area_window", closable=False, flags=flags)

        cursor_pos = imgui.get_cursor_screen_position()
        origin_x = cursor_pos[0] + self._pan_x
        origin_y = cursor_pos[1] + self._pan_y

        if self._png_texture_id is not None and self._xml_root is None:
            self.work_area.draw_png_preview(
                self._png_texture_id,
                int(self._png_w * self._zoom),
                int(self._png_h * self._zoom),
                origin_x,
                origin_y,
            )
        elif self._xml_root is not None:
            self.work_area.draw(
                elements=self._elements,
                root=self._xml_root,
                active_tool=active_tool,
                span_configs=self.tool_hud._span_configs if hasattr(self.tool_hud, '_span_configs') else {},
                work_w=self.work_w,
                work_h=self.work_h,
                origin_x=origin_x,
                origin_y=origin_y,
                on_select=self.on_select_element,
                on_delete=self.on_delete_element,
                on_create=self.on_create_element,
                ctrl_f_held=self._ctrl_f_held,
                backgrounds=self._bg_textures,
                zoom=self._zoom,
            )
            imgui.dummy(
                int(self.work_w * self._zoom),
                int(self.work_h * self._zoom),
            )
        else:
            imgui.text("Open a file from the left panel.")

        imgui.end()

        # Bottom message HUD
        self.message_hud.draw(win_w, win_h)


# ===================================================================
# pyglet + imgui bootstrap
# ===================================================================

def main() -> None:
    window = pyglet.window.Window(
        width=DEFAULT_WINDOW_W,
        height=DEFAULT_WINDOW_H,
        resizable=True,
        caption="Lavender UI Editor",
    )

    imgui.create_context()
    renderer = PygletRenderer(window)

    app = EditorApp()
    app.message_hud.info("Welcome to the Lavender UI Editor.")

    @window.event
    def on_draw():
        window.clear()
        imgui.new_frame()
        app.draw_frame(float(window.width), float(window.height))
        imgui.render()
        renderer.render(imgui.get_draw_data())

    @window.event
    def on_close():
        renderer.shutdown()

    pyglet.app.run()


if __name__ == "__main__":
    main()
