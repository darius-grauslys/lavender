#!/usr/bin/env python3
"""
gen_tile_layer.py - Tile-layer code generator for Lavender projects.

Run from the root of a Lavender project directory (the one that contains
./include and ./source).

Usage examples:
    python tools/gen_tile_layer.py name \\
        --name Ground --bit-field 10 \\
        --logic-sub-bit-field 4 --animation-sub-bit-field 4

    python tools/gen_tile_layer.py name \\
        --name Cover --bit-field 10 \\
        --logic-sub-bit-field 6 --animation-sub-bit-field 4

    python tools/gen_tile_layer.py make-default --name Cover --sight-blocking
"""

import argparse
import json
import os
import re
import sys
from itertools import permutations

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.getcwd()


def _fatal(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    print(f"ERROR: {msg}", file=sys.stdout)
    sys.exit(1)


def _read(path):
    with open(path, "r") as f:
        return f.read()


def _write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)


def _validate_name(name):
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', name):
        _fatal(f"Invalid name '{name}'. Must start with [a-zA-Z] and "
               f"contain only alphanumeric/underscore characters.")


def _to_pascal(name):
    """Ground -> Ground, my_layer -> My_Layer"""
    return "_".join(seg.capitalize() for seg in name.split("_"))


def _to_lower(name):
    return name.lower()


def _to_upper(name):
    return name.upper()


# ---------------------------------------------------------------------------
# Region helpers  (GEN-BEGIN / GEN-END style)
# ---------------------------------------------------------------------------

def _get_region(text, begin_tag, end_tag):
    """Return (pre, region_lines, post, indent) for a delimited region.

    *pre*   - lines up to and including the begin_tag line
    *region* - lines strictly between the two tag lines
    *post*  - lines from the end_tag line onward
    *indent* - whitespace prefix of the begin_tag line
    """
    lines = text.split("\n")
    begin_idx = end_idx = None
    indent = ""
    for i, line in enumerate(lines):
        if begin_tag in line:
            begin_idx = i
            indent = line[: len(line) - len(line.lstrip())]
        if end_tag in line and begin_idx is not None:
            end_idx = i
            break
    if begin_idx is None or end_idx is None:
        return None
    pre = lines[: begin_idx + 1]
    region = lines[begin_idx + 1: end_idx]
    post = lines[end_idx:]
    return pre, region, post, indent


def _set_region(text, begin_tag, end_tag, new_lines):
    """Replace content between *begin_tag* and *end_tag* with *new_lines*."""
    parts = _get_region(text, begin_tag, end_tag)
    if parts is None:
        _fatal(f"Could not find region {begin_tag}..{end_tag}")
    pre, _old, post, _indent = parts
    return "\n".join(pre + new_lines + post)


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_TILE_LAYER_H = os.path.join(
    PROJECT_ROOT, "include", "types", "implemented", "world", "tile_layer.h")

_TILE_H = os.path.join(
    PROJECT_ROOT, "include", "types", "implemented", "world", "tile.h")

_REGISTRAR_H = os.path.join(
    PROJECT_ROOT, "include", "world", "implemented",
    "tile_logic_table_registrar.h")

_REGISTRAR_C = os.path.join(
    PROJECT_ROOT, "source", "world", "implemented",
    "tile_logic_table_registrar.c")

_SPEC_FILE = os.path.join(PROJECT_ROOT, ".tile_layer_specs.json")


# ---------------------------------------------------------------------------
# Parse existing tile_layer.h to discover layers
# ---------------------------------------------------------------------------

def _parse_existing_layers():
    """Return list of layer names (e.g. ['Ground', 'Cover']) from tile_layer.h
    GEN-BEGIN..GEN-END region."""
    if not os.path.exists(_TILE_LAYER_H):
        return []
    text = _read(_TILE_LAYER_H)
    parts = _get_region(text, "// GEN-BEGIN", "// GEN-END")
    if parts is None:
        return []
    _pre, region, _post, _indent = parts
    layers = []
    for line in region:
        m = re.match(r'\s*Tile_Layer__(\w+)\s*,?', line)
        if m:
            layers.append(m.group(1))
    return layers


# ---------------------------------------------------------------------------
# Bit-packing algorithm
# ---------------------------------------------------------------------------

