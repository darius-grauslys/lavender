#!/usr/bin/env python3
"""gen_ui – generate C source/header from a UI XML description.

Usage:
    python tools/gen_ui.py <source.xml> [config_field value ...]

This is a clean rewrite of the original ``ui_builder.py``.  All UI element
types live in ``tools/gen_ui_elements/`` as proper classes.
"""

from __future__ import annotations

import os
import sys
import xml.etree.ElementTree as ET
from collections import deque
from typing import Dict, List, Optional, Type

# ---------------------------------------------------------------------------
# Ensure the repo root is on sys.path so that ``tools.*`` is importable.
# ---------------------------------------------------------------------------
_TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_TOOLS_DIR)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from tools.gen_ui_elements.base import (
    Background,
    CodeWriter,
    Config,
    Context,
    GeneratorState,
    Include,
    P_UI_ITERATOR,
    P_UI_MANAGER,
    UIElement,
    UISignature,
    xml_int,
    xml_str,
)
from tools.gen_ui_elements.containers import (
    AllocateUIContainerElement,
    AllocateUIElement,
    AllocChildElement,
    GridElement,
    GroupElement,
)
from tools.gen_ui_elements.widgets import (
    BackgroundElement,
    ButtonElement,
    CodeElement,
    DraggableElement,
    DropZoneElement,
    SliderElement,
    WindowElementElement,
)

# ---------------------------------------------------------------------------
# Built-in element class registry (xml_tag -> class)
# ---------------------------------------------------------------------------

_BUILTIN_ELEMENT_CLASSES: Dict[str, Type[UIElement]] = {
    cls.xml_tag: cls
    for cls in [
        GroupElement,
        GridElement,
        AllocateUIElement,
        AllocateUIContainerElement,
        AllocChildElement,
        BackgroundElement,
        ButtonElement,
        WindowElementElement,
        SliderElement,
        DraggableElement,
        DropZoneElement,
        CodeElement,
    ]
}


def build_element_registry(
    config: Config,
) -> Dict[str, UIElement]:
    """Create *instances* of element handlers keyed by XML tag.

    Each ``<ui_func_signature>`` in the XML ``<config>`` maps an XML tag to
    one of the built-in handler classes and supplies the C function name(s).
    """
    registry: Dict[str, UIElement] = {}
    for raw in config.signatures:
        tag = raw.xml_tag
        cls = _BUILTIN_ELEMENT_CLASSES.get(tag)
        if cls is None:
            print(f"warning: no handler class for xml tag '{tag}'")
            continue
        instance = cls()
        instance.xml_tag = tag
        instance.c_signature = raw.c_signatures.split(",")[0] if raw.c_signatures else ""
        registry[tag] = instance
    return registry


# ---------------------------------------------------------------------------
# Source generation
# ---------------------------------------------------------------------------

