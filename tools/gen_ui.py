#!/usr/bin/env python3
"""gen_ui – scaffold a new UI XML template.

Usage:
    python tools/gen_ui.py create <output.xml> [options...]

Creates a new UI XML template pre-populated with all core Lavender engine
headers and built-in ``ui_func_signature`` entries for the chosen platform.

For generating C source/header files from an existing UI XML, use
``gen_ui_code.py`` instead.
"""

from __future__ import annotations

import argparse
import os
import sys
import xml.etree.ElementTree as ET
from typing import List, Tuple


# ---------------------------------------------------------------------------
# Core Lavender includes & signatures for XML scaffolding
# ---------------------------------------------------------------------------
# These are engine headers (from $LAVENDER_DIR), NOT game-specific headers.
# Game-specific headers (e.g. ui/ui_ag__*.h, assets/ui/default/ui_map_*.h,
# ui/implemented/handlers/*) must be added via --include.

_CORE_INCLUDES_SDL: List[str] = [
    "ui/ui_element.h",
    "ui/ui_button.h",
    "ui/ui_drop_zone.h",
    "ui/ui_draggable.h",
    "ui/ui_slider.h",
    "ui/ui_window_element.h",
    "ui/ui_manager.h",
    "ui/ui_context.h",
    "ui/ui_tile_map.h",
    "ui/ui_tile_map_manager.h",
    "rendering/graphics_window.h",
    "rendering/graphics_window_manager.h",
    "rendering/gfx_context.h",
    "rendering/aliased_texture_manager.h",
    "vectors.h",
    "defines.h",
    "game.h",
]

_CORE_INCLUDES_NDS: List[str] = [
    "ui/ui_element.h",
    "ui/ui_button.h",
    "ui/ui_drop_zone.h",
    "ui/ui_draggable.h",
    "ui/ui_slider.h",
    "ui/ui_manager.h",
    "vectors.h",
    "defines.h",
    "nds_defines.h",
    "game.h",
]

# All built-in ui_func_signatures.
# None of these are game-specific — they are all engine builtins.
# Tuples of (xml_tag, c_signatures_or_empty).
_CORE_SIGNATURES_COMMON: List[Tuple[str, str]] = [
    ("grid", ""),
    ("group", ""),
    ("alloc_child", "allocate_ui_element_from__ui_manager_as__child"),
    ("allocate_ui", "allocate_ui_element_from__ui_manager"),
    ("allocate_ui_container",
     "allocate_many_ui_elements_from__ui_manager_in__succession"),
    ("code", ""),
    ("button", "initialize_ui_element_as__button"),
    ("slider", "initialize_ui_element_as__slider"),
    ("draggable", "initialize_ui_element_as__draggable"),
    ("drop_zone", "initialize_ui_element_as__drop_zone"),
]

# SDL adds background and window_element signatures.
_CORE_SIGNATURES_SDL: List[Tuple[str, str]] = _CORE_SIGNATURES_COMMON + [
    ("background", "SDL_initialize_ui_element_as__background"),
    ("window_element",
     "initialize_ui_element_as__window_element_and__open_window"),
]

# NDS uses only the common (platform-agnostic) signatures.
_CORE_SIGNATURES_NDS: List[Tuple[str, str]] = list(_CORE_SIGNATURES_COMMON)


# ---------------------------------------------------------------------------
# XML scaffolding – ``gen_ui.py create``
# ---------------------------------------------------------------------------

def _indent_xml(elem: ET.Element, level: int = 0) -> None:
    """In-place pretty-print indentation for an ElementTree element."""
    indent = "\n" + "  " * (level + 1)
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = indent
        for i, child in enumerate(elem):
            _indent_xml(child, level + 1)
            if i < len(elem) - 1:
                child.tail = indent
            else:
                child.tail = "\n" + "  " * level
    if level and (not elem.tail or not elem.tail.strip()):
        elem.tail = "\n" + "  " * (level - 1)


