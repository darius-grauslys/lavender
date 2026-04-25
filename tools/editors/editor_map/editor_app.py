"""
Main editor application for editor_map.

Ties together all modules: modes, tools, workspace, keybinds,
message HUD, file hierarchy, and properties panels.

Uses Dear ImGui via pyimgui.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import List, Optional

import imgui
from imgui.integrations.glfw import GlfwRenderer
import glfw
import OpenGL.GL as gl
import ctypes

# Ensure editor_map package root is on sys.path
_editor_map_dir = str(Path(__file__).resolve().parent)
if _editor_map_dir not in sys.path:
    sys.path.insert(0, _editor_map_dir)

from keybinds.keybind import (
    KeyCombo, Modifier,
    VIRTUAL_KEY_SCROLL_UP, VIRTUAL_KEY_SCROLL_DOWN,
    VIRTUAL_KEY_ZOOM_IN, VIRTUAL_KEY_ZOOM_OUT,
)
from keybinds.keybind_manager import KeybindManager
from modes.editor_mode import EditorMode
from modes.global_space_view import GlobalSpaceViewMode
from modes.chunk_edit import ChunkEditMode
from modes.entity_edit import EntityEditMode
from modes.inventory_edit import InventoryEditMode
from workspace.movement import WorkspaceMovement
from workspace.objects import WorkspaceObjects
from workspace.render import WorkspaceRenderer
from core.engine_config import EngineConfig, load_engine_config
from core.tile_parser import (
    parse_tile_header_from_file, TileInfo, TileParseError, TileLayerLayout,
)
from core.c_enum import parse_c_enum_from_file, find_enum_by_name, CEnum
from core.world_directory import list_worlds, ensure_world_dir, world_root
from core.editor_project_config import (
    EditorProjectConfig,
    WorldEditorConfig,
    load_editor_project_config,
    save_editor_project_config,
    load_world_editor_config,
    save_world_editor_config,
)
from core.tilesheet import Tilesheet, load_tilesheet
from core.tilesheet_browser import browse_and_set_tilesheet, clear_tilesheet
from ui.message_hud import MessageHUD

VERSION = "0.1.0"


class EditorApp:
    """Main editor application."""

    def __init__(
            self,
            engine_dir: Path,
            project_dir: Optional[Path] = None):
        self._engine_dir = engine_dir
        self._project_dir = project_dir or Path(".")

        # Core systems
        self._keybind_manager = KeybindManager()
        self._message_hud = MessageHUD()
        self._config: Optional[EngineConfig] = None
        self._tile_info: Optional[TileInfo] = None
        self._tile_enums: List[CEnum] = []
        self._editor_project_config: Optional[EditorProjectConfig] = None
        self._tilesheet: Optional[Tilesheet] = None
        self._tilesheet_rendering_enabled: bool = False

        # GL texture for tilesheet
        self._tilesheet_texture_id: int = 0

        # Workspace
        self._movement = WorkspaceMovement()
        self._objects: Optional[WorkspaceObjects] = None
        self._renderer: Optional[WorkspaceRenderer] = None

        # Modes
        self._modes: List[EditorMode] = []
        self._active_mode_index: int = 0

        # File hierarchy
        self._worlds: List[str] = []
        self._active_world: Optional[str] = None
        self._active_world_config: Optional[WorldEditorConfig] = None
        self._new_world_name: str = ""
        self._new_tilesheet_path: str = ""
        self._delete_confirm_name: str = ""
        self._delete_target: Optional[str] = None

        # UI state
        self._properties_width: float = 250.0
        self._tool_hud_width: float = 250.0
        self._file_hierarchy_width: float = 200.0

    def initialize(self) -> None:
        """Load config, parse types, set up modes."""
        self._message_hud.system(f"editor_map v{VERSION}")

        # Load engine config
        defaults_path = (
            self._engine_dir / 'core' / 'include' / 'platform_defaults.h')
        project_config_path = (
            self._project_dir / 'include' / 'config' / 'implemented'
            / 'engine_config.h')
        if not defaults_path.exists():
            self._message_hud.error(
                f"Engine platform_defaults.h not found at "
                f"'{defaults_path}'. Engine constants will use "
                f"hardcoded fallbacks.")
        if not project_config_path.exists():
            self._message_hud.info(
                f"No project engine_config.h override found at "
                f"'{project_config_path}' — using engine defaults only.")
        self._config = load_engine_config(
            self._engine_dir, self._project_dir)
        self._message_hud.info(
            f"Engine config: chunk={self._config.chunk_width}x"
            f"{self._config.chunk_height}x{self._config.chunk_depth}")

        # Parse tile header
        tile_h = self._project_dir / "include" / "types" / "implemented" / "world" / "tile.h"
        tile_result = parse_tile_header_from_file(tile_h)
        if isinstance(tile_result, TileParseError):
            self._tile_info = None
            self._message_hud.error(
                f"Project is Under Defined: {tile_result.message}")
        else:
            self._tile_info = tile_result
            self._message_hud.info(
                f"Tile size: {self._tile_info.size_in_bytes} bytes, "
                f"{len(self._tile_info.layer_fields)} layer(s)")
            for i, layout in enumerate(self._tile_info.layer_layouts):
                lf = self._tile_info.layer_fields[i] \
                    if i < len(self._tile_info.layer_fields) else None
                layer_name = lf.field_name if lf else f"layer_{i}"
                self._message_hud.info(
                    f"  Layer '{layer_name}': "
                    f"logic={layout.logic_bits}b, "
                    f"anim={layout.animation_bits}b, "
                    f"remainder={layout.remainder_bits}b")
            # Load enums for each tile layer
            for lf in self._tile_info.layer_fields:
                enum = self._find_project_enum(lf.enum_type_name)
                if enum:
                    self._tile_enums.append(enum)
                    self._message_hud.info(
                        f"Loaded tile enum: {enum.name} "
                        f"({len(enum.members)} members)")
                else:
                    self._message_hud.error(
                        f"Failed to load tile enum '{lf.enum_type_name}' "
                        f"for tile layer field '{lf.field_name}' "
                        f"(bit width {lf.bit_width}). "
                        f"Searched project headers in "
                        f"'{self._project_dir / 'include' / 'types' / 'implemented'}' "
                        f"and engine headers in "
                        f"'{self._engine_dir / 'core' / 'include' / 'types' / 'implemented'}'. "
                        f"Ensure a header defines: "
                        f"typedef enum ... {{ ... }} {lf.enum_type_name};")

        # Load editor project config and tilesheet
        self._editor_project_config = load_editor_project_config(
            self._project_dir)
        self._load_tilesheet()

        # Initialize workspace
        self._objects = WorkspaceObjects(self._config)
        self._renderer = WorkspaceRenderer(self._config)
        if self._tilesheet:
            self._renderer.set_tilesheet(self._tilesheet)
        if self._tile_info:
            self._renderer.set_tile_info(self._tile_info)

        # Initialize modes — inject movement so tools can register
        # keybind callbacks that drive the viewport.
        cfg_cw = self._config.chunk_width if self._config else 8
        cfg_ch = self._config.chunk_height if self._config else 8
        gs_mode = GlobalSpaceViewMode(
            self._keybind_manager,
            movement=self._movement,
            gs_width=cfg_cw,
            gs_height=cfg_ch)
        chunk_mode = ChunkEditMode(
            self._keybind_manager,
            movement=self._movement,
            chunk_w=cfg_cw,
            chunk_h=cfg_ch)
        if self._tile_enums:
            chunk_mode.set_tile_enums(self._tile_enums)
        if self._tile_info:
            chunk_mode.set_layer_info(
                self._tile_info.layer_fields,
                self._tile_info.layer_layouts)
        chunk_mode.set_project_dir(self._project_dir)
        chunk_mode.set_on_enum_updated(self._reload_tile_enums)
        if self._tilesheet:
            chunk_mode.set_active_tilesheet(self._tilesheet)
            chunk_mode.set_tilesheet_texture_id(
                self._tilesheet_texture_id)
        entity_mode = EntityEditMode(
            self._keybind_manager, movement=self._movement)
        inv_mode = InventoryEditMode(
            self._keybind_manager, movement=self._movement)

        self._modes = [gs_mode, chunk_mode, entity_mode, inv_mode]

        # Set base keybinds
        self._setup_base_keybinds()

        # Activate first mode
        if self._modes:
            self._modes[0].on_activate()

        # Load world list
        self._refresh_worlds()

    def _load_tilesheet(self) -> None:
        """Load the tilesheet from the active world's editor config."""
        if not self._active_world_config:
            # No world selected — check if there's a legacy project config
            if (self._editor_project_config
                    and self._editor_project_config.tilesheet_path):
                self._message_hud.warning(
                    "No world selected. Tilesheet is configured "
                    "per-world. Select a world to load its tilesheet.")
            else:
                self._message_hud.warning(
                    "No tilesheet configured. "
                    "Select a world and set its tilesheet path.")
            self._tilesheet_rendering_enabled = False
            return

        resolved = self._active_world_config.resolve_tilesheet(
            self._project_dir)
        if resolved:
            self._tilesheet = load_tilesheet(resolved)
            if self._tilesheet:
                self._tilesheet_rendering_enabled = True
                self._message_hud.info(
                    f"Tilesheet loaded: {resolved} "
                    f"({self._tilesheet.width}x{self._tilesheet.height}, "
                    f"{self._tilesheet.total_tiles} tiles)")
                self._upload_tilesheet_texture()
            else:
                self._tilesheet_rendering_enabled = False
                self._message_hud.error(
                    f"Failed to load tilesheet image at '{resolved}'. "
                    f"Ensure PIL/Pillow or pypng is installed.")
        else:
            path_str = self._active_world_config.tilesheet_path
            if path_str:
                self._message_hud.error(
                    f"Tilesheet not found at "
                    f"'{self._project_dir / path_str}'. "
                    f"Tile rendering disabled.")
            else:
                self._message_hud.warning(
                    "No tilesheet configured for this world. "
                    "Use the tilesheet path field to set one.")
            self._tilesheet_rendering_enabled = False

    def _upload_tilesheet_texture(self) -> None:
        """Upload the current tilesheet pixel data to an OpenGL texture."""
        # Delete old texture if any
        if self._tilesheet_texture_id != 0:
            gl.glDeleteTextures(1, [self._tilesheet_texture_id])
            self._tilesheet_texture_id = 0

        if self._tilesheet is None:
            return

        ts = self._tilesheet
        if ts.width <= 0 or ts.height <= 0 or not ts.pixels:
            self._message_hud.error(
                "Tilesheet has invalid dimensions or empty pixel data.")
            return

        try:
            tex_id = gl.glGenTextures(1)
            gl.glBindTexture(gl.GL_TEXTURE_2D, tex_id)
            gl.glTexParameteri(
                gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER,
                gl.GL_NEAREST)
            gl.glTexParameteri(
                gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER,
                gl.GL_NEAREST)
            gl.glTexParameteri(
                gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S,
                gl.GL_CLAMP_TO_EDGE)
            gl.glTexParameteri(
                gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T,
                gl.GL_CLAMP_TO_EDGE)
            gl.glTexImage2D(
                gl.GL_TEXTURE_2D, 0, gl.GL_RGBA,
                ts.width, ts.height, 0,
                gl.GL_RGBA, gl.GL_UNSIGNED_BYTE,
                ts.pixels)
            gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
            self._tilesheet_texture_id = int(tex_id)
            self._message_hud.info(
                f"Tilesheet GL texture created (id={tex_id}, "
                f"{ts.width}x{ts.height}).")
        except Exception as e:
            self._message_hud.error(
                f"Failed to create GL texture for tilesheet: {e}")
            self._tilesheet_texture_id = 0

    def _reload_tile_enums(self) -> None:
        """Reload tile enums after editing."""
        self._tile_enums.clear()
        if self._tile_info:
            for lf in self._tile_info.layer_fields:
                enum = self._find_project_enum(lf.enum_type_name)
                if enum:
                    self._tile_enums.append(enum)
            chunk_mode = self._modes[1]  # ChunkEditMode
            if hasattr(chunk_mode, 'set_tile_enums'):
                chunk_mode.set_tile_enums(self._tile_enums)
        self._message_hud.info("Tile enums reloaded.")

    def _find_project_enum(self, type_name: str) -> Optional[CEnum]:
        """Search project headers for an enum by type name."""
        # Search in project include/types/implemented/world/
        search_dir = self._project_dir / "include" / "types" / "implemented" / "world"
        if search_dir.is_dir():
            for header in search_dir.glob("*.h"):
                enums = parse_c_enum_from_file(header)
                found = find_enum_by_name(enums, type_name)
                if found:
                    return found

        # Also search entity types
        search_dir = self._project_dir / "include" / "types" / "implemented" / "entity"
        if search_dir.is_dir():
            for header in search_dir.glob("*.h"):
                enums = parse_c_enum_from_file(header)
                found = find_enum_by_name(enums, type_name)
                if found:
                    return found

        # Fallback: engine defaults
        search_dir = self._engine_dir / "core" / "include" / "types" / "implemented"
        if search_dir.is_dir():
            for header in search_dir.rglob("*.h"):
                enums = parse_c_enum_from_file(header)
                found = find_enum_by_name(enums, type_name)
                if found:
                    return found

        return None

    def _setup_base_keybinds(self) -> None:
        """Set up base keybinds that are always active."""
        base = {
            KeyCombo(glfw.KEY_M, Modifier.CTRL): self._toggle_message_hud,
            KeyCombo(glfw.KEY_H, Modifier.CTRL): self._print_keybind_help,
            KeyCombo(glfw.KEY_G, Modifier.CTRL): lambda: self._switch_mode(0),
            KeyCombo(glfw.KEY_K, Modifier.CTRL): lambda: self._switch_mode(1),
            KeyCombo(glfw.KEY_E, Modifier.CTRL): lambda: self._switch_mode(2),
            KeyCombo(glfw.KEY_I, Modifier.CTRL): lambda: self._switch_mode(3),
        }
        # Tool selection: Shift+N for tools 0-9
        for n in range(10):
            key = glfw.KEY_0 + n
            idx = n
            base[KeyCombo(key, Modifier.SHIFT)] = \
                lambda i=idx: self._select_tool(i)

        self._keybind_manager.set_base_keybinds(base)

    def _toggle_message_hud(self) -> None:
        self._message_hud._collapsed = not self._message_hud._collapsed

    def _print_keybind_help(self) -> None:
        active = self._keybind_manager.get_all_active_binds()
        self._message_hud.system("=== Active Keybinds ===")
        for combo, cb in sorted(active.items(), key=lambda x: (int(x[0].modifiers), x[0].key)):
            mod_str = ""
            if combo.modifiers & Modifier.CTRL:
                mod_str += "Ctrl+"
            if combo.modifiers & Modifier.SHIFT:
                mod_str += "Shift+"
            if combo.modifiers & Modifier.ALT:
                mod_str += "Alt+"
            key_name = _key_name(combo.key)
            name = getattr(cb, '__name__', str(cb))
            self._message_hud.system(f"  {mod_str}{key_name}: {name}")

    def _switch_mode(self, index: int) -> None:
        if index == self._active_mode_index:
            return
        if 0 <= index < len(self._modes):
            self._modes[self._active_mode_index].on_deactivate()
            self._active_mode_index = index
            self._modes[index].on_activate()
            self._message_hud.info(
                f"Switched to: {self._modes[index].name}")

    def _select_tool(self, index: int) -> None:
        mode = self._modes[self._active_mode_index]
        if 0 <= index < len(mode.tools):
            mode.select_tool(index)

    def _refresh_worlds(self) -> None:
        self._worlds = list_worlds(self._project_dir)

    # -- Drawing ---

    def draw(self) -> None:
        """Draw the entire editor UI. Called each frame."""
        display_size = imgui.get_io().display_size
        w, h = display_size.x, display_size.y

        self._process_keybinds()
        self._draw_mode_tabs(w)
        self._draw_file_hierarchy(h)
        self._draw_tool_hud(w, h)
        self._draw_properties_hud(w, h)
        self._draw_workspace(w, h)
        self._message_hud.draw(w, h)

    def _process_keybinds(self) -> None:
        """Check for keybind activations this frame.

        Physical key presses and virtual scroll/zoom events are
        all routed through the keybind manager so that tools and
        modes can override behaviour via push_override/pop_override.
        """
        io = imgui.get_io()

        # Build current modifier mask
        mods = Modifier.NONE
        if io.key_ctrl:
            mods |= Modifier.CTRL
        if io.key_shift:
            mods |= Modifier.SHIFT
        if io.key_alt:
            mods |= Modifier.ALT

        # --- Physical key presses ---
        # When an imgui widget wants the keyboard (e.g. text input),
        # only allow Ctrl-modified combos (mode switches, etc.)
        # through.  Unmodified keys are suppressed so they don't
        # interfere with text editing.
        if not io.want_capture_keyboard or io.key_ctrl:
            for key in range(glfw.KEY_SPACE, glfw.KEY_LAST + 1):
                if imgui.is_key_pressed(key):
                    combo = KeyCombo(key, mods)
                    self._keybind_manager.fire(combo)

        # --- Virtual scroll / zoom events ---
        # These are generated from the mouse scroll wheel and
        # dispatched as virtual key combos so that tools can
        # override scroll behaviour via the keybind stack.
        if io.mouse_wheel != 0 and not io.want_capture_mouse:
            has_alt = bool(mods & Modifier.ALT)
            has_shift = bool(mods & Modifier.SHIFT)

            if has_alt and has_shift:
                # Alt+Shift + scroll → zoom
                if io.mouse_wheel > 0:
                    self._keybind_manager.fire(
                        KeyCombo(VIRTUAL_KEY_ZOOM_IN,
                                 Modifier.ALT | Modifier.SHIFT))
                else:
                    self._keybind_manager.fire(
                        KeyCombo(VIRTUAL_KEY_ZOOM_OUT,
                                 Modifier.ALT | Modifier.SHIFT))
            elif has_shift:
                # Shift + scroll → horizontal pan
                if io.mouse_wheel > 0:
                    self._keybind_manager.fire(
                        KeyCombo(VIRTUAL_KEY_SCROLL_UP, Modifier.SHIFT))
                else:
                    self._keybind_manager.fire(
                        KeyCombo(VIRTUAL_KEY_SCROLL_DOWN, Modifier.SHIFT))
            else:
                # Scroll → vertical pan
                if io.mouse_wheel > 0:
                    self._keybind_manager.fire(
                        KeyCombo(VIRTUAL_KEY_SCROLL_UP, Modifier.NONE))
                else:
                    self._keybind_manager.fire(
                        KeyCombo(VIRTUAL_KEY_SCROLL_DOWN, Modifier.NONE))

    def _draw_mode_tabs(self, window_width: float) -> None:
        """Draw the mode tab bar at the top."""
        imgui.set_next_window_position(0, 0)
        imgui.set_next_window_size(window_width, 30)
        flags = (
            imgui.WINDOW_NO_MOVE
            | imgui.WINDOW_NO_RESIZE
            | imgui.WINDOW_NO_TITLE_BAR
            | imgui.WINDOW_NO_SAVED_SETTINGS
        )
        imgui.begin("##mode_tabs", flags=flags)
        for i, mode in enumerate(self._modes):
            if i > 0:
                imgui.same_line()
            selected = (i == self._active_mode_index)
            if selected:
                imgui.push_style_color(imgui.COLOR_BUTTON, 0.3, 0.5, 0.8, 1.0)
            if imgui.button(f"{mode.name} ({mode.shortcut_label})##{i}"):
                self._switch_mode(i)
            if selected:
                imgui.pop_style_color()
        imgui.end()

    def _draw_file_hierarchy(self, window_height: float) -> None:
        """Draw the file hierarchy HUD on the left."""
        msg_h = self._message_hud.panel_height
        top = 30.0
        h = window_height - top - msg_h

        imgui.set_next_window_position(0, top)
        imgui.set_next_window_size(self._file_hierarchy_width, h)
        flags = (
            imgui.WINDOW_NO_MOVE
            | imgui.WINDOW_NO_SAVED_SETTINGS
        )
        imgui.begin("File Hierarchy##fh", flags=flags)
        self._file_hierarchy_width = max(100, imgui.get_window_width())

        imgui.text("Worlds:")
        imgui.separator()

        imgui.begin_child("##world_list", 0, -60, border=True)
        for world_name in self._worlds:
            selected = (world_name == self._active_world)
            if imgui.selectable(world_name, selected)[0]:
                self._active_world = world_name
                self._active_world_config = load_world_editor_config(
                    self._project_dir, world_name)
                self._new_tilesheet_path = (
                    self._active_world_config.tilesheet_path)
                self._message_hud.info(f"Selected world: {world_name}")
                self._load_tilesheet()
                if self._tilesheet and self._renderer:
                    self._renderer.set_tilesheet(self._tilesheet)
                self._update_chunk_mode_tilesheet()
            imgui.same_line(imgui.get_window_width() - 30)
            if imgui.small_button(f"X##{world_name}"):
                self._delete_target = world_name
                self._delete_confirm_name = ""
        imgui.end_child()

        # Delete confirmation
        if self._delete_target:
            imgui.text(f"Type '{self._delete_target}' to confirm:")
            _, self._delete_confirm_name = imgui.input_text(
                "##del_confirm", self._delete_confirm_name, 64)
            if imgui.button("OK##del"):
                if self._delete_confirm_name == self._delete_target:
                    import shutil
                    target = world_root(self._project_dir, self._delete_target)
                    if target.exists():
                        shutil.rmtree(target)
                    self._refresh_worlds()
                    if self._active_world == self._delete_target:
                        self._active_world = None
                        self._active_world_config = None
                        self._new_tilesheet_path = ""
                    self._message_hud.info(
                        f"Deleted world: {self._delete_target}")
                self._delete_target = None
            imgui.same_line()
            if imgui.button("Cancel##del"):
                self._delete_target = None

        # Add new world
        imgui.separator()
        _, self._new_world_name = imgui.input_text(
            "##new_world", self._new_world_name, 64)
        imgui.same_line()
        if imgui.button("+##add_world"):
            if self._new_world_name.strip():
                if not self._tile_info:
                    self._message_hud.error(
                        "Cannot create world: project is Under Defined. "
                        "The tile header at "
                        f"'{self._project_dir / 'include' / 'types' / 'implemented' / 'world' / 'tile.h'}' "
                        "could not be parsed. See earlier error messages "
                        "for details.")
                else:
                    ensure_world_dir(
                        self._project_dir, self._new_world_name.strip())
                    self._refresh_worlds()
                    self._message_hud.info(
                        f"Created world: {self._new_world_name.strip()}")
                    self._new_world_name = ""

        # Per-world tilesheet path (below new-world controls)
        imgui.separator()
        imgui.text("Tilesheet:")
        has_world = self._active_world is not None
        if not has_world:
            imgui.push_style_var(imgui.STYLE_ALPHA, 0.5)
            imgui.input_text(
                "##ts_path", "(no world selected)", 256,
                imgui.INPUT_TEXT_READ_ONLY)
            imgui.button("Browse...##ts_browse")
            imgui.same_line()
            imgui.button("Clear##ts_clear")
            imgui.pop_style_var()
        else:
            display_path = (
                self._new_tilesheet_path
                if self._new_tilesheet_path
                else "(none)")
            imgui.input_text(
                "##ts_path", display_path, 256,
                imgui.INPUT_TEXT_READ_ONLY)
            if imgui.button("Browse...##ts_browse"):
                rel_path, tilesheet = browse_and_set_tilesheet(
                    self._project_dir,
                    self._active_world,
                    self._message_hud)
                if rel_path is not None:
                    self._new_tilesheet_path = rel_path
                    self._active_world_config = load_world_editor_config(
                        self._project_dir, self._active_world)
                    self._tilesheet = tilesheet
                    self._tilesheet_rendering_enabled = tilesheet is not None
                    if self._tilesheet:
                        self._upload_tilesheet_texture()
                        if self._renderer:
                            self._renderer.set_tilesheet(self._tilesheet)
                    else:
                        # Clear old texture if load failed
                        if self._tilesheet_texture_id != 0:
                            gl.glDeleteTextures(
                                1, [self._tilesheet_texture_id])
                            self._tilesheet_texture_id = 0
                    # Update chunk edit mode with new tilesheet
                    self._update_chunk_mode_tilesheet()
            imgui.same_line()
            if imgui.button("Clear##ts_clear"):
                clear_tilesheet(
                    self._project_dir,
                    self._active_world,
                    self._message_hud)
                self._new_tilesheet_path = ""
                self._active_world_config = load_world_editor_config(
                    self._project_dir, self._active_world)
                self._tilesheet = None
                self._tilesheet_rendering_enabled = False
                if self._tilesheet_texture_id != 0:
                    gl.glDeleteTextures(
                        1, [self._tilesheet_texture_id])
                    self._tilesheet_texture_id = 0
                self._update_chunk_mode_tilesheet()

        imgui.end()

    def _draw_tool_hud(self, window_width: float, window_height: float) -> None:
        """Draw the Tool HUD on the right side."""
        msg_h = self._message_hud.panel_height
        top = 30.0
        h = (window_height - top - msg_h) * 0.5

        imgui.set_next_window_position(
            window_width - self._tool_hud_width, top)
        imgui.set_next_window_size(self._tool_hud_width, h)
        flags = (
            imgui.WINDOW_NO_MOVE
            | imgui.WINDOW_NO_SAVED_SETTINGS
        )
        imgui.begin("Toolkit##toolkit", flags=flags)
        self._tool_hud_width = max(150, imgui.get_window_width())

        mode = self._modes[self._active_mode_index]

        # Tool grid (5-wide)
        imgui.text("Tools:")
        col = 0
        for i, tool in enumerate(mode.tools):
            is_active = (i == mode._active_tool_index)
            if is_active:
                imgui.push_style_color(
                    imgui.COLOR_BUTTON, 0.3, 0.6, 0.9, 1.0)
            if imgui.button(f"{tool.icon_label}##{i}", width=40, height=40):
                mode.select_tool(i)
            if imgui.is_item_hovered():
                imgui.set_tooltip(tool.name)
            if is_active:
                imgui.pop_style_color()
            col += 1
            if col < 5 and i < len(mode.tools) - 1:
                imgui.same_line()
            else:
                col = 0

        imgui.separator()
        imgui.text("Tool Properties:")
        mode.draw_tool_properties()

        imgui.end()

    def _draw_properties_hud(
            self, window_width: float, window_height: float) -> None:
        """Draw the Properties HUD below the Tool HUD."""
        msg_h = self._message_hud.panel_height
        top = 30.0
        tool_h = (window_height - top - msg_h) * 0.5
        props_top = top + tool_h
        props_h = window_height - props_top - msg_h

        imgui.set_next_window_position(
            window_width - self._tool_hud_width, props_top)
        imgui.set_next_window_size(self._tool_hud_width, props_h)
        flags = (
            imgui.WINDOW_NO_MOVE
            | imgui.WINDOW_NO_SAVED_SETTINGS
        )
        imgui.begin("Properties##props", flags=flags)

        mode = self._modes[self._active_mode_index]
        tool = mode.active_tool
        if tool and hasattr(tool, 'selection') and tool.selection:
            imgui.text(f"Selected: {len(tool.selection)} item(s)")
            # TODO: derive property fields from engine source per spec 1.3.1
            imgui.text("(Property fields TBD)")
        else:
            imgui.text("No selection.")

        imgui.end()

    def _draw_workspace(
            self, window_width: float, window_height: float) -> None:
        """Draw the main workspace area."""
        msg_h = self._message_hud.panel_height
        top = 30.0
        left = self._file_hierarchy_width
        right = self._tool_hud_width
        ws_w = window_width - left - right
        ws_h = window_height - top - msg_h

        imgui.set_next_window_position(left, top)
        imgui.set_next_window_size(ws_w, ws_h)
        flags = (
            imgui.WINDOW_NO_MOVE
            | imgui.WINDOW_NO_RESIZE
            | imgui.WINDOW_NO_TITLE_BAR
            | imgui.WINDOW_NO_SAVED_SETTINGS
            | imgui.WINDOW_NO_SCROLLBAR
        )
        imgui.begin("##workspace", flags=flags)

        # Workspace screen-space bounds
        win_pos = imgui.get_window_position()
        ws_ox, ws_oy = win_pos.x, win_pos.y

        # Draw chunk grid lines
        draw_list = imgui.get_window_draw_list()
        ws_chunk_w = self._config.chunk_width if self._config else 8
        ws_chunk_h = self._config.chunk_height if self._config else 8
        (first_vx, vstep,
         first_hy, hstep,
         _gl, _gt) = self._movement.get_chunk_grid_params(
            ws_ox, ws_oy, ws_w, ws_h, ws_chunk_w, ws_chunk_h)

        grid_col = imgui.get_color_u32_rgba(0.3, 0.3, 0.3, 0.4)
        if vstep > 0:
            x = first_vx
            while x <= ws_ox + ws_w:
                if x >= ws_ox:
                    draw_list.add_line(
                        x, ws_oy, x, ws_oy + ws_h, grid_col)
                x += vstep
        if hstep > 0:
            y = first_hy
            while y <= ws_oy + ws_h:
                if y >= ws_oy:
                    draw_list.add_line(
                        ws_ox, y, ws_ox + ws_w, y, grid_col)
                y += hstep

        # Draw mode-specific content
        mode = self._modes[self._active_mode_index]
        mode.draw_workspace(None)

        # Coordinate overlay: show hovered tile position
        hover_tile_text = ""
        if imgui.is_window_hovered():
            mouse = imgui.get_mouse_position()
            tile_x, tile_y = self._movement.screen_to_tile(
                mouse.x, mouse.y, ws_ox, ws_oy, ws_w, ws_h)
            tile_z = self._movement.viewport.center_z
            # Chunk coordinates
            cx = math.floor(tile_x / ws_chunk_w)
            cy = math.floor(tile_y / ws_chunk_h)
            # Local tile within chunk
            lx = tile_x - cx * ws_chunk_w
            ly = tile_y - cy * ws_chunk_h
            # Show Z axis only when chunk depth > 1 (3D voxel world)
            chunk_depth = self._config.chunk_depth if self._config else 1
            if chunk_depth > 1:
                hover_tile_text = (
                    f"Tile: ({tile_x}, {tile_y}, {tile_z})  "
                    f"Chunk: ({cx}, {cy})  "
                    f"Local: ({lx}, {ly})  "
                    f"Z: {tile_z}")
            else:
                hover_tile_text = (
                    f"Tile: ({tile_x}, {tile_y})  "
                    f"Chunk: ({cx}, {cy})  "
                    f"Local: ({lx}, {ly})")

        if hover_tile_text:
            # Draw overlay text with dark background for readability
            text_x = ws_ox + 8
            text_y = ws_oy + 4
            text_size = imgui.calc_text_size(hover_tile_text)
            bg_col = imgui.get_color_u32_rgba(0.0, 0.0, 0.0, 0.7)
            fg_col = imgui.get_color_u32_rgba(1.0, 1.0, 1.0, 1.0)
            draw_list.add_rect_filled(
                text_x - 2, text_y - 1,
                text_x + text_size.x + 4,
                text_y + text_size.y + 2,
                bg_col, 3.0)
            draw_list.add_text(
                text_x, text_y, fg_col, hover_tile_text)

        # Workspace input (scroll, arrow keys, zoom) is handled
        # entirely through the keybind manager — see
        # _process_keybinds() which translates raw input into
        # virtual key combos and fires them through the stack.

        imgui.end()


    def _update_chunk_mode_tilesheet(self) -> None:
        """Push the active tilesheet and GL texture to the chunk edit mode."""
        if len(self._modes) > 1:
            chunk_mode = self._modes[1]
            if hasattr(chunk_mode, 'set_active_tilesheet'):
                chunk_mode.set_active_tilesheet(self._tilesheet)
            if hasattr(chunk_mode, 'set_tilesheet_texture_id'):
                chunk_mode.set_tilesheet_texture_id(
                    self._tilesheet_texture_id)