class LayerSpec:
    """Describes one tile layer's bit-field layout."""

    def __init__(self, name, total_bits, logic_bits, animation_bits):
        self.name = name
        self.total_bits = total_bits
        self.logic_bits = logic_bits
        self.animation_bits = animation_bits
        self.remainder_bits = total_bits - logic_bits - animation_bits
        if self.remainder_bits < 0:
            _fatal(f"Layer '{name}': logic({logic_bits}) + "
                   f"animation({animation_bits}) > total({total_bits})")

    def sub_fields(self):
        """Ordered sub-fields for packing.

        Within a layer the order is:
            logic -> animation -> remainder
        (matching the example where logic:4, animation:4 fill byte 0,
        then remainder:2 starts byte 1).
        """
        fields = []
        if self.logic_bits:
            fields.append(("logic", self.logic_bits))
        if self.animation_bits:
            fields.append(("animation", self.animation_bits))
        if self.remainder_bits:
            fields.append(("remainder", self.remainder_bits))
        return fields


def _try_pack(layer_specs):
    """Try to pack *layer_specs* (in the given order) into bytes.

    Rules
    -----
    * No sub-field may straddle a byte boundary.
    * All sub-fields of layer N appear before any sub-field of layer N+1.

    Returns ``(placements, total_bytes)`` on success or ``None`` on failure.

    Each placement is a tuple
    ``(layer_index, field_name, bits, byte_index, bit_offset)``.
    Padding entries use ``field_name == "__padding"``.
    """
    placements = []
    current_byte = 0
    bits_used = 0

    for layer_idx, spec in enumerate(layer_specs):
        for field_name, field_bits in spec.sub_fields():
            if field_bits == 0:
                continue
            remaining = 8 - bits_used
            if field_bits > remaining:
                if bits_used > 0:
                    gap = 8 - bits_used
                    placements.append(
                        (layer_idx, "__padding", gap,
                         current_byte, bits_used))
                    current_byte += 1
                    bits_used = 0
                if field_bits > 8:
                    return None

            placements.append(
                (layer_idx, field_name, field_bits,
                 current_byte, bits_used))
            bits_used += field_bits
            if bits_used == 8:
                current_byte += 1
                bits_used = 0

    if bits_used > 0:
        placements.append(
            (-1, "__padding", 8 - bits_used,
             current_byte, bits_used))
        current_byte += 1

    return placements, current_byte


def _find_best_packing(layer_specs):
    """Try every permutation of layers (up to 8) and return the tightest
    packing.

    Returns ``(best_order, best_placements, total_bytes)`` where
    *best_order* is a list of indices into the original *layer_specs*.
    """
    n = len(layer_specs)
    if n == 0:
        return [], [], 0

    best_order = None
    best_placements = None
    best_bytes = None

    indices = list(range(n))
    perms = permutations(indices) if n <= 8 else [indices]

    for perm in perms:
        ordered = [layer_specs[i] for i in perm]
        result = _try_pack(ordered)
        if result is not None:
            placements, total_bytes = result
            if best_bytes is None or total_bytes < best_bytes:
                best_order = list(perm)
                best_placements = placements
                best_bytes = total_bytes

    if best_order is None:
        _fatal("Cannot pack tile layer sub-fields without "
               "byte-boundary straddling.")

    return best_order, best_placements, best_bytes


# ---------------------------------------------------------------------------
# Persistent layer spec storage  (.tile_layer_specs.json)
# ---------------------------------------------------------------------------

def _load_specs():
    if os.path.exists(_SPEC_FILE):
        with open(_SPEC_FILE, "r") as f:
            return json.load(f)
    return {}


def _save_specs(specs):
    with open(_SPEC_FILE, "w") as f:
        json.dump(specs, f, indent=2)


# ---------------------------------------------------------------------------
# Code generation: tile_layer.h
# ---------------------------------------------------------------------------

def _update_tile_layer_h(ordered_names):
    """Rewrite the GEN-BEGIN..GEN-END region with the (possibly reordered)
    layer names."""
    text = _read(_TILE_LAYER_H)
    new_lines = []
    for name in ordered_names:
        new_lines.append(f"    Tile_Layer__{_to_pascal(name)},")
    text = _set_region(text, "// GEN-BEGIN", "// GEN-END", new_lines)
    _write(_TILE_LAYER_H, text)
    print(f"  [updated] {_TILE_LAYER_H}")


