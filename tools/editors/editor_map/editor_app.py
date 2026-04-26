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
    parse_tile_header_from_file, TileInfo, TileParseError,
    TileLayerField, TileLayerLayout, write_tile_header,
    write_tile_kind_header_for_layer,
)
from core.c_enum import (
    parse_c_enum_from_file, find_enum_by_name, CEnum,
    write_tile_layer_header,
)
from core.tile_kind_editor import TileKindEditorState
from core.world_directory import list_worlds, ensure_world_dir, world_root
from core.editor_project_config import (
    EditorProjectConfig,
    EditorBuildConfig,
    WorldEditorConfig,
    load_editor_project_config,
    save_editor_project_config,
    load_build_config,
    save_build_config,
    load_world_editor_config,
    save_world_editor_config,
)
from core.tilesheet import Tilesheet, load_tilesheet
from core.tilesheet_manager import TilesheetManager
from core.tilesheet_viewer import TilesheetViewer
from core.file_hud import FileHUD, LayerEditorWindow, KindEditorWindow
from core.layer_manager import LayerManager, LayerEntry
from ui.message_hud import MessageHUD

VERSION = "0.1.0"


class EditorApp:
    """Main editor application."""

    def __init__(
            self,
            engine_dir: Path,
            project_dir: Optional[Path] = None,
            platform: str = ""):
        self._engine_dir = engine_dir
        self._project_dir = project_dir or Path(".")
        self._platform = platform

        # Core systems
        self._keybind_manager = KeybindManager()
        self._message_hud = MessageHUD()
        self._config: Optional[EngineConfig] = None
        self._tile_info: Optional[TileInfo] = None
        self._tile_enums: List[CEnum] = []
        self._editor_project_config: Optional[EditorProjectConfig] = None
        self._build_config: Optional[EditorBuildConfig] = None
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
        self._delete_confirm_name: str = ""
        self._delete_target: Optional[str] = None

        # File HUD menu bar
        self._file_hud = FileHUD()
        self._tilesheet_manager = TilesheetManager()
        self._tilesheet_viewer = TilesheetViewer()
        self._layer_editor_window = LayerEditorWindow()
        self._kind_editor_window = KindEditorWindow()
        self._layer_manager = LayerManager()
        self._should_exit: bool = False

        # Drag tracking for workspace tools
        self._workspace_dragging: bool = False

        # UI state
        self._properties_width: float = 250.0
        self._tool_hud_width: float = 250.0
        self._file_hierarchy_width: float = 200.0

    def initialize(self) -> None:
        """Load config, parse types, set up modes."""
        self._message_hud.system(f"editor_map v{VERSION}")
        self._message_hud.info(f"Platform: {self._platform}")

        # Wire message hud to keybind manager for logging
        self._keybind_manager.set_message_hud(self._message_hud)

        # Load build config (last world, workspace position)
        self._build_config = load_build_config(self._project_dir)

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

        # Initialize workspace (objects and renderer created here,
        # but wired into modes after mode creation below).
        max_tmp = (self._editor_project_config.max_tmp_chunks
                   if self._editor_project_config else 1024)
        self._objects = WorkspaceObjects(
            self._config,
            project_dir=self._project_dir,
            world_name=self._active_world or "",
            platform=self._platform,
            max_tmp_chunks=max_tmp,
            message_hud=self._message_hud)

        self._renderer = WorkspaceRenderer(self._config)
        if self._tilesheet:
            self._renderer.set_tilesheet(
                self._tilesheet, self._tilesheet_texture_id)
        if self._tile_info:
            self._renderer.set_tile_info(self._tile_info)
        self._renderer.set_layer_manager(self._layer_manager)

        # Wire layer editor callback
        self._layer_editor_window.on_ok = self._on_layer_editor_ok

        # Wire kind editor callback
        self._kind_editor_window.on_ok = self._on_kind_editor_ok

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
        entity_mode = EntityEditMode(
            self._keybind_manager, movement=self._movement)
        inv_mode = InventoryEditMode(
            self._keybind_manager, movement=self._movement)

        self._modes = [gs_mode, chunk_mode, entity_mode, inv_mode]

        # Wire objects into chunk edit mode for tile drawing
        if hasattr(chunk_mode, 'set_objects'):
            chunk_mode.set_objects(self._objects)
        tile_byte_size = (
            self._tile_info.size_in_bytes if self._tile_info else 1)
        if hasattr(chunk_mode, 'set_tile_byte_size'):
            chunk_mode.set_tile_byte_size(tile_byte_size)

        # Set base keybinds
        self._setup_base_keybinds()

        # Activate first mode
        if self._modes:
            self._modes[0].on_activate()

        # Load world list
        self._refresh_worlds()

        # Wire file HUD callbacks
        self._file_hud.on_save = self._save_all
        self._file_hud.on_exit = self._request_exit
        self._file_hud.on_open_tilesheet_viewer = \
            self._open_tilesheet_viewer
        self._file_hud.on_open_layer_editor = \
            self._open_layer_editor
        self._file_hud.on_open_kind_editor = \
            self._open_kind_editor

        # Auto-select last world from build config
        if (self._build_config
                and self._build_config.last_world
                and self._build_config.last_world in self._worlds):
            self._active_world = self._build_config.last_world
            self._active_world_config = load_world_editor_config(
                self._project_dir, self._active_world, self._platform)
            self._movement.go_to(
                self._active_world_config.workspace_x,
                self._active_world_config.workspace_y,
                self._active_world_config.workspace_z)
            self._objects.set_world(
                self._project_dir, self._active_world,
                self._platform)
            # Wire objects into chunk edit mode
            chunk_mode_restore = self._modes[1]
            if hasattr(chunk_mode_restore, 'set_objects'):
                chunk_mode_restore.set_objects(self._objects)
            self._load_tilesheet()
            self._load_layer_manager_from_config()
            self._sync_tilesheets_from_config()
            if self._renderer:
                self._renderer.set_tilesheet(
                    self._tilesheet, self._tilesheet_texture_id)
            self._update_chunk_mode_tilesheet()
            self._update_renderer_layer_tilesheets()
            self._message_hud.info(
                f"Restored last world: {self._active_world}")

    def _load_tilesheet(self) -> None:
        """Load all tilesheets from the active world's config.

        Populates the TilesheetManager from the config's tilesheets
        list.  The first successfully loaded tilesheet (or the first
        layer's tilesheet) becomes the active/fallback tilesheet used
        by the workspace renderer.
        """
        if not self._active_world_config:
            self._message_hud.warning(
                "No tilesheet configured. "
                "Select a world and set its tilesheet path.")
            self._tilesheet_rendering_enabled = False
            return

        ts_paths = list(self._active_world_config.tilesheets)
        if not ts_paths:
            self._message_hud.warning(
                "No tilesheet configured for this world. "
                "Use Edit > Tile > Tilesheets to add one.")
            self._tilesheet_rendering_enabled = False
            return

        # Sync all tilesheets into the manager
        self._tilesheet_manager.sync_from_config(
            self._project_dir, ts_paths)

        # Upload GL textures for newly loaded entries
        for ts_entry in self._tilesheet_manager.entries:
            if ts_entry.gl_texture_id == 0 and ts_entry.tilesheet:
                self._upload_entry_texture(ts_entry)

        # Determine the fallback tilesheet for the workspace renderer:
        # prefer the first layer's tilesheet, else the first loaded.
        fallback_path = ""
        if self._layer_manager.count > 0:
            first_layer = self._layer_manager.get(0)
            if first_layer and first_layer.tilesheet_path:
                fallback_path = first_layer.tilesheet_path
        if not fallback_path and self._tilesheet_manager.count > 0:
            fallback_path = self._tilesheet_manager.all_paths()[0]

        fallback_entry = self._tilesheet_manager.get(fallback_path)
        if fallback_entry and fallback_entry.tilesheet:
            self._tilesheet = fallback_entry.tilesheet
            self._tilesheet_texture_id = fallback_entry.gl_texture_id
            self._tilesheet_rendering_enabled = True
            self._message_hud.info(
                f"Loaded {self._tilesheet_manager.count} tilesheet(s). "
                f"Active: {fallback_path}")
        else:
            self._tilesheet = None
            self._tilesheet_texture_id = 0
            self._tilesheet_rendering_enabled = False
            self._message_hud.error(
                f"Failed to load any tilesheets. "
                f"Tile rendering disabled.")

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
            KeyCombo(glfw.KEY_S, Modifier.CTRL): self._save_all,
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
        self._worlds = list_worlds(
            self._project_dir, self._platform)

    # -- Drawing ---

    def draw(self) -> None:
        """Draw the entire editor UI. Called each frame."""
        display_size = imgui.get_io().display_size
        w, h = display_size.x, display_size.y

        self._process_keybinds()

        # File HUD menu bar (drawn first, at very top)
        self._file_hud.draw(self._objects)

        self._draw_mode_tabs(w)
        self._draw_file_hierarchy(h)
        self._draw_tool_hud(w, h)
        self._draw_properties_hud(w, h)
        self._draw_workspace(w, h)
        self._message_hud.draw(w, h)

        # Sub-windows
        self._kind_editor_window.draw()
        self._tilesheet_viewer.draw(
            self._tilesheet_manager,
            self._project_dir,
            self._active_world or "",
            self._message_hud,
            upload_texture_callback=self._upload_entry_texture)
        self._layer_editor_window.draw()

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
        if io.mouse_wheel != 0:
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
        """Draw the mode tab bar below the menu bar."""
        menu_h = FileHUD.MENU_BAR_HEIGHT
        imgui.set_next_window_position(0, menu_h)
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
        top = 30.0 + FileHUD.MENU_BAR_HEIGHT
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
                # Save workspace position to previous world config
                self._save_workspace_position()
                self._active_world = world_name
                self._active_world_config = load_world_editor_config(
                    self._project_dir, world_name)
                self._movement.go_to(
                    self._active_world_config.workspace_x,
                    self._active_world_config.workspace_y,
                    self._active_world_config.workspace_z)
                self._objects.set_world(
                    self._project_dir, world_name,
                    self._platform)
                # Re-wire objects into chunk edit mode
                chunk_mode = self._modes[1]
                if hasattr(chunk_mode, 'set_objects'):
                    chunk_mode.set_objects(self._objects)
                if self._build_config:
                    self._build_config.last_world = world_name
                    save_build_config(
                        self._project_dir, self._build_config)
                self._message_hud.info(f"Selected world: {world_name}")
                self._load_tilesheet()
                self._load_layer_manager_from_config()
                self._sync_tilesheets_from_config()
                if self._renderer:
                    self._renderer.set_tilesheet(
                        self._tilesheet, self._tilesheet_texture_id)
                    if self._tile_info:
                        self._renderer.set_tile_info(self._tile_info)
                self._update_chunk_mode_tilesheet()
                self._update_renderer_layer_tilesheets()
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
                    target = world_root(
                        self._project_dir, self._delete_target,
                        self._platform)
                    if target.exists():
                        shutil.rmtree(target)
                    self._refresh_worlds()
                    if self._active_world == self._delete_target:
                        self._active_world = None
                        self._active_world_config = None
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
                        self._project_dir,
                        self._new_world_name.strip(),
                        self._platform)
                    self._refresh_worlds()
                    self._message_hud.info(
                        f"Created world: {self._new_world_name.strip()}")
                    self._new_world_name = ""

        imgui.end()

    def _draw_tool_hud(self, window_width: float, window_height: float) -> None:
        """Draw the Tool HUD on the right side."""
        msg_h = self._message_hud.panel_height
        top = 30.0 + FileHUD.MENU_BAR_HEIGHT
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
        top = 30.0 + FileHUD.MENU_BAR_HEIGHT
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
        top = 30.0 + FileHUD.MENU_BAR_HEIGHT
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

        # Draw tiles from loaded chunks
        if self._renderer and self._objects:
            tile_byte_size = (
                self._tile_info.size_in_bytes if self._tile_info else 1)
            self._renderer.draw(
                self._objects,
                self._movement,
                (ws_ox, ws_oy),
                (ws_w, ws_h),
                tile_byte_size=tile_byte_size)

        # Draw tool overlays (e.g. TileRect drag preview)
        mode = self._modes[self._active_mode_index]
        tool = mode.active_tool
        if tool:
            tool.draw_overlay(
                workspace=None,
                draw_list=draw_list,
                movement=self._movement,
                window_pos=(ws_ox, ws_oy),
                window_size=(ws_w, ws_h))

        # Draw mode-specific content
        mode.draw_workspace(None)

        # Route tool overlays are drawn above (before mode content).

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

        # Route workspace clicks and drags to the active tool
        tool = mode.active_tool
        if imgui.is_window_hovered():
            mouse = imgui.get_mouse_position()
            tile_x, tile_y = self._movement.screen_to_tile(
                mouse.x, mouse.y, ws_ox, ws_oy, ws_w, ws_h)
            tile_z = self._movement.viewport.center_z

            if imgui.is_mouse_clicked(0):
                self._workspace_dragging = True
                if tool:
                    tool.on_workspace_drag_begin(
                        float(tile_x), float(tile_y), tile_z)
                    tool.on_workspace_click(
                        float(tile_x), float(tile_y), tile_z)

        if self._workspace_dragging and tool:
            mouse = imgui.get_mouse_position()
            tile_x, tile_y = self._movement.screen_to_tile(
                mouse.x, mouse.y, ws_ox, ws_oy, ws_w, ws_h)
            tile_z = self._movement.viewport.center_z

            if imgui.is_mouse_down(0) and not imgui.is_mouse_clicked(0):
                tool.on_workspace_drag_update(
                    float(tile_x), float(tile_y), tile_z)

            if imgui.is_mouse_released(0):
                tool.on_workspace_drag_end(
                    float(tile_x), float(tile_y), tile_z)
                self._workspace_dragging = False

        imgui.end()


    def _request_exit(self) -> None:
        """Request editor exit (called from FileHUD)."""
        self._should_exit = True

    @property
    def should_exit(self) -> bool:
        """True when the editor should close its window."""
        return self._should_exit

    def _open_tilesheet_viewer(self) -> None:
        """Open the tilesheet viewer sub-window."""
        self._tilesheet_viewer.open()

    def _open_layer_editor(self) -> None:
        """Open the layer editor sub-window."""
        ts_paths = self._tilesheet_manager.all_paths()
        self._layer_editor_window.open(
            layer_manager=self._layer_manager,
            tilesheet_paths=ts_paths)

    def _open_kind_editor(self) -> None:
        """Open the tile kind editor sub-window."""
        if not self._tile_info or not self._tile_enums:
            self._message_hud.error(
                "Cannot open Kind Editor: no tile layers or "
                "enums loaded. Ensure tile.h is valid and "
                "tile enums are found.")
            return

        layer_names: List[str] = []
        layer_enums: List[CEnum] = []
        layer_bit_widths: List[int] = []
        layer_logic_bits: List[int] = []
        layer_animation_bits: List[int] = []
        layer_header_paths: List[Path] = []
        layer_guard_macros: List[str] = []

        for i, lf in enumerate(self._tile_info.layer_fields):
            if i >= len(self._tile_enums):
                break
            enum = self._tile_enums[i]
            layout = (self._tile_info.layer_layouts[i]
                      if i < len(self._tile_info.layer_layouts)
                      else None)

            layer_names.append(lf.field_name)
            layer_enums.append(enum)
            layer_bit_widths.append(lf.bit_width)
            layer_logic_bits.append(
                layout.logic_bits if layout else 0)
            layer_animation_bits.append(
                layout.animation_bits if layout else 0)

            # Resolve header path: project first, then engine
            kind_filename = lf.enum_type_name.lower() + ".h"
            project_path = (
                self._project_dir / "include" / "types"
                / "implemented" / "world" / kind_filename)
            if project_path.exists():
                layer_header_paths.append(project_path)
            else:
                engine_path = (
                    self._engine_dir / "core" / "include"
                    / "types" / "implemented" / "world"
                    / kind_filename)
                layer_header_paths.append(engine_path)

            guard = "DEFINE_" + lf.enum_type_name.upper()
            layer_guard_macros.append(guard)

        # Build per-layer tilesheet info for preview buttons
        from core.tilesheet import TILE_PX
        per_layer_tex_ids: List[int] = []
        per_layer_tile_ws: List[int] = []
        per_layer_tile_hs: List[int] = []
        per_layer_cols: List[int] = []
        per_layer_rows: List[int] = []
        per_layer_img_ws: List[int] = []
        per_layer_img_hs: List[int] = []

        for i, lf in enumerate(self._tile_info.layer_fields):
            if i >= len(layer_names):
                break
            # Look up this layer's tilesheet via the layer manager
            layer_entry = self._layer_manager.get(i)
            ts_path = layer_entry.tilesheet_path if layer_entry else ""
            ts_entry = (
                self._tilesheet_manager.get(ts_path)
                if ts_path else None)

            if ts_entry and ts_entry.tilesheet and ts_entry.gl_texture_id:
                ts = ts_entry.tilesheet
                per_layer_tex_ids.append(ts_entry.gl_texture_id)
                per_layer_tile_ws.append(TILE_PX)
                per_layer_tile_hs.append(TILE_PX)
                per_layer_img_ws.append(ts.width)
                per_layer_img_hs.append(ts.height)
                per_layer_cols.append(ts.tiles_per_row)
                per_layer_rows.append(
                    (ts.height // TILE_PX) if TILE_PX > 0 else 1)
            else:
                # Fallback: no tilesheet for this layer
                per_layer_tex_ids.append(0)
                per_layer_tile_ws.append(TILE_PX)
                per_layer_tile_hs.append(TILE_PX)
                per_layer_img_ws.append(0)
                per_layer_img_hs.append(0)
                per_layer_cols.append(1)
                per_layer_rows.append(1)

        self._kind_editor_window.open(
            layer_names=layer_names,
            layer_enums=layer_enums,
            layer_bit_widths=layer_bit_widths,
            layer_logic_bits=layer_logic_bits,
            layer_animation_bits=layer_animation_bits,
            layer_header_paths=layer_header_paths,
            layer_guard_macros=layer_guard_macros,
            layer_tilesheet_texture_ids=per_layer_tex_ids,
            layer_tilesheet_tile_ws=per_layer_tile_ws,
            layer_tilesheet_tile_hs=per_layer_tile_hs,
            layer_tilesheet_cols=per_layer_cols,
            layer_tilesheet_rows=per_layer_rows,
            layer_tilesheet_img_ws=per_layer_img_ws,
            layer_tilesheet_img_hs=per_layer_img_hs,
        )

    def _upload_entry_texture(self, entry) -> None:
        """Upload GL texture for a TilesheetEntry."""
        if entry.tilesheet is None:
            return
        ts = entry.tilesheet
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
            entry.gl_texture_id = int(tex_id)
        except Exception as e:
            self._message_hud.error(
                f"Failed to upload tilesheet texture: {e}")
            entry.gl_texture_id = 0

    def _on_kind_editor_ok(
            self,
            state: 'TileKindEditorState',
            header_path: Path,
            guard_macro: str) -> None:
        """Handle Kind Editor OK — reload affected enum and mappings."""
        self._message_hud.info(
            f"Kind Editor: wrote {header_path.name} "
            f"({len(state.tile_kinds)} entries).")
        self._reload_tile_enums()
        self._update_renderer_tile_index_maps()

    def _save_all(self) -> None:
        """Flush all pending .tmp files to disk (Ctrl+S)."""
        if self._objects:
            count = self._objects.flush_all_tmp()
            self._message_hud.info(
                f"Save: {count} chunk(s) written to disk.")
        self._save_workspace_position()

    def _save_workspace_position(self) -> None:
        """Save current workspace position, layer config, and tilesheet
        list to the active world config and build config."""
        vp = self._movement.viewport
        if self._active_world and self._active_world_config:
            self._active_world_config.workspace_x = vp.center_x
            self._active_world_config.workspace_y = vp.center_y
            self._active_world_config.workspace_z = vp.center_z
            # Persist layer-to-tilesheet associations
            self._active_world_config.layers = \
                self._layer_manager.to_list()
            all_ts = self._layer_manager.get_unique_tilesheet_paths()
            for p in self._tilesheet_manager.all_paths():
                if p and p not in all_ts:
                    all_ts.append(p)
            self._active_world_config.tilesheets = all_ts
            save_world_editor_config(
                self._project_dir, self._active_world,
                self._active_world_config, self._platform)
        if self._build_config:
            self._build_config.workspace_x = vp.center_x
            self._build_config.workspace_y = vp.center_y
            self._build_config.workspace_z = vp.center_z
            save_build_config(self._project_dir, self._build_config)

    def _load_layer_manager_from_config(self) -> None:
        """Load layer manager from the active world config."""
        self._layer_manager.clear()
        if self._active_world_config and self._active_world_config.layers:
            self._layer_manager.from_list(
                self._active_world_config.layers)
            self._message_hud.info(
                f"Loaded {self._layer_manager.count} layer(s) "
                f"from world config.")
        elif self._tile_info:
            # Bootstrap from parsed tile.h if no config layers yet
            for i, lf in enumerate(self._tile_info.layer_fields):
                layout = (self._tile_info.layer_layouts[i]
                          if i < len(self._tile_info.layer_layouts)
                          else TileLayerLayout())
                ts_path = ""
                if (self._active_world_config
                        and self._active_world_config.tilesheets):
                    ts_path = self._active_world_config.tilesheets[0]
                self._layer_manager.add(LayerEntry(
                    layer_name=f"Tile_Layer__{i}",
                    enum_type_name=lf.enum_type_name,
                    tilesheet_path=ts_path,
                    bit_width=lf.bit_width,
                    logic_bits=layout.logic_bits,
                    animation_bits=layout.animation_bits,
                ))

    def _sync_tilesheets_from_config(self) -> None:
        """Sync tilesheet manager from world config tilesheet list."""
        if not self._active_world_config:
            return
        paths = list(self._active_world_config.tilesheets)
        # Include paths referenced by layers
        for entry in self._layer_manager.layers:
            if entry.tilesheet_path and entry.tilesheet_path not in paths:
                paths.append(entry.tilesheet_path)
        self._tilesheet_manager.sync_from_config(
            self._project_dir, paths)
        # Upload GL textures for any entries that need them
        for ts_entry in self._tilesheet_manager.entries:
            if ts_entry.gl_texture_id == 0 and ts_entry.tilesheet:
                self._upload_entry_texture(ts_entry)

    def _update_renderer_layer_tilesheets(self) -> None:
        """Push per-layer tilesheet assignments to the renderer."""
        if not self._renderer:
            return
        self._renderer.clear_layer_tilesheets()
        for i, layer_entry in enumerate(self._layer_manager.layers):
            if not layer_entry.tilesheet_path:
                continue
            ts_entry = self._tilesheet_manager.get(
                layer_entry.tilesheet_path)
            if ts_entry and ts_entry.tilesheet and ts_entry.gl_texture_id:
                self._renderer.set_layer_tilesheet(
                    i, ts_entry.tilesheet, ts_entry.gl_texture_id)
        # Also refresh tile index mappings
        self._update_renderer_tile_index_maps()

    def _update_renderer_tile_index_maps(self) -> None:
        """Load per-layer tilesheet tile-index mappings and push to renderer.

        For each tile layer, reads the JSON sidecar mapping (enum member
        name → tilesheet tile index), converts it to an enum-value-based
        mapping, and sets it on the renderer so that tile values are
        remapped to the correct tilesheet tile before UV computation.
        """
        if not self._renderer:
            return
        self._renderer.clear_layer_tile_index_maps()
        if not self._tile_info:
            return

        from core.tile_kind_editor import (
            load_tilesheet_mapping,
            build_value_to_tile_index_map,
        )

        for i, lf in enumerate(self._tile_info.layer_fields):
            if i >= len(self._tile_enums):
                continue
            enum = self._tile_enums[i]

            # Resolve header path (same logic as _open_kind_editor)
            kind_filename = lf.enum_type_name.lower() + ".h"
            project_path = (
                self._project_dir / "include" / "types"
                / "implemented" / "world" / kind_filename)
            if project_path.exists():
                header_path = project_path
            else:
                header_path = (
                    self._engine_dir / "core" / "include"
                    / "types" / "implemented" / "world"
                    / kind_filename)

            name_map = load_tilesheet_mapping(header_path)
            if name_map:
                value_map = build_value_to_tile_index_map(enum, name_map)
                if value_map:
                    self._renderer.set_layer_tile_index_map(i, value_map)

    def _on_layer_editor_ok(self, entries) -> None:
        """Handle Layer Editor OK — write tile_layer.h, tile.h, update config."""
        from core.c_enum import write_tile_layer_header
        from core.tile_parser import (
            TileLayerField, TileLayerLayout, write_tile_header,
        )

        # Build layer data from editor entries
        new_layers: List[LayerEntry] = []
        layer_fields: List[TileLayerField] = []
        layer_layouts: List[TileLayerLayout] = []
        layer_names: List[str] = []

        for entry in entries:
            le = LayerEntry(
                layer_name=entry.layer_name,
                enum_type_name=entry.enum_type_name,
                tilesheet_path=entry.tilesheet_path,
                bit_width=entry.bit_width,
                logic_bits=entry.logic_bits,
                animation_bits=entry.animation_bits,
            )
            err = le.validate()
            if err:
                self._message_hud.error(
                    f"Layer '{entry.layer_name}': {err}")
                return
            new_layers.append(le)
            layer_names.append(entry.layer_name)

            # Derive field name from enum type
            field_name = f"the_kind_of__{entry.layer_name.lower()}"
            layer_fields.append(TileLayerField(
                enum_type_name=entry.enum_type_name,
                field_name=field_name,
                bit_width=entry.bit_width,
            ))
            remainder = (entry.bit_width
                         - entry.logic_bits
                         - entry.animation_bits)
            layer_layouts.append(TileLayerLayout(
                logic_bits=entry.logic_bits,
                animation_bits=entry.animation_bits,
                remainder_bits=max(0, remainder),
            ))

        # Write tile_layer.h
        tile_layer_path = (
            self._project_dir / "include" / "types"
            / "implemented" / "world" / "tile_layer.h")
        default_layer = layer_names[0] if layer_names else ""
        try:
            write_tile_layer_header(
                tile_layer_path,
                layer_names,
                default_layer=default_layer,
                sight_blocking_layer=default_layer,
                passable_layer=default_layer,
                ground_layer=default_layer,
            )
            self._message_hud.info(
                f"Wrote tile_layer.h with {len(layer_names)} layer(s).")
        except Exception as e:
            self._message_hud.error(
                f"Failed to write tile_layer.h: {e}")
            return

        # Write tile.h
        tile_h_path = (
            self._project_dir / "include" / "types"
            / "implemented" / "world" / "tile.h")
        try:
            write_tile_header(tile_h_path, layer_fields, layer_layouts)
            self._message_hud.info(
                f"Wrote tile.h ({len(layer_fields)} layer(s)).")
        except Exception as e:
            self._message_hud.error(
                f"Failed to write tile.h: {e}")
            return

        # Generate _kind.h files for each layer that doesn't
        # already have one.  This ensures the project has the
        # enum header that defines_weak.h expects so the weak
        # fallback is skipped.
        for entry in entries:
            kind_filename = entry.enum_type_name.lower() + ".h"
            kind_filepath = (
                self._project_dir / "include" / "types"
                / "implemented" / "world" / kind_filename)
            if not kind_filepath.exists():
                try:
                    write_tile_kind_header_for_layer(
                        kind_filepath,
                        entry.enum_type_name,
                        logic_bits=entry.logic_bits,
                    )
                    self._message_hud.info(
                        f"Generated {kind_filename} for layer "
                        f"'{entry.layer_name}'.")
                except Exception as e:
                    self._message_hud.error(
                        f"Failed to write {kind_filename}: {e}")
            else:
                self._message_hud.info(
                    f"{kind_filename} already exists, skipping "
                    f"generation.")

        # Update layer manager
        self._layer_manager.set_layers(new_layers)

        # Save to world config — persist layer list and all
        # referenced tilesheet paths so they survive reload.
        if self._active_world and self._active_world_config:
            self._active_world_config.layers = \
                self._layer_manager.to_list()
            # Collect all unique tilesheet paths from layers
            all_ts = self._layer_manager.get_unique_tilesheet_paths()
            # Also keep any tilesheets already in the manager that
            # aren't referenced by a layer (user may have loaded
            # extras via the tilesheet viewer).
            for p in self._tilesheet_manager.all_paths():
                if p and p not in all_ts:
                    all_ts.append(p)
            self._active_world_config.tilesheets = all_ts
            save_world_editor_config(
                self._project_dir, self._active_world,
                self._active_world_config, self._platform)

        # Re-parse tile.h to refresh tile_info
        tile_result = parse_tile_header_from_file(tile_h_path)
        if isinstance(tile_result, TileParseError):
            self._message_hud.error(
                f"Re-parse tile.h failed: {tile_result.message}")
        else:
            self._tile_info = tile_result
            if self._renderer:
                self._renderer.set_tile_info(self._tile_info)

        # Reload tile enums
        self._reload_tile_enums()

        # Sync tilesheets and update renderer
        self._sync_tilesheets_from_config()
        self._update_renderer_layer_tilesheets()

    def _update_chunk_mode_tilesheet(self) -> None:
        """Push the active tilesheet and GL texture to the workspace
        renderer."""
        if self._renderer:
            self._renderer.set_tilesheet(
                self._tilesheet, self._tilesheet_texture_id)
            if self._tile_info:
                self._renderer.set_tile_info(self._tile_info)


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


def run_editor(
        engine_dir: str,
        project_dir: str = ".",
        platform: str = "") -> None:
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

    app = EditorApp(Path(engine_dir), Path(project_dir), platform)
    app.initialize()

    while not glfw.window_should_close(window):
        glfw.poll_events()
        impl.process_inputs()

        imgui.new_frame()
        app.draw()
        imgui.render()

        if app.should_exit:
            glfw.set_window_should_close(window, True)

        gl.glClearColor(0.1, 0.1, 0.1, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)

    impl.shutdown()
    glfw.terminate()