def generate_source(
    xml_node_ui,
    state: GeneratorState,
) -> None:
    """Emit the full ``.c`` and ``.h`` content into *state*."""
    cfg = state.config
    w = state.writer
    h = state.header

    print(f"GEN: {cfg.associated_header_sub_dir_in__include_folder}"
          f"\\{cfg.source_name}")

    # -- includes ----------------------------------------------------------
    cfg.includes.insert(
        0,
        Include(
            f"{cfg.associated_header_sub_dir_in__include_folder}"
            f"{cfg.source_name}.h"
        ),
    )
    for inc in cfg.includes:
        w.write_include(inc.path)

    # -- header preamble ---------------------------------------------------
    guard = cfg.source_name.upper()
    h.raw(f"#ifndef {guard}_H\n")
    h.raw(f"#define {guard}_H\n")
    h.raw("\n#include <defines.h>\n")
    h.raw(
        "// THIS CODE IS AUTO GENERATED. "
        "Go to ./core/assets/ui/xml/ instead of modifying this file.\n"
    )

    func_name = f"allocate_ui_for__{cfg.source_name}"
    param_list = (
        "Gfx_Context *p_gfx_context, "
        "Graphics_Window *p_gfx_window, "
        "Game *p_game, "
        "UI_Manager *p_ui_manager, "
        "Identifier__u16 index_of__ui_element_offset__u16"
    )
    h.raw(f"\nbool {func_name}({param_list});\n")

    # -- source preamble ---------------------------------------------------
    w.raw(
        "// THIS CODE IS AUTO GENERATED. "
        "Go to ./core/assets/ui/xml/ instead of modifying this file.\n"
    )
    w.raw(f"\nbool {func_name}({param_list})")
    w.open_brace()

    # -- local variables ---------------------------------------------------
    w.write_local_decl("UI_Element *", P_UI_ITERATOR)
    w.write_local_decl("UI_Element *", f"{P_UI_ITERATOR}_previous_previous")
    w.write_local_decl("UI_Element *", f"{P_UI_ITERATOR}_previous")
    w.write_local_decl("UI_Element *", f"{P_UI_ITERATOR}_child")

    # -- root context ------------------------------------------------------
    root_ctx = Context()
    root_ctx.p_ui_element = ""
    state.push_context(root_ctx)

    state.current_element_id = xml_int(
        xml_node_ui, "offset_of__ui_index", 0
    )

    # -- optional tile-map setup -------------------------------------------
    tile_map_size = xml_str(
        xml_node_ui, "ui_tile_map__size", "UI_Tile_Map_Size__None"
    )
    has_tile_map = tile_map_size != "UI_Tile_Map_Size__None"

    if has_tile_map:
        w.write_assignment(
            "p_gfx_window->ui_tile_map__wrapper",
            w.call(
                "allocate_ui_tile_map_with__ui_tile_map_manager",
                [
                    "get_p_ui_tile_map_manager_from__gfx_context(p_gfx_context)",
                    tile_map_size,
                ],
            ),
        )

    aliased_tex = xml_str(
        xml_node_ui,
        "ui_tile_map__aliased_texture",
        "UI_Tile_Map__Aliased_Texture",
    )
    if aliased_tex != "UI_Tile_Map__Aliased_Texture":
        if has_tile_map:
            w.write_assignment(
                "Identifier__u32 uuid_of__aliased_texture",
                w.call(
                    "get_uuid_of__aliased_texture",
                    [
                        "get_p_aliased_texture_manager_from__game(p_game)",
                        f'"{aliased_tex}"',
                    ],
                ),
            )
            w.write_call(
                "set_graphics_window__ui_tile_map__texture",
                ["p_gfx_window", "uuid_of__aliased_texture"],
            )
        else:
            print("MISSING UI_TILE_MAP_SIZE - ui_tile_map__aliased_texture")

    tile_map = xml_str(xml_node_ui, "ui_tile_map", "None")
    tile_map_len = xml_str(xml_node_ui, "ui_tile_map__length", "0")
    tile_map_off = xml_str(xml_node_ui, "ui_tile_map__offset", "0")
    if tile_map != "None":
        if has_tile_map:
            w.write_call(
                "copy_into_ui_tile_map",
                [
                    "get_p_ui_tile_map_from__graphics_window(p_gfx_window)",
                    tile_map,
                    tile_map_off,
                    tile_map_len,
                ],
            )
        else:
            print("MISSING UI_TILE_MAP_SIZE - ui_tile_map")

    ui_position = xml_str(xml_node_ui, "ui_position", "")
    if ui_position:
        w.write_call(
            "set_position_3i32_of__graphics_window",
            ["p_game", "p_gfx_window", f"get_vector__3i32({ui_position})"],
        )

    # -- child elements ----------------------------------------------------
    for child in xml_node_ui:
        state.construct_element(child)

    # -- epilogue ----------------------------------------------------------
    w.line("return true", semicolon=True)
    w.close_brace()
    h.raw("#endif\n")


# ---------------------------------------------------------------------------
# read_ui – top-level parse + generate + write
# ---------------------------------------------------------------------------

def read_ui(
    path: str,
    config: Config,
    *,
    resize_callback=None,
) -> Optional[GeneratorState]:
    """Parse *path*, generate code, optionally write files.

    Returns the ``GeneratorState`` (useful for the viewer) or ``None`` on
    error.
    """
    try:
        tree = ET.parse(path)
        root = tree.getroot()
    except ET.ParseError as exc:
        print(f"Error reading xml: {exc.position}")
        return None

    xml_config = root.find("config")
    xml_ui = root.find("ui")
    if xml_config is None:
        print("xml is missing config node.")
        return None
    if xml_ui is None:
        print("xml is missing ui node.")
        return None

    try:
        config.update_from_xml(xml_config, resize_callback=resize_callback)
    except FileNotFoundError as exc:
        print(f"File missing: {exc.filename}")
        return None

    state = GeneratorState(config)
    state.element_registry = build_element_registry(config)

    try:
        generate_source(xml_ui, state)
    except KeyError as exc:
        print(f"Missing field: {exc}")
        return None

    if config.is_outputting:
        _write_output(config, state)

    return state


def _write_output(config: Config, state: GeneratorState) -> None:
    for attr, writer in [
        ("output__c_path", state.writer),
        ("output__h_path", state.header),
    ]:
        rel = getattr(config, attr)
        full = os.path.join(config.base_dir, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w") as fh:
            fh.write(writer.get_source())


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: gen_ui.py <source.xml> [config_field value ...]")
        sys.exit(1)

    source_xml = sys.argv[1]
    if not os.path.exists(source_xml):
        print(f"Cannot find source xml: {source_xml}")
        sys.exit(1)

    config = Config(source_xml)

    # Apply CLI overrides (pairs of field_name value).
    idx = 2
    while idx + 1 < len(sys.argv):
        field_name = sys.argv[idx]
        value = sys.argv[idx + 1]
        if hasattr(config, field_name):
            current = getattr(config, field_name)
            if isinstance(current, bool):
                setattr(config, field_name, value.lower() == "true")
            elif isinstance(current, int):
                setattr(config, field_name, int(value))
            else:
                setattr(config, field_name, value)
        else:
            print(f"warning: '{field_name}' is not a valid config field")
        idx += 2

    read_ui(source_xml, config)


if __name__ == "__main__":
    main()
