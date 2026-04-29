"""lav_ai_app.py — Lavender MCP server wrapping the project's code-gen scripts.

This module exposes each of the 13 generator/modifier/query scripts (28 tools
total, one per sub-command or operation mode) as MCP tools via a FastMCP server.
All scripts are invoked as sub-processes that inherit the caller's working
directory (CWD).  Tool scripts are run via their absolute path under the
Lavender project root.  The tools expect CWD to be a game project directory
(one that contains ``./include`` and ``./source``); running from the Lavender
engine directory itself is explicitly rejected.

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

    For Lavender-specific context on UI XML conventions, ID offset usage,
    and platform-specific signatures, consult available memory tooling.

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

    For Lavender-specific context on UI XML conventions, ID offset usage,
    and platform-specific signatures, consult available memory tooling.

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

    For Lavender-specific context on game action type hierarchies and
    existing registrar entries, consult available memory tooling.

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

    For Lavender-specific context on sprite naming conventions, animation
    layouts, and existing registrations, consult available memory tooling.

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

    For Lavender-specific context on sprite naming conventions, animation
    layouts, and existing registrations, consult available memory tooling.

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

    For Lavender-specific context on sprite naming conventions, animation
    layouts, and existing registrations, consult available memory tooling.

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

    For Lavender-specific context on sprite sheet layout conventions and
    frame resolution requirements, consult available memory tooling.

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

    For Lavender-specific context on tile layer specifications, bit-field
    configurations, and existing registrations, consult available memory
    tooling.

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

    For Lavender-specific context on tile layer specifications, bit-field
    configurations, and existing registrations, consult available memory
    tooling.

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

    For Lavender-specific context on tile layer specifications, bit-field
    configurations, and existing registrations, consult available memory
    tooling.

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

    For Lavender-specific context on entity lifecycle patterns, existing
    registrations, and naming conventions, consult available memory tooling.

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

    For Lavender-specific context on UI tile conventions and existing
    registrations, consult available memory tooling.

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
# Internal helper – mod_png command builder
# ---------------------------------------------------------------------------

_MOD_PNG_SCRIPT = str(PROJECT_ROOT / "tools" / "mod_png.py")


def _parse_areas(areas: str) -> list[dict]:
    """Parse semicolon-separated ``key:value`` area specs into dicts."""
    parsed = []
    for area_str in areas.split(";"):
        area = {}
        for pair in area_str.split(","):
            k, v = pair.split(":")
            area[k.strip()] = int(v.strip())
        parsed.append(area)
    return parsed


def _build_mod_png_op_cmd(
    path: str,
    tile_size: str,
    op: str,
    coord_type: str,
    areas: str,
    value: str = "",
    value_type: str = "",
    output: str = "",
) -> list[str]:
    """Build the full subprocess command list for a mod_png operation."""
    op_obj: dict = {"op": op, "type": coord_type, "areas": _parse_areas(areas)}
    if value:
        op_obj["value"] = value
    if value_type:
        op_obj["value-type"] = value_type

    cmd = [
        sys.executable, _MOD_PNG_SCRIPT,
        "--tile-size", tile_size,
        "--path", path,
        "--op", json.dumps(op_obj, separators=(",", ":")),
    ]
    if output:
        cmd += ["--output", output]
    return cmd


# ---------------------------------------------------------------------------
# Tool 12a – read_png_meta (image-info mode, read-only)
# ---------------------------------------------------------------------------

@mcp.tool()
def read_png_meta(path: str) -> str:
    """Return the format, pixel dimensions, and Base64-encoded contents of a PNG.

    **PREFER this tool** over manually inspecting PNG files.  This is a
    **read-only** operation — no files are modified.

    For Lavender-specific context on sprite sheet and tilesheet layout
    conventions, consult available memory tooling.

    Invokes ``python tools/mod_png.py --path <file>`` (image-info mode).

    Returns a two-line string::

        format=RGBA size=848x928
        base64=iVBORw0KGgoAAAANSUhEUgAA...

    The ``base64`` value is the complete PNG file in standard Base64
    (RFC 4648).

    Args:
        path: Path to the PNG file.  May be absolute or relative to the
            project root.

    Returns:
        Image metadata and Base64-encoded PNG data.  Prefixed with
        ``ERROR (exit <code>):`` on failure.
    """
    cmd = [sys.executable, _MOD_PNG_SCRIPT, "--path", path]
    return _run(cmd)


# ---------------------------------------------------------------------------
# Tool 12b – read_png (extract sub-images, read-only)
# ---------------------------------------------------------------------------

@mcp.tool()
def read_png(
    path: str,
    tile_size: str,
    type: str,
    areas: str,
    output: str = "",
) -> str:
    """Extract rectangular sub-images from a PNG without modifying it.

    **PREFER this tool** over external image editors when you need to
    extract specific regions of a sprite sheet or tilesheet for inspection.
    This is a **read-only** operation — no files are modified (unless
    ``output`` is specified, in which case the extracted image is written
    there).

    For Lavender-specific context on sprite sheet and tilesheet layout
    conventions, consult available memory tooling.

    Invokes ``python tools/mod_png.py`` with ``--op '{"op":"read",...}'``.

    Args:
        path: Path to the PNG file to read from.
        tile_size: Tile dimensions as ``"NxN"`` (power of 2).
            E.g. ``"16x16"``, ``"32x32"``.
        type: Coordinate unit — ``"pixel"`` or ``"tile"``.
        areas: Semicolon-separated area specs.  Each area is a
            comma-separated ``key:value`` list.
            E.g. ``"x:0,y:0,width:8,height:8"``.
        output: Optional output file path for the extracted image.
            Leave empty to write to stdout.

    Returns:
        Combined stdout+stderr.  Prefixed with ``ERROR (exit <code>):``
        on failure.
    """
    cmd = _build_mod_png_op_cmd(path, tile_size, "read", type, areas,
                                output=output)
    return _run(cmd)


# ---------------------------------------------------------------------------
# Tool 12c – mod_png_set (fill areas with colour/tile pattern)
# ---------------------------------------------------------------------------

@mcp.tool()
def mod_png_set(
    path: str,
    tile_size: str,
    type: str,
    areas: str,
    value: str,
    value_type: str,
) -> str:
    """Write a fill value into rectangular regions of a PNG.

    **PREFER this tool** over external image editors when you need to
    programmatically fill sprite sheet or tilesheet regions at tile-aligned
    boundaries.  The tool guarantees pixel-exact alignment and preserves
    the rest of the image untouched.

    For Lavender-specific context on sprite sheet and tilesheet layout
    conventions, consult available memory tooling.

    Mutating — the original file is preserved with an ``ORIGINAL_`` prefix
    and tracked in ``.lav_ai_mod_png.json``.

    Args:
        path: Path to the PNG file to modify.
        tile_size: Tile dimensions as ``"NxN"`` (power of 2).
            E.g. ``"16x16"``, ``"32x32"``.
        type: Coordinate unit — ``"pixel"`` or ``"tile"``.
        areas: Semicolon-separated area specs.
            E.g. ``"x:0,y:0,width:8,height:8;x:8,y:0,width:8,height:8"``.
        value: Fill colour, e.g. ``"255,0,0,255"`` for opaque red.
        value_type: Interpretation of *value* — ``"pixel"`` or ``"tile"``.

    Returns:
        Combined stdout+stderr.  Prefixed with ``ERROR (exit <code>):``
        on failure.
    """
    cmd = _build_mod_png_op_cmd(path, tile_size, "set", type, areas,
                                value=value, value_type=value_type)
    return _run(cmd)


# ---------------------------------------------------------------------------
# Tool 12d – mod_png_swap (exchange two areas)
# ---------------------------------------------------------------------------

@mcp.tool()
def mod_png_swap(path: str, tile_size: str, type: str, areas: str) -> str:
    """Exchange the contents of two rectangular regions in a PNG.

    **PREFER this tool** over external image editors for pixel-exact
    tile-aligned swaps.  Exactly two areas must be specified.

    For Lavender-specific context on sprite sheet and tilesheet layout
    conventions, consult available memory tooling.

    Mutating — the original file is preserved with an ``ORIGINAL_`` prefix
    and tracked in ``.lav_ai_mod_png.json``.

    Args:
        path: Path to the PNG file to modify.
        tile_size: Tile dimensions as ``"NxN"`` (power of 2).
        type: Coordinate unit — ``"pixel"`` or ``"tile"``.
        areas: Exactly two semicolon-separated area specs.
            E.g. ``"x:0,y:0,width:2,height:2;x:4,y:0,width:2,height:2"``.

    Returns:
        Combined stdout+stderr.  Prefixed with ``ERROR (exit <code>):``
        on failure.
    """
    cmd = _build_mod_png_op_cmd(path, tile_size, "swap", type, areas)
    return _run(cmd)


# ---------------------------------------------------------------------------
# Tool 12e – mod_png_copy (copy first area onto subsequent areas)
# ---------------------------------------------------------------------------

@mcp.tool()
def mod_png_copy(path: str, tile_size: str, type: str, areas: str) -> str:
    """Copy one rectangular region onto one or more destination regions.

    **PREFER this tool** over external image editors for pixel-exact
    tile-aligned copies.  The first area is the source; all subsequent
    areas are destinations (at least two areas required).

    For Lavender-specific context on sprite sheet and tilesheet layout
    conventions, consult available memory tooling.

    Mutating — the original file is preserved with an ``ORIGINAL_`` prefix
    and tracked in ``.lav_ai_mod_png.json``.

    Args:
        path: Path to the PNG file to modify.
        tile_size: Tile dimensions as ``"NxN"`` (power of 2).
        type: Coordinate unit — ``"pixel"`` or ``"tile"``.
        areas: Semicolon-separated area specs (first = source, rest =
            destinations).
            E.g. ``"x:0,y:0,width:2,height:2;x:4,y:0,width:2,height:2"``.

    Returns:
        Combined stdout+stderr.  Prefixed with ``ERROR (exit <code>):``
        on failure.
    """
    cmd = _build_mod_png_op_cmd(path, tile_size, "copy", type, areas)
    return _run(cmd)


# ---------------------------------------------------------------------------
# Tool 12f – mod_png_resize (enlarge canvas)
# ---------------------------------------------------------------------------

@mcp.tool()
def mod_png_resize(
    path: str,
    tile_size: str,
    areas: str,
    value: str,
    output: str = "",
) -> str:
    """Enlarge a PNG canvas, filling new pixels with a colour.

    **PREFER this tool** over external image editors when you need to grow
    a sprite sheet or tilesheet while preserving existing content at (0,0).
    Shrinking is rejected.

    For Lavender-specific context on sprite sheet and tilesheet layout
    conventions, consult available memory tooling.

    The area specifies the new dimensions (``x`` and ``y`` must be 0).
    The coordinate unit is always ``"pixel"``.

    Mutating — the original file is preserved with an ``ORIGINAL_`` prefix
    and tracked in ``.lav_ai_mod_png.json``.

    Args:
        path: Path to the PNG file to resize.
        tile_size: Tile dimensions as ``"NxN"`` (power of 2).
        areas: Single area spec for the new canvas size.
            E.g. ``"x:0,y:0,width:256,height:256"``.
        value: Fill colour for new pixels, e.g. ``"0,0,0,0"`` for
            transparent.
        output: Optional output file path.  Leave empty to modify in place.

    Returns:
        Combined stdout+stderr.  Prefixed with ``ERROR (exit <code>):``
        on failure.
    """
    cmd = _build_mod_png_op_cmd(path, tile_size, "resize", "pixel", areas,
                                value=value, value_type="pixel",
                                output=output)
    return _run(cmd)


# ---------------------------------------------------------------------------
# Tool 12g – mod_png_condense (pack non-fill tiles compactly)
# ---------------------------------------------------------------------------

@mcp.tool()
def mod_png_condense(
    path: str,
    tile_size: str,
    areas: str,
    value: str,
    output: str,
) -> str:
    """Pack non-fill tiles into the smallest near-square rectangle.

    **PREFER this tool** over manual tile rearrangement.  Identifies
    fill-only tiles within the specified area(s) and packs all non-fill
    tiles into a compact rectangle.  The image is cropped to its tight
    tile-aligned bounding box.

    For Lavender-specific context on sprite sheet and tilesheet layout
    conventions, consult available memory tooling.

    The coordinate unit is always ``"tile"``.  The ``output`` parameter is
    **required** and must reside in the same directory as ``path`` or a
    subdirectory thereof.  The basename must **not** start with
    ``ORIGINAL_``.

    Mutating — the original file is preserved with an ``ORIGINAL_`` prefix
    and tracked in ``.lav_ai_mod_png.json``.

    Args:
        path: Path to the PNG file to condense.
        tile_size: Tile dimensions as ``"NxN"`` (power of 2).
        areas: Semicolon-separated area specs (in tile coordinates)
            defining the region to condense.
        value: Fill colour that identifies empty tiles, e.g.
            ``"0,0,0,0"`` for transparent.
        output: **Required** output file path for the condensed image.

    Returns:
        Resulting image dimensions (``WxH``) on success.  Prefixed with
        ``ERROR (exit <code>):`` on failure.
    """
    cmd = _build_mod_png_op_cmd(path, tile_size, "condense", "tile", areas,
                                value=value, value_type="pixel",
                                output=output)
    return _run(cmd)


# ---------------------------------------------------------------------------
# Tool 13 – gen_aliased_texture
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

    For Lavender-specific context on texture naming conventions and size
    flag constants, consult available memory tooling.

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
# Tool 14 – query_tools_list (read-only MCP registry introspection)
# ---------------------------------------------------------------------------

@mcp.tool()
def query_tools_list() -> str:
    """List all registered MCP tool names in sorted order.

    Read-only introspection of the Lavender MCP tool registry.  Use this
    to discover what tools are available before planning invocations.

    For Lavender-specific context on tool registration patterns and naming
    conventions, consult available memory tooling.

    Returns:
        Sorted tool names, one per line.
    """
    cmd = [sys.executable, str(PROJECT_ROOT / "tools" / "lav_query_tools.py"), "list"]
    return _run(cmd)


# ---------------------------------------------------------------------------
# Tool 15 – query_tools_search (search tool names by regex)
# ---------------------------------------------------------------------------

@mcp.tool()
def query_tools_search(pattern: str) -> str:
    """Search registered MCP tool names by regex pattern.

    Read-only introspection.  Returns all tool names matching the pattern.

    For Lavender-specific context on tool registration patterns and naming
    conventions, consult available memory tooling.

    Args:
        pattern: Regex pattern to match against tool names.
            E.g. ``"mod_png.*"``, ``"gen_sprite"``, ``"query_.*"``.

    Returns:
        Matching tool names, one per line.  Prefixed with
        ``ERROR (exit <code>):`` if no matches or invalid regex.
    """
    cmd = [sys.executable, str(PROJECT_ROOT / "tools" / "lav_query_tools.py"),
           "search", "--pattern", pattern]
    return _run(cmd)


# ---------------------------------------------------------------------------
# Tool 16 – query_tools_describe (describe a tool's schema)
# ---------------------------------------------------------------------------

@mcp.tool()
def query_tools_describe(name: str) -> str:
    """Describe a registered MCP tool's parameter schema and summary.

    Read-only introspection.  Returns the tool's name, parameter JSON
    schema (with types and defaults), description length, and a summary
    of the first few lines of its description.

    For Lavender-specific context on tool registration patterns and naming
    conventions, consult available memory tooling.

    Args:
        name: Exact tool name.  E.g. ``"gen_entity"``, ``"mod_png_set"``.

    Returns:
        Tool metadata as structured text.  Prefixed with
        ``ERROR (exit <code>):`` if the tool is not found.
    """
    cmd = [sys.executable, str(PROJECT_ROOT / "tools" / "lav_query_tools.py"),
           "describe", "--name", name]
    return _run(cmd)


# ---------------------------------------------------------------------------
# Tool 17 – query_agents_list (list agent names from opencode.json)
# ---------------------------------------------------------------------------

@mcp.tool()
def query_agents_list() -> str:
    """List all agent names defined in the project's opencode.json.

    Read-only inspection of agent configurations.  Returns sorted agent
    names, one per line.

    For Lavender-specific context on agent architecture and permission
    patterns, consult available memory tooling.

    Returns:
        Sorted agent names, one per line.
    """
    cmd = [sys.executable, str(PROJECT_ROOT / "tools" / "lav_query_agents.py"),
           "list"]
    return _run(cmd)


# ---------------------------------------------------------------------------
# Tool 18 – query_agents_show (show agent details)
# ---------------------------------------------------------------------------

@mcp.tool()
def query_agents_show(agent: str) -> str:
    """Show an agent's description, model, mode, permissions, and prompt length.

    Read-only inspection of a single agent's configuration from
    opencode.json.

    For Lavender-specific context on agent architecture and permission
    patterns, consult available memory tooling.

    Args:
        agent: Agent name.  E.g. ``"planner"``, ``"spritesheet-animator"``.

    Returns:
        Agent metadata as structured text.  Prefixed with
        ``ERROR (exit <code>):`` if the agent is not found.
    """
    cmd = [sys.executable, str(PROJECT_ROOT / "tools" / "lav_query_agents.py"),
           "show", "--agent", agent]
    return _run(cmd)


# ---------------------------------------------------------------------------
# Tool 19 – query_agents_search_prompts (search prompt text)
# ---------------------------------------------------------------------------

@mcp.tool()
def query_agents_search_prompts(pattern: str, agent: str = "") -> str:
    """Search agent prompt text for a regex pattern with context snippets.

    Read-only inspection.  For each agent whose prompt matches, reports the
    match count and surrounding context.

    For Lavender-specific context on agent architecture and permission
    patterns, consult available memory tooling.

    Args:
        pattern: Regex pattern to search for in prompt text.
            E.g. ``"mod_png"``, ``"gen_entity.*name"``.
        agent: Optional agent name to restrict the search to a single agent.
            Leave empty to search all agents.

    Returns:
        Per-agent match counts and context snippets.  Prefixed with
        ``ERROR (exit <code>):`` if no matches found.
    """
    cmd = [sys.executable, str(PROJECT_ROOT / "tools" / "lav_query_agents.py"),
           "search-prompts", "--pattern", pattern]
    if agent:
        cmd += ["--agent", agent]
    return _run(cmd)


# ---------------------------------------------------------------------------
# Tool 20 – query_agents_search_permissions (search permission entries)
# ---------------------------------------------------------------------------

@mcp.tool()
def query_agents_search_permissions(pattern: str, agent: str = "") -> str:
    """Search agent permission keys and values for a regex pattern.

    Read-only inspection.  Returns all permission entries where the key or
    value matches the pattern.

    For Lavender-specific context on agent architecture and permission
    patterns, consult available memory tooling.

    Args:
        pattern: Regex pattern to match against permission keys/values.
            E.g. ``"lavender-tools_gen"``, ``"allow"``.
        agent: Optional agent name to restrict the search.
            Leave empty to search all agents.

    Returns:
        Matching permission entries as ``agent: key = value``.  Prefixed
        with ``ERROR (exit <code>):`` if no matches found.
    """
    cmd = [sys.executable, str(PROJECT_ROOT / "tools" / "lav_query_agents.py"),
           "search-permissions", "--pattern", pattern]
    if agent:
        cmd += ["--agent", agent]
    return _run(cmd)


# ---------------------------------------------------------------------------
# Tool 21 – query_agents_verify_clean (verify no stale references)
# ---------------------------------------------------------------------------

@mcp.tool()
def query_agents_verify_clean(pattern: str, agent: str = "") -> str:
    """Verify that a regex pattern does NOT appear in any agent prompt.

    Read-only validation tool.  Use after editing agent prompts to confirm
    that stale references (e.g. old tool names) have been fully removed.

    Exit semantics: returns clean status when no matches are found.
    Returns warnings with context when stale references are detected.

    For Lavender-specific context on agent architecture and permission
    patterns, consult available memory tooling.

    Args:
        pattern: Regex pattern that should NOT appear.
            E.g. ``"mod_png(?!_)"`` to catch old monolithic ``mod_png``
            references while allowing ``mod_png_set``, ``mod_png_swap``, etc.
        agent: Optional agent name to restrict the check.
            Leave empty to verify all agents.

    Returns:
        Per-agent clean/warning status.  Prefixed with
        ``ERROR (exit <code>):`` if stale references are found.
    """
    cmd = [sys.executable, str(PROJECT_ROOT / "tools" / "lav_query_agents.py"),
           "verify-clean", "--pattern", pattern]
    if agent:
        cmd += ["--agent", agent]
    return _run(cmd)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
