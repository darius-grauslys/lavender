"""
Main editor application for editor_map.

Ties together all modules: modes, tools, workspace, keybinds,
message HUD, file hierarchy, and properties panels.

Uses Dear ImGui via pyimgui.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional

import imgui
from imgui.integrations.glfw import GlfwRenderer
import glfw
import OpenGL.GL as gl

# Ensure editor_map package root is on sys.path
_editor_map_dir = str(Path(__file__).resolve().parent)
if _editor_map_dir not in sys.path:
    sys.path.insert(0, _editor_map_dir)

from keybinds.keybind import KeyCombo, Modifier
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
        self._new_world_name: str = ""
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

        # Initialize workspace
        self._objects = WorkspaceObjects(self._config)
        self._renderer = WorkspaceRenderer(self._config)

        # Initialize modes
        gs_mode = GlobalSpaceViewMode(self._keybind_manager)
        chunk_mode = ChunkEditMode(self._keybind_manager)
        if self._tile_enums:
            chunk_mode.set_tile_enums(self._tile_enums)
        entity_mode = EntityEditMode(self._keybind_manager)
        inv_mode = InventoryEditMode(self._keybind_manager)

        self._modes = [gs_mode, chunk_mode, entity_mode, inv_mode]

        # Set base keybinds
        self._setup_base_keybinds()

        # Activate first mode
        if self._modes:
            self._modes[0].on_activate()

        # Load world list
        self._refresh_worlds()

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
        """Check for keybind activations this frame."""
        io = imgui.get_io()
        if io.want_capture_keyboard:
            return

        mods = Modifier.NONE
        if io.key_ctrl:
            mods |= Modifier.CTRL
        if io.key_shift:
            mods |= Modifier.SHIFT
        if io.key_alt:
            mods |= Modifier.ALT

        for key in range(glfw.KEY_SPACE, glfw.KEY_LAST + 1):
            if imgui.is_key_pressed(key):
                combo = KeyCombo(key, mods)
                self._keybind_manager.fire(combo)

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
                self._message_hud.info(f"Selected world: {world_name}")
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

        # Draw mode-specific content
        mode = self._modes[self._active_mode_index]
        mode.draw_workspace(None)

        # Draw the tile grid if renderer is available
        if self._renderer and self._objects:
            win_pos = imgui.get_window_position()
            tile_size = self._tile_info.size_in_bytes if self._tile_info else 1
            self._renderer.draw(
                self._objects,
                self._movement,
                (win_pos.x, win_pos.y),
                (ws_w, ws_h),
                tile_size)

        # Handle workspace input
        if imgui.is_window_hovered():
            io = imgui.get_io()
            # Scroll to pan
            if io.mouse_wheel != 0:
                if io.key_shift:
                    self._movement.pan_by_tiles(
                        int(-io.mouse_wheel), 0)
                else:
                    self._movement.pan_by_tiles(
                        0, int(-io.mouse_wheel))

        imgui.end()


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