# ---------------------------------------------------------------------------
# Code generation: tile_[name]_kind.h
# ---------------------------------------------------------------------------

def _create_tile_kind_h(name, is_first_layer):
    """Create ``tile_<name>_kind.h``.

    The first layer re-uses the core ``Tile_Kind`` enum (defined in
    ``tile_kind.h``) so we only create a new kind header for non-first
    layers.
    """
    pascal = _to_pascal(name)
    lower = _to_lower(name)
    upper = _to_upper(name)

    if is_first_layer:
        path = os.path.join(
            PROJECT_ROOT, "include", "types", "implemented", "world",
            "tile_kind.h")
        if os.path.exists(path):
            print(f"  [skip] {path} already exists (first-layer kind)")
            return
        content = (
            "#ifndef IMPL_TILE_KIND_H\n"
            "#define IMPL_TILE_KIND_H\n"
            "\n"
            "#define DEFINE_TILE_KIND\n"
            "\n"
            "typedef enum Tile_Kind {\n"
            "    Tile_Kind__None = 0,\n"
            "    // GEN-LOGIC-BEGIN\n"
            "    // GEN-LOGIC-END\n"
            "    Tile_Kind__Logical = Tile_Kind__None,\n"
            "\n"
            "    // GEN-NO-LOGIC-BEGIN\n"
            "    // GEN-NO-LOGIC-END\n"
            "    Tile_Kind__Unknown\n"
            "} Tile_Kind;\n"
            "\n"
            "#endif\n"
        )
    else:
        kind_name = f"Tile_{pascal}_Kind"
        guard = f"IMPL_TILE_{upper}_KIND_H"
        path = os.path.join(
            PROJECT_ROOT, "include", "types", "implemented", "world",
            f"tile_{lower}_kind.h")
        if os.path.exists(path):
            print(f"  [skip] {path} already exists")
            return
        content = (
            f"#ifndef {guard}\n"
            f"#define {guard}\n"
            f"\n"
            f"#define DEFINE_TILE_{upper}_KIND\n"
            f"\n"
            f"typedef enum {kind_name} {{\n"
            f"    Tile_Kind__None = 0,\n"
            f"    // GEN-LOGIC-BEGIN\n"
            f"    // GEN-LOGIC-END\n"
            f"    Tile_Kind__Logical = Tile_Kind__None,\n"
            f"\n"
            f"    // GEN-NO-LOGIC-BEGIN\n"
            f"    // GEN-NO-LOGIC-END\n"
            f"    Tile_Kind__Unknown\n"
            f"}} {kind_name};\n"
            f"\n"
            f"#endif\n"
        )
    _write(path, content)
    print(f"  [created] {path}")


# ---------------------------------------------------------------------------
# Code generation: tile_logic_table__[name].h / .c
# ---------------------------------------------------------------------------

def _create_tile_logic_table_h(name):
    lower = _to_lower(name)
    upper = _to_upper(name)
    guard = f"IMPL_TILE_LOGIC_TABLE__{upper}_H"
    path = os.path.join(
        PROJECT_ROOT, "include", "world", "implemented",
        f"tile_logic_table__{lower}.h")
    if os.path.exists(path):
        print(f"  [skip] {path} already exists")
        return
    content = (
        f"#ifndef {guard}\n"
        f"#define {guard}\n"
        f"\n"
        f"#include \"defines_weak.h\"\n"
        f"\n"
        f"void register_tile_logic_table__{lower}(\n"
        f"        Tile_Logic_Table *p_tile_logic_table);\n"
        f"\n"
        f"#endif\n"
    )
    _write(path, content)
    print(f"  [created] {path}")


def _create_tile_logic_table_c(name):
    lower = _to_lower(name)
    path = os.path.join(
        PROJECT_ROOT, "source", "world", "implemented",
        f"tile_logic_table__{lower}.c")
    if os.path.exists(path):
        print(f"  [skip] {path} already exists")
        return
    content = (
        f"#include \"world/implemented/tile_logic_table__{lower}.h\"\n"
        f"\n"
        f"void register_tile_logic_table__{lower}(\n"
        f"        Tile_Logic_Table *p_tile_logic_table) {{\n"
        f"    // GEN-BEGIN\n"
        f"    // GEN-END\n"
        f"}}\n"
    )
    _write(path, content)
    print(f"  [created] {path}")