def create_xml(cli_args: List[str]) -> None:
    """Scaffold a new UI XML template with all core Lavender essentials.

    The generated XML is pre-populated with:
    * All core engine header includes (from ``$LAVENDER_DIR``).
    * All built-in ``<ui_func_signature>`` entries (no game-specific ones).
    * Proper ``<output>`` paths derived from ``--sub-dir`` and filename.
    * ``offset_of__ui_index`` on the ``<ui>`` node when non-zero.

    Additional game-specific headers can be added via repeatable
    ``--include`` flags.
    """
    parser = argparse.ArgumentParser(
        prog="gen_ui.py create",
        description=(
            "Create a new UI XML template pre-populated with core "
            "Lavender includes and all built-in ui_func_signatures."
        ),
    )
    parser.add_argument(
        "output",
        help="Path to the output XML file to create.",
    )
    parser.add_argument(
        "--sub-dir",
        default="ui/implemented/generated/game/",
        help=(
            "Sub-directory under include/source for generated output "
            "(default: ui/implemented/generated/game/)."
        ),
    )
    parser.add_argument(
        "--source-name",
        default=None,
        help=(
            "C source name (without extension).  Defaults to the output "
            "filename stem."
        ),
    )
    parser.add_argument(
        "--platform",
        default="SDL",
        choices=["SDL", "NDS"],
        help="Target platform (default: SDL).",
    )
    parser.add_argument(
        "--size",
        default="256,192",
        help="Window size as W,H (default: 256,192).",
    )
    parser.add_argument(
        "--base-dir",
        default="./",
        help="Base directory for output paths (default: ./).",
    )
    parser.add_argument(
        "--offset-of-ui-index",
        type=int,
        default=0,
        help=(
            "Starting UI element ID offset.  Used to prevent ID collisions "
            "when multiple XML UIs are loaded simultaneously.  For example, "
            "if the HUD uses IDs 0-2, a screen that includes the HUD should "
            "set this to 3 so its own elements start at ID 3.  (default: 0)"
        ),
    )
    parser.add_argument(
        "--include",
        action="append",
        default=[],
        dest="extra_includes",
        metavar="HEADER_PATH",
        help=(
            "Additional header include path (repeatable).  Use this for "
            "game-specific headers, e.g. --include ui/ui_ag__slider.h"
        ),
    )

    opts = parser.parse_args(cli_args)

    source_name = opts.source_name or os.path.splitext(
        os.path.basename(opts.output)
    )[0]

    # Ensure sub_dir ends with /
    sub_dir = opts.sub_dir
    if sub_dir and not sub_dir.endswith("/"):
        sub_dir += "/"

    # Select platform-specific core sets
    if opts.platform == "NDS":
        core_includes = list(_CORE_INCLUDES_NDS)
        core_sigs = _CORE_SIGNATURES_NDS
    else:
        core_includes = list(_CORE_INCLUDES_SDL)
        core_sigs = _CORE_SIGNATURES_SDL

    # -- Build XML tree ----------------------------------------------------
    root = ET.Element("root")
    config_elem = ET.SubElement(root, "config")

    # <include sub_dir="...">
    include_elem = ET.SubElement(config_elem, "include")
    include_elem.set("sub_dir", sub_dir)

    for hdr in core_includes:
        h = ET.SubElement(include_elem, "header")
        h.set("path", hdr)

    # Extra (game-specific) includes
    for hdr in opts.extra_includes:
        h = ET.SubElement(include_elem, "header")
        h.set("path", hdr)

    # <output ...>
    output_elem = ET.SubElement(config_elem, "output")
    output_elem.set("base_dir", opts.base_dir)
    output_elem.set(
        "c_path", f"./source/{sub_dir}{source_name}.c"
    )
    output_elem.set(
        "h_path", f"./include/{sub_dir}{source_name}.h"
    )

    # <platform ...>
    platform_elem = ET.SubElement(config_elem, "platform")
    platform_elem.set("target", opts.platform)
    platform_elem.set("size", opts.size)

    # <ui_func_signature ...> for every core signature
    for tag_name, c_sigs in core_sigs:
        sig = ET.SubElement(config_elem, "ui_func_signature")
        sig.set("for", tag_name)
        if c_sigs:
            sig.set("c_signatures", c_sigs)

    # <ui ...>
    ui_elem = ET.SubElement(root, "ui")
    if opts.offset_of_ui_index != 0:
        ui_elem.set(
            "offset_of__ui_index", str(opts.offset_of_ui_index)
        )

    # -- Pretty-print and write --------------------------------------------
    _indent_xml(root)

    tree = ET.ElementTree(root)
    os.makedirs(os.path.dirname(os.path.abspath(opts.output)), exist_ok=True)
    ET.indent(tree, space="  ")
    tree.write(opts.output, encoding="utf-8", xml_declaration=True)

    print(f"Created: {opts.output}")
    print(f"  source_name:          {source_name}")
    print(f"  platform:             {opts.platform}")
    print(f"  size:                 {opts.size}")
    print(f"  sub_dir:              {sub_dir}")
    print(f"  offset_of__ui_index:  {opts.offset_of_ui_index}")
    print(f"  core includes:        {len(core_includes)}")
    print(f"  extra includes:       {len(opts.extra_includes)}")
    print(f"  core signatures:      {len(core_sigs)}")


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] != "create":
        print(
            "Usage:\n"
            "  gen_ui.py create <output.xml> [options...]\n"
            "\n"
            "Run 'gen_ui.py create --help' for scaffolding options.\n"
            "\n"
            "For C code generation from an existing UI XML, use\n"
            "gen_ui_code.py instead."
        )
        sys.exit(1)

    create_xml(sys.argv[2:])


if __name__ == "__main__":
    main()
