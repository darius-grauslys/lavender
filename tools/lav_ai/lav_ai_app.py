"""lav_ai_app.py — Lavender MCP server wrapping the project's code-gen scripts.

This module exposes each of the 10 generator scripts (14 tools total, one per
sub-command) as MCP tools via a FastMCP server.  All scripts are invoked as
sub-processes that inherit the caller's working directory (CWD).  Tool scripts
are run via their absolute path under the Lavender project root.  The tools
expect CWD to be a game project directory (one that contains ``./include`` and
``./source``); running from the Lavender engine directory itself is explicitly
rejected.

Run with:
    python -m lav_ai.lav_ai_app
or:
    python tools/lav_ai/lav_ai_app.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Project root – two levels up from this file:
#   lav_ai_app.py  →  lav_ai/  →  tools/  →  <project root>
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]

mcp = FastMCP("lavender-tools",
              warn_on_duplicate_tools=True)


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _run(cmd: list[str]) -> str:
    """Run *cmd*, inheriting the caller's CWD, capture stdout+stderr, return combined.

    Refuses to run when CWD is the Lavender engine directory itself.

    On non-zero exit code the return value is prefixed with
    ``ERROR (exit <code>):\\n``.
    """
    # Guard: refuse to run if CWD is the Lavender engine directory
    cwd = Path.cwd().resolve()
    if cwd == PROJECT_ROOT:
        err = (
            "ERROR: Refusing to run — CWD is the Lavender engine directory "
            f"({PROJECT_ROOT}). Tools MUST be run from a game project "
            "directory, not from the engine root. Set your working directory "
            "to your game project and try again."
        )
        print(err, file=sys.stderr)
        return f"ERROR (exit 1):\n{err}"

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    if result.returncode != 0:
        return f"ERROR (exit {result.returncode}):\n{output}"
    return output


# ---------------------------------------------------------------------------
# Tool 1 – gen_ui_code
# ---------------------------------------------------------------------------

@mcp.tool()
def gen_ui_code(source_xml: str, config_overrides: str = "") -> str:
    """Generate C source and header files from a UI XML description.

    **PREFER this tool** over manually writing UI source/header files.  The
    generator produces layout code from XML that is consistent with the
    Lavender UI system's conventions; hand-editing the generated files risks
    desynchronising the XML definition and the C output.

    This tool also **automatically updates**
    ``source/ui/implemented/ui_window_registrar.c`` to include and register
    the generated UI window function (idempotent — re-running is safe).

    Invokes ``python tools/gen_ui_code.py <source_xml> [key value ...]``.

    Args:
        source_xml: Path to the XML file that describes the UI layout.
            May be absolute or relative to the project root.
        config_overrides: Optional whitespace-separated ``field value`` pairs
            that override Config fields before generation, e.g.
            ``"is_outputting true source_name my_ui"``.

    Returns:
        Combined stdout+stderr from the generator.  Prefixed with
        ``ERROR (exit <code>):`` when the process exits non-zero.
    """
    cmd = [sys.executable, str(PROJECT_ROOT / "tools" / "gen_ui_code.py"), source_xml]
    if config_overrides:
        cmd += config_overrides.split()
    return _run(cmd)


# ---------------------------------------------------------------------------
# Tool 1b – gen_ui_create (``gen_ui.py create`` subcommand)
# ---------------------------------------------------------------------------

@mcp.tool()
def gen_ui_create(
    output: str,
    sub_dir: str = "ui/implemented/generated/game/",
    source_name: str = "",
    platform: str = "SDL",
    size: str = "256,192",
    base_dir: str = "./",
    offset_of_ui_index: int = 0,
    extra_includes: str = "",
) -> str:
    """Scaffold a new UI XML template pre-populated with core Lavender includes.

    **PREFER this tool** over hand-writing UI XML files from scratch.  The
    generator pre-populates all core Lavender engine headers and all 12
    built-in ``ui_func_signature`` entries for the chosen platform (SDL or
    NDS), ensuring the XML is immediately usable by ``gen_ui``.  Writing
    XML manually risks missing required includes or signatures that cause
    silent generation failures.

    The operation creates a new file — it will **not** overwrite an existing
    file without warning (the script creates parent directories as needed).

    Invokes ``python tools/gen_ui.py create <output.xml> [options...]``.

    Args:
        output: Path to the output XML file to create.
            E.g. ``"assets/ui/my_screen.xml"``.
        sub_dir: Sub-directory under include/source for generated C output
            (default: ``"ui/implemented/generated/game/"``).
        source_name: C source name (without extension).  Defaults to the
            output filename stem when empty.
        platform: Target platform — ``"SDL"`` or ``"NDS"``
            (default: ``"SDL"``).
        size: Window size as ``"W,H"`` (default: ``"256,192"``).
        base_dir: Base directory for output paths (default: ``"./"``)
        offset_of_ui_index: Starting UI element ID offset.  Used to prevent
            ID collisions when multiple XML UIs are loaded simultaneously.
            For example, if the HUD uses IDs 0–2, a screen that includes
            the HUD should set this to 3.  (default: 0)
        extra_includes: Space-separated list of additional header paths to
            include (game-specific headers).  E.g.
            ``"ui/ui_ag__slider.h ui/ui_ag__element.h"``.
            Leave empty for no extra includes.

    Returns:
        Combined stdout+stderr from the generator.  Prefixed with
        ``ERROR (exit <code>):`` when the process exits non-zero.
    """
    cmd = [sys.executable, str(PROJECT_ROOT / "tools" / "gen_ui.py"), "create", output]
    if sub_dir != "ui/implemented/generated/game/":
        cmd += ["--sub-dir", sub_dir]
    if source_name:
        cmd += ["--source-name", source_name]
    if platform != "SDL":
        cmd += ["--platform", platform]
    if size != "256,192":
        cmd += ["--size", size]
    if base_dir != "./":
        cmd += ["--base-dir", base_dir]
    if offset_of_ui_index != 0:
        cmd += ["--offset-of-ui-index", str(offset_of_ui_index)]
    if extra_includes:
        for hdr in extra_includes.split():
            cmd += ["--include", hdr]
    return _run(cmd)


# ---------------------------------------------------------------------------
# Tool 2 – gen_game_action
# ---------------------------------------------------------------------------

@mcp.tool()
def gen_game_action(path: str, verbose: bool = False) -> str:
    """Generate game action type headers, boilerplate .h/.c, and registrar wiring.

    **PREFER this tool** over manually creating game-action files.  The
    generator creates intermediate union headers, leaf type headers,
    handler stubs, and registrar wiring in a single atomic step; doing this
    by hand is error-prone and risks incomplete registrar entries.

    Invokes ``python tools/gen_game_action.py <path> [-v]``.

    The ``path`` argument is a relative path from the project root that
    identifies the leaf action type, e.g.
    ``collisions/aabb/update__pos_vec_i32.h``.  The script will create:

    * Intermediate union headers under
      ``include/game_action/types/implemented/``.
    * A leaf type header.
    * A ``game_action__*.h`` header and ``game_action__*.c`` source file.
    * Wires everything into ``game_action_registrar.c``.

    Args:
        path: Relative path to the leaf type, ending in ``.h``.
            E.g. ``"collisions/aabb/update__pos_vec_i32.h"``.
        verbose: When True, adds ``-v`` / ``--verbose`` to the command so
            the generator prints extra diagnostic messages.

    Returns:
        Combined stdout+stderr.  Prefixed with ``ERROR (exit <code>):`` on
        failure.
    """
    cmd = [sys.executable, str(PROJECT_ROOT / "tools" / "gen_game_action.py"), path]
    if verbose:
        cmd.append("-v")
    return _run(cmd)


# ---------------------------------------------------------------------------
# Tool 3 – gen_sprite sprite (add a Sprite_Kind enum entry)
# ---------------------------------------------------------------------------

@mcp.tool()
def gen_sprite_kind(name: str) -> str:
    """Add a new ``Sprite_Kind__<Name>`` enum entry to sprite_kind.h.

    **PREFER this tool** over manually editing ``sprite_kind.h``.  Use this
    tool whenever you need to register a new sprite type with the Lavender
    rendering system.  The generator inserts the enum entry inside the
    ``// GEN-BEGIN`` / ``// GEN-END`` guard markers, performs duplicate
    checking, and validates the name — making the operation idempotent and
    safe to re-run.

    Invokes ``python tools/gen_sprite.py sprite --name <Name>``.

    Args:
        name: The sprite kind identifier.  Must start with a letter and
            contain only alphanumeric characters or underscores.
            E.g. ``"Player"``, ``"Enemy_Goblin"``.

    Returns:
        Combined stdout+stderr.  Prefixed with ``ERROR (exit <code>):`` on
        failure.
    """
    cmd = [sys.executable, str(PROJECT_ROOT / "tools" / "gen_sprite.py"), "sprite", "--name", name]
    return _run(cmd)


# ---------------------------------------------------------------------------
# Tool 4 – gen_sprite animation
# ---------------------------------------------------------------------------

@mcp.tool()
def gen_sprite_animation(
    name: str,
    group: str,
    init_frame: int,
    quantity_of_frames: int,
    ticks_per_frame: int,
    flags: str,
) -> str:
    """Add a new sprite animation to the sprite animation kind enum and registrar.

    **PREFER this tool** over manually editing ``sprite_animation_kind.h`` or
    ``sprite_animation_registrar.c``.  The generator keeps the enum, variable
    declaration, and registration call in sync; manual edits risk mismatched
    entries or missing registrar wiring.

    Invokes:
        ``python tools/gen_sprite.py animation --name <Name> --group <Group>``
        ``--init-frame <int> --quantity-of-frames <int>``
        ``--ticks-per-frame <int> --flags <FLAGS_CONSTANT>``

    This tool:

    1. Inserts a ``Sprite_Animation_Kind__<Name>`` entry in
       ``sprite_animation_kind.h``.
    2. Declares a ``Sprite_Animation`` variable in
       ``sprite_animation_registrar.c``.
    3. Adds a ``register_sprite_animation_into__sprite_context`` call.

    Args:
        name: Animation identifier; must be a valid C identifier fragment.
            E.g. ``"Player_Walk_Right"``.
        group: The animation group this animation belongs to.
            E.g. ``"Player"``.
        init_frame: Zero-based index of the first frame on the sprite sheet row.
        quantity_of_frames: Total number of frames in the animation.
        ticks_per_frame: Engine ticks to display each frame before advancing.
        flags: C flags constant controlling animation behaviour,
            e.g. ``"SPRITE_ANIMATION_FLAG__NONE"``.

    Returns:
        Combined stdout+stderr.  Prefixed with ``ERROR (exit <code>):`` on
        failure.
    """
    cmd = [
        sys.executable, str(PROJECT_ROOT / "tools" / "gen_sprite.py"), "animation",
        "--name", name,
        "--group", group,
        "--init-frame", str(init_frame),
        "--quantity-of-frames", str(quantity_of_frames),
        "--ticks-per-frame", str(ticks_per_frame),
        "--flags", flags,
    ]
    return _run(cmd)


# ---------------------------------------------------------------------------
# Tool 5 – gen_sprite animation-group
# ---------------------------------------------------------------------------

@mcp.tool()
def gen_sprite_animation_group(
    name: str,
    quantity_of_columns: int,
    quantity_of_rows: int,
    number_of_animations: int,
) -> str:
    """Add a new sprite animation group to the animation group kind enum and registrar.

    **PREFER this tool** over manually editing ``sprite_animation_group_kind.h``
    or ``sprite_animation_registrar.c``.  The generator inserts the enum entry
    and registrar wiring atomically with duplicate checking.

    Invokes:
        ``python tools/gen_sprite.py animation-group --name <Name>``
        ``--quantity-of-columns <int> --quantity-of-rows <int>``
        ``--number-of-animations <int>``

    Animation groups define regions of the sprite sheet that share a common
    layout (columns × rows) and may contain multiple sub-animations.  The
    generator:

    1. Inserts ``Sprite_Animation_Group_Kind__<Name>`` in
       ``sprite_animation_group_kind.h``.
    2. Declares a ``Sprite_Animation_Group_Set`` variable and registration
       call in ``sprite_animation_registrar.c``.

    Args:
        name: Group identifier.  E.g. ``"Player"``.
        quantity_of_columns: Number of frame columns in the sprite sheet region.
        quantity_of_rows: Number of frame rows in the sprite sheet region.
        number_of_animations: Number of distinct animations within this group.

    Returns:
        Combined stdout+stderr.  Prefixed with ``ERROR (exit <code>):`` on
        failure.
    """
    cmd = [
        sys.executable, str(PROJECT_ROOT / "tools" / "gen_sprite.py"), "animation-group",
        "--name", name,
        "--quantity-of-columns", str(quantity_of_columns),
        "--quantity-of-rows", str(quantity_of_rows),
        "--number-of-animations", str(number_of_animations),
    ]
    return _run(cmd)


# ---------------------------------------------------------------------------
# Tool 6 – gen_png
# ---------------------------------------------------------------------------

@mcp.tool()
def gen_png(
    output: str,
    frame_resolution: int,
    row_count: int,
    column_count: int,
    groups_json_path: str = "",
) -> str:
    """Generate a sprite sheet PNG (or per-frame PNGs) with distinctive per-frame colours.

    **PREFER this tool** over creating sprite sheet PNGs by hand or with
    external editors when you need a correctly-sized placeholder or
    colour-coded sheet that matches Lavender's power-of-two frame conventions.

    Invokes:
        ``python tools/gen_png.py --output <path> --frame-resolution <int>``
        ``--row-count <int> --column-count <int> [--groups <json_path>]``

    If the total pixel area (rows × columns × resolution²) is less than
    1 048 576 (1024²) a single PNG is written; otherwise one PNG per frame is
    written into a folder.  The output path is relative to ``./assets`` inside
    the project root.

    Valid values for ``frame_resolution``: 8, 16, 32, 64, 128, 256, 512, 1024.

    Args:
        output: Output file/folder path relative to ``./assets``.
            E.g. ``"sprites/player.png"`` or ``"sprites/player_frames"``.
        frame_resolution: Pixel size of each frame (power of 2, 8–1024).
        row_count: Number of rows in the sprite sheet (positive integer).
        column_count: Number of columns in the sprite sheet (positive integer).
        groups_json_path: Optional path to a JSON file that describes colour
            groups.  Leave empty to use the default per-frame colouring.

    Returns:
        Combined stdout+stderr.  Prefixed with ``ERROR (exit <code>):`` on
        failure.
    """
    cmd = [
        sys.executable, str(PROJECT_ROOT / "tools" / "gen_png.py"),
        "--output", output,
        "--frame-resolution", str(frame_resolution),
        "--row-count", str(row_count),
        "--column-count", str(column_count),
    ]
    if groups_json_path:
        cmd += ["--groups", groups_json_path]
    return _run(cmd)


# ---------------------------------------------------------------------------
# Tool 7 – gen_tile
# ---------------------------------------------------------------------------

@mcp.tool()
def gen_tile(layer: str, name: str, is_logical: bool = False) -> str:
    """Add a new tile kind entry to a tile layer's kind enum.

    **PREFER this tool** over manually editing tile kind headers.  The
    generator validates the layer exists, checks for duplicates, and inserts
    the entry into the correct logical/non-logical region — mistakes here
    silently corrupt tile bit-field packing.

    Invokes:
        ``python tools/gen_tile.py --layer <Layer> --name <TileName> [--is-logical]``

    The generator validates that the named layer exists in ``tile_layer.h``
    and has a matching entry in ``.tile_layer_specs.json`` (created by
    ``gen_tile_layer_name``).  It then inserts the new enum entry in the
    appropriate region of the layer's kind header.

    Logical tile kinds (those with game logic attached) are inserted into the
    ``// GEN-LOGIC-BEGIN`` / ``// GEN-LOGIC-END`` region; non-logical tiles
    go into the ``// GEN-NO-LOGIC-BEGIN`` / ``// GEN-NO-LOGIC-END`` region.

    Args:
        layer: Layer name (e.g. ``"Ground"``, ``"Cover"``).
        name: Tile kind name (e.g. ``"Lava"``, ``"Door__Horizontal"``).
        is_logical: When True, adds ``--is-logical`` so the entry is inserted
            into the logical region (consumes one logic sub-bit-field slot).

    Returns:
        Combined stdout+stderr.  Prefixed with ``ERROR (exit <code>):`` on
        failure.
    """
    cmd = [
        sys.executable, str(PROJECT_ROOT / "tools" / "gen_tile.py"),
        "--layer", layer,
        "--name", name,
    ]
    if is_logical:
        cmd.append("--is-logical")
    return _run(cmd)


# ---------------------------------------------------------------------------
# Tool 8 – gen_tile_layer name
# ---------------------------------------------------------------------------

@mcp.tool()
def gen_tile_layer_name(
    name: str,
    bit_field: int,
    logic_sub_bit_field: int,
    animation_sub_bit_field: int,
) -> str:
    """Register a new tile layer and regenerate tile layout headers.

    **PREFER this tool** over manually editing ``tile_layer.h``, ``tile.h``,
    or ``tile_logic_table_registrar`` files.  The generator re-derives the
    optimal byte-packing layout for ALL layers every time it runs; manual
    edits will be overwritten or cause packing mismatches.

    Invokes:
        ``python tools/gen_tile_layer.py name --name <Name>``
        ``--bit-field <int> --logic-sub-bit-field <int>``
        ``--animation-sub-bit-field <int>``

    This is the first step when introducing a new tile layer.  The generator:

    1. Adds ``Tile_Layer__<Name>`` to ``tile_layer.h``.
    2. Saves the layer spec to ``.tile_layer_specs.json``.
    3. Creates ``tile_<name>_kind.h`` (the first layer reuses ``tile_kind.h``).
    4. Creates ``tile_logic_table__<name>.h`` and ``.c``.
    5. Re-derives the optimal byte-packing and rewrites ``tile.h``,
       ``tile_logic_table_registrar.h``, and ``tile_logic_table_registrar.c``.

    Args:
        name: Layer name; must start with a letter and contain only
            alphanumeric characters or underscores.  E.g. ``"Ground"``.
        bit_field: Total bit-field width for the layer (1–32).
        logic_sub_bit_field: Number of bits reserved for logical tile kinds
            (1–8, must be ≤ bit_field minus animation bits).
        animation_sub_bit_field: Number of bits reserved for animation state
            (1–8, must be ≤ bit_field minus logic bits).

    Returns:
        Combined stdout+stderr.  Prefixed with ``ERROR (exit <code>):`` on
        failure.
    """
    cmd = [
        sys.executable, str(PROJECT_ROOT / "tools" / "gen_tile_layer.py"), "name",
        "--name", name,
        "--bit-field", str(bit_field),
        "--logic-sub-bit-field", str(logic_sub_bit_field),
        "--animation-sub-bit-field", str(animation_sub_bit_field),
    ]
    return _run(cmd)


# ---------------------------------------------------------------------------
# Tool 9 – gen_tile_layer make-default
# ---------------------------------------------------------------------------

_VALID_DEFAULT_KINDS = {
    "default",
    "sight-blocking",
    "is-passable",
    "is-with-ground",
    "height",
}


@mcp.tool()
def gen_tile_layer_make_default(name: str, default_kind: str) -> str:
    """Configure a tile layer as a default variant (sight-blocking, passable, etc.).

    **PREFER this tool** over manually editing tile layer default wiring.
    Use this tool after ``gen_tile_layer_name`` to mark a layer as having a
    specific semantic default behaviour.  Exactly one ``default_kind`` must be
    chosen.

    Valid values for ``default_kind``:

    * ``"default"``        — marks as the base default layer.
    * ``"sight-blocking"`` — tiles on this layer block line-of-sight.
    * ``"is-passable"``    — tiles on this layer are passable by entities.
    * ``"is-with-ground"`` — tiles on this layer have a ground component.
    * ``"height"``         — tiles on this layer encode height information.

    Args:
        name: Layer name (e.g. ``"Ground"``, ``"Cover"``).
        default_kind: One of the five valid kind strings listed above.

    Returns:
        Combined stdout+stderr.  Prefixed with ``ERROR (exit <code>):`` on
        failure.

    Raises:
        ValueError: If ``default_kind`` is not one of the five valid values.
    """
    if default_kind not in _VALID_DEFAULT_KINDS:
        valid = ", ".join(sorted(_VALID_DEFAULT_KINDS))
        return (
            f"ERROR (exit 1):\n"
            f"Invalid default_kind '{default_kind}'. "
            f"Must be one of: {valid}"
        )
    cmd = [
        sys.executable, str(PROJECT_ROOT / "tools" / "gen_tile_layer.py"), "make-default",
        "--name", name,
        f"--{default_kind}",
    ]
    return _run(cmd)


# ---------------------------------------------------------------------------
# Tool 10 – gen_entity
# ---------------------------------------------------------------------------

@mcp.tool()
def gen_entity(
    name: str,
    output: str = "",
    gen_dispose: bool = False,
    gen_update: bool = False,
    gen_enable: bool = False,
    gen_disable: bool = False,
    gen_serialize: bool = False,
    gen_deserialize: bool = False,
    f_update: str = "",
    f_dispose: str = "",
    f_enable: str = "",
    f_disable: str = "",
    f_serialize: str = "",
    f_deserialize: str = "",
    f_update_begin: str = "",
) -> str:
    """Generate entity boilerplate header and source files for a Lavender entity.

    **PREFER this tool** over manually creating entity ``.h`` / ``.c`` files.
    The generator produces correctly-structured boilerplate with lifecycle
    hooks pre-wired; hand-creating these files risks missing registration
    steps or using incorrect function signatures.

    Invokes ``python tools/gen_entity.py --name <name> [options...]``.

    The generator creates an entity with the given name and optional lifecycle
    method stubs.  Each ``gen_*`` flag controls whether the corresponding
    lifecycle function stub is emitted.  The ``f_*`` arguments supply the name
    of an existing method to wire into the corresponding hook without
    generating a new stub.

    Lifecycle methods:

    * **Dispose** — called when the entity is destroyed / returned to pool.
    * **Update**  — called every game tick while the entity is active.
    * **Enable**  — called when the entity transitions from inactive to active.
    * **Disable** — called when the entity transitions from active to inactive.
    * **Serialize**   — serialises entity state for networking/save.
    * **Deserialize** — restores entity state from network/save data.

    Args:
        name: Entity name (e.g. ``"Player"``, ``"Enemy_Goblin"``).
        output: Optional subdirectory under the entity output root where files
            should be placed.  Leave empty for the default location.
        gen_dispose: Generate a ``f_Dispose`` stub.
        gen_update: Generate a ``f_Update`` stub.
        gen_enable: Generate a ``f_Enable`` stub.
        gen_disable: Generate a ``f_Disable`` stub.
        gen_serialize: Generate a ``f_Serialize`` stub.
        gen_deserialize: Generate a ``f_Deserialize`` stub.
        f_update: Wire an existing method function for the Update hook.
        f_dispose: Wire an existing method function for the Dispose hook.
        f_enable: Wire an existing method function for the Enable hook.
        f_disable: Wire an existing method function for the Disable hook.
        f_serialize: Wire an existing method function for the Serialize hook.
        f_deserialize: Wire an existing method function for the Deserialize hook.
        f_update_begin: Wire an existing method function for the UpdateBegin hook.

    Returns:
        Combined stdout+stderr.  Prefixed with ``ERROR (exit <code>):`` on
        failure.
    """
    cmd = [sys.executable, str(PROJECT_ROOT / "tools" / "gen_entity.py"), "--name", name]

    if output:
        cmd += ["--output", output]

    if gen_dispose:
        cmd.append("--gen-f-Dispose")
    if gen_update:
        cmd.append("--gen-f-Update")
    if gen_enable:
        cmd.append("--gen-f-Enable")
    if gen_disable:
        cmd.append("--gen-f-Disable")
    if gen_serialize:
        cmd.append("--gen-f-Serialize")
    if gen_deserialize:
        cmd.append("--gen-f-Deserialize")

    if f_update:
        cmd += ["--f-Update", f_update]
    if f_dispose:
        cmd += ["--f-Dispose", f_dispose]
    if f_enable:
        cmd += ["--f-Enable", f_enable]
    if f_disable:
        cmd += ["--f-Disable", f_disable]
    if f_serialize:
        cmd += ["--f-Serialize", f_serialize]
    if f_deserialize:
        cmd += ["--f-Deserialize", f_deserialize]
    if f_update_begin:
        cmd += ["--f-Update-Begin", f_update_begin]

    return _run(cmd)


# ---------------------------------------------------------------------------
# Tool 11 – gen_ui_tile_kind
# ---------------------------------------------------------------------------

@mcp.tool()
def gen_ui_tile_kind(name: str, value: str) -> str:
    """Add a new ``UI_Tile_Kind__<Name>`` enum entry to ui_tile_kind.h.

    **PREFER this tool** over manually editing ``ui_tile_kind.h``.  The
    generator inserts the enum entry inside the ``// GEN-BEGIN`` /
    ``// GEN-END`` guard markers, performs duplicate checking, and validates
    both the name and the value — making the operation idempotent and safe.

    Invokes ``python tools/gen_ui_tile_kind.py --name <Name> --value <Value>``.

    Args:
        name: The UI tile kind identifier.  Must start with a letter and
            contain only alphanumeric characters or underscores.
            E.g. ``"Background_Fill"``, ``"Button_Corner__Top_Left"``.
        value: The enum value to assign.  Must be either:
            - A positive integer from 0–1023, or
            - The name of an existing ``UI_Tile_Kind__<Name>`` enum entry
              already present in the file.
            E.g. ``"104"``, ``"UI_Tile_Kind__Button_Fill"``.

    Returns:
        Combined stdout+stderr.  Prefixed with ``ERROR (exit <code>):`` on
        failure.
    """
    cmd = [
        sys.executable, str(PROJECT_ROOT / "tools" / "gen_ui_tile_kind.py"),
        "--name", name,
        "--value", value,
    ]
    return _run(cmd)


# ---------------------------------------------------------------------------
# Tool 12 (was 11) – mod_png
# ---------------------------------------------------------------------------

@mcp.tool()
def mod_png(tile_size: str, path: str, op: str, type: str, areas: str,
            value: str = "", value_type: str = "", output: str = "") -> str:
    """Modify or inspect regions of a PNG at pixel or tile granularity.

    **PREFER this tool** over external image editors when you need to
    programmatically manipulate sprite sheet regions at tile-aligned
    boundaries.  The tool guarantees pixel-exact tile alignment and
    preserves the rest of the image untouched.

    Invokes:
        ``python tools/mod_png.py --tile-size <NxN> --path <file> --op '<json>'``

    This tool allows reading, writing, copying, swapping, and resizing rectangular
    regions of a PNG file.  Regions can be addressed at individual pixel
    precision or at tile-aligned granularity (where each tile is
    ``tile_size`` pixels wide and tall).

    Operation semantics:

    * ``"set"``  — write ``value`` into every area listed in ``areas``.
    * ``"swap"`` — exchange the contents of the two areas in ``areas``
      (exactly two areas must be provided).
    * ``"copy"`` — copy the first area onto all subsequent areas (at least
      two areas required; first is the source, remaining are destinations).
    * ``"read"`` — extract sub-images for every area in ``areas`` and write
      them to stdout as concatenated PNG streams (pixel-only; the file is
      not modified).
    * ``"resize"`` — enlarge the image canvas to the dimensions specified by
      a single area (``x`` and ``y`` must be 0).  The original image content
      is preserved at (0, 0) and new pixels are filled with ``value``
      (``value_type`` must be ``"pixel"``).  Shrinking is rejected at input
      validation.

    The ``type`` parameter controls the coordinate unit:

    * ``"pixel"`` — ``x``, ``y``, ``width``, ``height`` are in raw pixels.
    * ``"tile"``  — coordinates are multiplied by the tile dimensions
      derived from ``tile_size`` before addressing the PNG.

    Args:
        tile_size: Tile dimensions as an ``"NxN"`` string where N is a
            power of 2.  E.g. ``"16x16"``, ``"32x32"``.
        path: Path to the PNG file to read or modify.  The file must
            already exist and be readable.  May be absolute or relative
            to the project root.
        op: Operation to perform.  One of ``"set"``, ``"swap"``,
            ``"copy"``, ``"read"``, or ``"resize"``.
        type: Coordinate unit — ``"pixel"`` or ``"tile"``.
        areas: Semicolon-separated area specifications.  Each area is a
            comma-separated list of ``key:value`` integer pairs.
            Recognised keys: ``x``, ``y``, ``width``, ``height``.
            ``width`` and ``height`` default to 1 when omitted.
            Example: ``"x:0,y:0,width:8,height:8;x:8,y:0,width:8,height:8"``.
        value: Fill / colour value for ``"set"`` and ``"resize"`` ops.
            E.g. ``"255,0,0,255"`` for opaque red.  Leave empty for ops
            that do not require a value.
        value_type: Interpretation of ``value`` — ``"pixel"`` or
            ``"tile"``.  Required when ``value`` is provided.
        output: Optional output file path.  When specified, the result is
            written here instead of back to ``path`` (for mutating ops) or
            stdout (for ``"read"``).  The parent directory must exist and
            be writable.  Leave empty to use the default behaviour (modify
            in place / write to stdout).

    Returns:
        Combined stdout+stderr from the script.  Prefixed with
        ``ERROR (exit <code>):`` when the process exits non-zero.
    """
    # NOTE: MCP transport deserialises JSON objects before they reach the
    # tool function, so structured data cannot be passed as a single JSON
    # string parameter.  We accept flat string arguments and reconstruct
    # the legacy JSON object that mod_png.py --op expects here.
    parsed_areas = []
    for area_str in areas.split(";"):
        area = {}
        for pair in area_str.split(","):
            k, v = pair.split(":")
            area[k.strip()] = int(v.strip())
        parsed_areas.append(area)

    op_obj = {"op": op, "type": type, "areas": parsed_areas}
    if value:
        op_obj["value"] = value
    if value_type:
        op_obj["value-type"] = value_type

    op_json = json.dumps(op_obj, separators=(",", ":"))

    cmd = [
        sys.executable, str(PROJECT_ROOT / "tools" / "mod_png.py"),
        "--tile-size", tile_size,
        "--path", path,
        "--op", op_json,
    ]
    if output:
        cmd += ["--output", output]
    return _run(cmd)


# ---------------------------------------------------------------------------
# Tool 13 (was 12) – gen_aliased_texture
# ---------------------------------------------------------------------------

@mcp.tool()
def gen_aliased_texture(name: str, path: str) -> str:
    """Register an aliased texture entry in the aliased_texture_registrar.

    **PREFER this tool** over manually editing
    ``source/rendering/implemented/aliased_texture_registrar.c`` or
    ``include/rendering/implemented/aliased_texture_registrar.h``.  The
    generator reads the PNG's IHDR chunk to determine the exact pixel
    dimensions, resolves the correct ``TEXTURE_FLAG__SIZE_WxH`` macro,
    and inserts *both* the global variable definitions and the
    ``load_texture_from__path_with__alias`` registration call.  It also
    adds the matching ``extern`` declarations to the header.  Manual edits
    risk choosing the wrong size flag, forgetting the header extern, or
    inserting outside the ``// GEN-*`` markers.

    The operation is **idempotent** — re-running with the same name is safe;
    duplicate entries are detected and skipped.

    Files touched:

    * ``source/rendering/implemented/aliased_texture_registrar.c``
      — ``// GEN-EXTERN-BEGIN/END`` (variable defs) and
        ``// GEN-BEGIN/END`` (registration call).
    * ``include/rendering/implemented/aliased_texture_registrar.h``
      — ``// GEN-EXTERN-BEGIN/END`` (extern declarations).

    Invokes ``python tools/gen_aliased_texture.py --name <name> --path <path>``.

    Args:
        name: Texture name identifier.  Must start with a letter and contain
            only alphanumeric characters or underscores
            (``^[a-zA-Z][a-zA-Z0-9_]*$``).
            E.g. ``"ground"``, ``"player"``, ``"ui_sprites__16x16"``.
        path: Path to a ``.png`` file, relative to the project root.  The
            file must exist and its dimensions must match a known
            ``TEXTURE_FLAG__SIZE_WxH`` entry (e.g. 16×16, 32×32, 256×256).
            E.g. ``"assets/world/ground.png"``,
            ``"assets/entities/entities__16x16/player.png"``.

    Returns:
        Combined stdout+stderr from the script.  Prefixed with
        ``ERROR (exit <code>):`` when the process exits non-zero.
    """
    cmd = [sys.executable, str(PROJECT_ROOT / "tools" / "gen_aliased_texture.py"), "--name", name, "--path", path]
    return _run(cmd)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