def _key_name(key: int) -> str:
    """Convert a GLFW key constant to a readable name."""
    names = {
        glfw.KEY_SPACE: "Space",
        glfw.KEY_ESCAPE: "Escape",
        glfw.KEY_ENTER: "Enter",
        glfw.KEY_TAB: "Tab",
        glfw.KEY_BACKSPACE: "Backspace",
        glfw.KEY_DELETE: "Delete",
        glfw.KEY_UP: "Up",
        glfw.KEY_DOWN: "Down",
        glfw.KEY_LEFT: "Left",
        glfw.KEY_RIGHT: "Right",
    }
    if key in names:
        return names[key]
    if glfw.KEY_A <= key <= glfw.KEY_Z:
        return chr(ord('A') + key - glfw.KEY_A)
    if glfw.KEY_0 <= key <= glfw.KEY_9:
        return chr(ord('0') + key - glfw.KEY_0)
    return f"Key({key})"


def run_editor(engine_dir: str, project_dir: str = ".") -> None:
    """Entry point: launch the editor window."""
    if not glfw.init():
        print("Failed to initialize GLFW", file=sys.stderr)
        sys.exit(1)

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)

    window = glfw.create_window(
        1280, 720, "Lavender Map Editor", None, None)
    if not window:
        glfw.terminate()
        print("Failed to create GLFW window", file=sys.stderr)
        sys.exit(1)

    glfw.make_context_current(window)
    imgui.create_context()
    impl = GlfwRenderer(window)

    app = EditorApp(Path(engine_dir), Path(project_dir))
    app.initialize()

    while not glfw.window_should_close(window):
        glfw.poll_events()
        impl.process_inputs()

        imgui.new_frame()
        app.draw()
        imgui.render()

        gl.glClearColor(0.1, 0.1, 0.1, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)

    impl.shutdown()
    glfw.terminate()