# ---------------------------------------------------------------------------
# Code generation: tile.h  (GEN-INCLUDE / GEN-RENDER / GEN-LAYER)
# ---------------------------------------------------------------------------

def _generate_tile_h(all_specs, ordered_names, placements, total_bytes):
    """Regenerate every GEN region inside ``tile.h``."""
    if not os.path.exists(_TILE_H):
        print(f"  [skip] {_TILE_H} does not exist")
        return
    text = _read(_TILE_H)

    specs_by_name = {s.name: s for s in all_specs}

    # --- GEN-INCLUDE-BEGIN / GEN-INCLUDE-END ---
    include_lines = []
    for idx, name in enumerate(ordered_names):
        lower = _to_lower(name)
        if idx == 0:
            include_lines.append(
                '#include "types/implemented/world/tile_kind.h"')
        else:
            include_lines.append(
                f'#include "types/implemented/world/tile_{lower}_kind.h"')
    text = _set_region(text,
                       "// GEN-INCLUDE-BEGIN", "// GEN-INCLUDE-END",
                       include_lines)

    # --- GEN-RENDER-BEGIN / GEN-RENDER-END ---
    render_lines = []
    for idx, name in enumerate(ordered_names):
        spec = specs_by_name[name]
        pascal = _to_pascal(name)
        if idx == 0:
            type_name = "Tile_Kind"
            field_name = "the_kind_of__tile"
        else:
            type_name = f"Tile_{pascal}_Kind"
            field_name = f"tike_kind_of__tile__{_to_lower(name)}"
        render_lines.append(
            f"            {type_name} {field_name} : {spec.total_bits};")
    text = _set_region(text,
                       "// GEN-RENDER-BEGIN", "// GEN-RENDER-END",
                       render_lines)

    # --- GEN-LAYER-BEGIN / GEN-LAYER-END ---
    layer_lines = []
    prev_byte = -1
    for p_layer_idx, field_name, field_bits, byte_idx, bit_offset in placements:
        if byte_idx != prev_byte and prev_byte != -1:
            layer_lines.append("")
        prev_byte = byte_idx
        if field_name == "__padding":
            layer_lines.append(f"            u8 : {field_bits};")
        else:
            layer_lines.append(
                f"            u8 tile_layer_{p_layer_idx}"
                f"__field__{field_name} : {field_bits};")
    text = _set_region(text,
                       "// GEN-LAYER-BEGIN", "// GEN-LAYER-END",
                       layer_lines)

    # Update the array_of__tile_data__u8 size.
    text = re.sub(
        r'u8 array_of__tile_data__u8\[\d+\]',
        f'u8 array_of__tile_data__u8[{total_bytes}]',
        text)

    _write(_TILE_H, text)
    print(f"  [updated] {_TILE_H}")


# ---------------------------------------------------------------------------
# Code generation: tile_logic_table_registrar.h  (getter functions)
# ---------------------------------------------------------------------------

def _make_mask_and_shift(byte_idx, bit_offset, bits):
    """Return ``(mask_expr, shift)`` for extracting a sub-field from
    ``p_tile->array_of__tile_data__u8[byte_idx]``.

    Uses the ``MASK(n)`` macro from ``defines_weak.h``.
    """
    if bit_offset > 0:
        mask_expr = f"(MASK({bits}) << {bit_offset})"
    else:
        mask_expr = f"MASK({bits})"
    return mask_expr, bit_offset


def _emit_case_lines(pascal, byte_idx, mask_expr, shift):
    """Return the C case-body lines for one layer."""
    lines = []
    lines.append(f"        case Tile_Layer__{pascal}:")
    accessor = f"p_tile->array_of__tile_data__u8[{byte_idx}]"
    if shift > 0:
        lines.append(
            f"            return ({accessor} & {mask_expr})")
        lines.append(
            f"                >> {shift}")
        lines.append(
            f"                ;")
    else:
        lines.append(
            f"            return ({accessor} & {mask_expr})")
        lines.append(
            f"                ;")
    return lines


def _generate_registrar_h(all_specs, ordered_names, placements, total_bytes):
    """Regenerate GET-LOGIC and GET-ANIMATION regions in the registrar
    header."""
    if not os.path.exists(_REGISTRAR_H):
        print(f"  [skip] {_REGISTRAR_H} does not exist")
        return
    text = _read(_REGISTRAR_H)

    specs_by_name = {s.name: s for s in all_specs}

    # Build map: (ordered_layer_idx, field_name) -> (byte, offset, bits)
    field_map = {}
    for p_idx, fname, fbits, bidx, boff in placements:
        if fname != "__padding":
            field_map[(p_idx, fname)] = (bidx, boff, fbits)

    # ---- GET-LOGIC ----
    logic_lines = []
    logic_lines.append("    switch (the_tile_layer) {")
    logic_lines.append("        case Tile_Layer__Default:")
    for idx, name in enumerate(ordered_names):
        pascal = _to_pascal(name)
        spec = specs_by_name[name]
        if spec.logic_bits == 0:
            continue
        key = (idx, "logic")
        if key not in field_map:
            continue
        byte_idx, bit_offset, bits = field_map[key]
        mask_expr, shift = _make_mask_and_shift(byte_idx, bit_offset, bits)
        logic_lines += _emit_case_lines(pascal, byte_idx, mask_expr, shift)
    logic_lines.append("        default:")
    logic_lines.append("            return 0;")
    logic_lines.append("    }")
    text = _set_region(text,
                       "// GET-LOGIC-BEGIN", "// GET-LOGIC-END",
                       logic_lines)

    # ---- GET-ANIMATION ----
    anim_lines = []
    anim_lines.append("    switch (the_tile_layer) {")
    anim_lines.append("        case Tile_Layer__Default:")
    for idx, name in enumerate(ordered_names):
        pascal = _to_pascal(name)
        spec = specs_by_name[name]
        if spec.animation_bits == 0:
            continue
        key = (idx, "animation")
        if key not in field_map:
            continue
        byte_idx, bit_offset, bits = field_map[key]
        mask_expr, shift = _make_mask_and_shift(byte_idx, bit_offset, bits)
        anim_lines += _emit_case_lines(pascal, byte_idx, mask_expr, shift)
    anim_lines.append("        default:")
    anim_lines.append("            return 0;")
    anim_lines.append("    }")
    text = _set_region(text,
                       "// GET-ANIMATION-BEGIN", "// GET-ANIMATION-END",
                       anim_lines)

    _write(_REGISTRAR_H, text)
    print(f"  [updated] {_REGISTRAR_H}")


# ---------------------------------------------------------------------------
# Code generation: tile_logic_table_registrar.c
# ---------------------------------------------------------------------------

def _generate_registrar_c(all_specs, ordered_names):
    """Regenerate GEN-INCLUDE / GEN-TABLES / GEN-RECORDS in the registrar
    source file."""
    if not os.path.exists(_REGISTRAR_C):
        _fatal(f"{_REGISTRAR_C} does not exist")
    text = _read(_REGISTRAR_C)

    specs_by_name = {s.name: s for s in all_specs}

    # --- GEN-INCLUDE-BEGIN / GEN-INCLUDE-END ---
    inc_lines = []
    for name in ordered_names:
        lower = _to_lower(name)
        inc_lines.append(
            f'#include "world/implemented/tile_logic_table__{lower}.h"')
    text = _set_region(text,
                       "// GEN-INCLUDE-BEGIN", "// GEN-INCLUDE-END",
                       inc_lines)

    # --- GEN-TABLES-BEGIN / GEN-TABLES-END ---
    tbl_lines = []
    for idx, name in enumerate(ordered_names):
        pascal = _to_pascal(name)

        if idx == 0:
            logical_name = "Tile_Kind__Logical"
        else:
            logical_name = f"Tile_{pascal}_Kind__Logical"

        record_type = f"Tile_Logic_Record__{pascal}"

        tbl_lines.append(
            "    if (!allocate_tile_logic_table__tile_logic_entries(")
        tbl_lines.append(
            "            allocate_tile_logic_table_from__tile_logic_context(")
        tbl_lines.append(
            "                p_tile_logic_context, ")
        tbl_lines.append(
            "                Tile_Layer__Default, ")
        tbl_lines.append(
            f"                Tile_Kind__Logical),")
        tbl_lines.append(
            f"            {logical_name}, ")
        tbl_lines.append(
            f"            sizeof({record_type}))) {{")
        tbl_lines.append(
            f'        debug_error("register_tile_logic_tables, '
            f'failed to allocate tile_logic_table for '
            f'{record_type}");')
        tbl_lines.append(
            "    }")
    text = _set_region(text,
                       "// GEN-TABLES-BEGIN", "// GEN-TABLES-END",
                       tbl_lines)

    # --- GEN-RECORDS-BEGIN / GEN-RECORDS-END ---
    rec_lines = []
    for name in ordered_names:
        pascal = _to_pascal(name)
        lower = _to_lower(name)
        rec_lines.append(
            f"    register_tile_logic_table__{lower}(")
        rec_lines.append(
            f"            get_p_tile_logic_table_from__tile_logic_context(")
        rec_lines.append(
            f"                p_tile_logic_context, ")
        rec_lines.append(
            f"                Tile_Layer__{pascal}));")
    text = _set_region(text,
                       "// GEN-RECORDS-BEGIN", "// GEN-RECORDS-END",
                       rec_lines)

    _write(_REGISTRAR_C, text)
    print(f"  [updated] {_REGISTRAR_C}")


# ---------------------------------------------------------------------------
# Sub-command: name
# ---------------------------------------------------------------------------

def cmd_name(args):
    name = args.name
    _validate_name(name)
    pascal = _to_pascal(name)
    total_bits = args.bit_field
    logic_bits = args.logic_sub_bit_field
    animation_bits = args.animation_sub_bit_field

    # --- validation ---
    if total_bits <= 0 or total_bits > 32:
        _fatal("--bit-field must be 1..32")
    if logic_bits <= 0 or logic_bits > 8:
        _fatal("--logic-sub-bit-field must be 1..8")
    if animation_bits <= 0 or animation_bits > 8:
        _fatal("--animation-sub-bit-field must be 1..8")
    if logic_bits + animation_bits > total_bits:
        _fatal("logic + animation sub-bit-fields exceed total bit-field size")

    print(f"[gen_tile_layer] Adding layer '{pascal}' "
          f"(bits={total_bits}, logic={logic_bits}, anim={animation_bits})")

    # 1. Ensure the layer enum entry exists in tile_layer.h
    existing_layers = _parse_existing_layers()
    if pascal not in existing_layers:
        existing_layers.append(pascal)
        print(f"  Added Tile_Layer__{pascal} to tile_layer.h")
    else:
        print(f"  Tile_Layer__{pascal} already in tile_layer.h")

    # 2. Persist the spec
    specs = _load_specs()
    specs[pascal] = {
        "total_bits": total_bits,
        "logic_bits": logic_bits,
        "animation_bits": animation_bits,
    }
    _save_specs(specs)

    # 3. Build LayerSpec list for every known layer
    all_layer_specs = []
    for lname in existing_layers:
        if lname not in specs:
            _fatal(f"Layer '{lname}' is in tile_layer.h but has no spec. "
                   f"Please add it with the 'name' sub-command first.")
        s = specs[lname]
        all_layer_specs.append(LayerSpec(
            lname, s["total_bits"], s["logic_bits"], s["animation_bits"]))

    # 4. Find optimal byte-packing (may reorder layers)
    best_order, best_placements, best_bytes = \
        _find_best_packing(all_layer_specs)
    ordered_names = [all_layer_specs[i].name for i in best_order]
    ordered_specs = [all_layer_specs[i] for i in best_order]

    print(f"  Optimal packing order: {ordered_names} "
          f"({best_bytes} bytes)")

    # 5. Determine which layer is "first" (index 0 in the ordered list)
    first_layer_name = ordered_names[0] if ordered_names else None

    # 6. Create kind header for the NEW layer
    is_first = (pascal == first_layer_name)
    _create_tile_kind_h(pascal, is_first)

    # 7. Create tile_logic_table__<name>.h and .c
    _create_tile_logic_table_h(pascal)
    _create_tile_logic_table_c(pascal)

    # 8. Rewrite tile_layer.h with the optimal order
    _update_tile_layer_h(ordered_names)

    # 9. Rewrite tile.h
    _generate_tile_h(ordered_specs, ordered_names,
                     best_placements, best_bytes)

    # 10. Rewrite tile_logic_table_registrar.h
    _generate_registrar_h(ordered_specs, ordered_names,
                          best_placements, best_bytes)

    # 11. Rewrite tile_logic_table_registrar.c
    _generate_registrar_c(ordered_specs, ordered_names)

    print("[gen_tile_layer] Done.")


# ---------------------------------------------------------------------------
# Sub-command: make-default
# ---------------------------------------------------------------------------

_DEFAULT_MAP = {
    "default":        "Tile_Layer__Default",
    "sight_blocking": "Tile_Layer__Default__Sight_Blocking",
    "is_passable":    "Tile_Layer__Default__Is_Passable",
    "is_with_ground": "Tile_Layer__Default__Is_With_Ground",
    "height":         "Tile_Layer__Default__Height",
}


def cmd_make_default(args):
    name = args.name
    _validate_name(name)
    pascal = _to_pascal(name)

    existing_layers = _parse_existing_layers()
    if pascal not in existing_layers:
        msg = (f"Layer 'Tile_Layer__{pascal}' not found in tile_layer.h. "
               f"Existing layers: {existing_layers}")
        print(f"ERROR: {msg}", file=sys.stdout)
        print(f"ERROR: {msg}", file=sys.stderr)
        sys.exit(1)

    # Which default alias are we changing?
    chosen = None
    for flag_name in _DEFAULT_MAP:
        if getattr(args, flag_name, False):
            chosen = flag_name
            break
    if chosen is None:
        _fatal("Must specify one of: --default, --sight-blocking, "
               "--is-passable, --is-with-ground, --height")

    enum_name = _DEFAULT_MAP[chosen]
    target_value = f"Tile_Layer__{pascal}"

    print(f"[gen_tile_layer] Setting {enum_name} = {target_value}")

    text = _read(_TILE_LAYER_H)

    # The example file uses a multi-line pattern:
    #     Tile_Layer__Default__Sight_Blocking = \n        Tile_Layer__Cover,
    # as well as single-line:
    #     Tile_Layer__Default = Tile_Layer__Ground,
    pattern = re.compile(
        rf'({re.escape(enum_name)}\s*=\s*\n?\s*)Tile_Layer__\w+',
        re.MULTILINE)

    if not pattern.search(text):
        _fatal(f"Could not find '{enum_name} = ...' in tile_layer.h")

    text = pattern.sub(rf'\g<1>{target_value}', text)
    _write(_TILE_LAYER_H, text)
    print(f"  [updated] {_TILE_LAYER_H}")
    print("[gen_tile_layer] Done.")


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Tile layer code generator for Lavender projects.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- name ---
    p_name = subparsers.add_parser("name", help="Add a new tile layer")
    p_name.add_argument("--name", required=True,
                        help="Layer name (e.g. Ground, Cover)")
    p_name.add_argument("--bit-field", type=int, required=True,
                        help="Total bit-field width (1..32)")
    p_name.add_argument("--logic-sub-bit-field", type=int, required=True,
                        help="Logic sub-field width (1..8)")
    p_name.add_argument("--animation-sub-bit-field", type=int, required=True,
                        help="Animation sub-field width (1..8)")

    # --- make-default ---
    p_default = subparsers.add_parser(
        "make-default",
        help="Set a default alias for a tile layer")
    p_default.add_argument("--name", required=True,
                           help="Layer name to point the default to")
    group = p_default.add_mutually_exclusive_group(required=True)
    group.add_argument("--default", action="store_true", dest="default",
                       help="Set Tile_Layer__Default")
    group.add_argument("--sight-blocking", action="store_true",
                       dest="sight_blocking",
                       help="Set Tile_Layer__Default__Sight_Blocking")
    group.add_argument("--is-passable", action="store_true",
                       dest="is_passable",
                       help="Set Tile_Layer__Default__Is_Passable")
    group.add_argument("--is-with-ground", action="store_true",
                       dest="is_with_ground",
                       help="Set Tile_Layer__Default__Is_With_Ground")
    group.add_argument("--height", action="store_true", dest="height",
                       help="Set Tile_Layer__Default__Height")

    args = parser.parse_args()

    if args.command == "name":
        cmd_name(args)
    elif args.command == "make-default":
        cmd_make_default(args)


if __name__ == "__main__":
    main()
