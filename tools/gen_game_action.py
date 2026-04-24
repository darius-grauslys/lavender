#!/usr/bin/env python3
"""
gen_game_action.py – code-generator for Lavender game action type headers,
game action boilerplate (.h/.c), and registrar wiring.

Run from the root of a Lavender *project* directory (the one that contains
./include and ./source).

Usage:
    python tools/gen_game_action.py <relative/path/to/leaf.h>

Example:
    python tools/gen_game_action.py collisions/aabb/update__pos_vec_i32.h

Creates:
    include/game_action/types/implemented/collisions/ga_types__collisions.h
    include/game_action/types/implemented/collisions/aabb/ga_types__collisions__aabb.h
    include/game_action/types/implemented/collisions/aabb/ga_type__collisions__aabb__update__pos_vec_i32.h
    include/game_action/implemented/collisions/aabb/game_action__collisions__aabb__update__pos_vec_i32.h
    source/game_action/implemented/collisions/aabb/game_action__collisions__aabb__update__pos_vec_i32.c
    (and wires everything into the registrar)
"""

import argparse
import os
import re
import sys

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PROJECT_ROOT = os.getcwd()

BASE_DIR = os.path.join(".", "include", "game_action", "types", "implemented")


def _fatal(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def validate_path(rel_path):
    """Ensure the path ends with .h and has at least one component."""
    if not rel_path.endswith(".h"):
        _fatal("path must end with .h")
    no_ext = rel_path[:-2]
    parts = no_ext.split("/")
    if len(parts) < 1 or not parts[-1]:
        _fatal("path must have at least one component.")
    return parts


def read_file(path):
    if not os.path.isfile(path):
        _fatal(f"file not found: {path}")
    with open(path, "r") as f:
        return f.read()


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)


# ---------------------------------------------------------------------------
# Name-building helpers
# ---------------------------------------------------------------------------

def build_prefix(components, count):
    """Build accumulated prefix from first *count* components.

    e.g. components=(collisions, aabb), count=2 => "collisions__aabb"
    """
    return "__".join(components[:count])


def to_upper(name):
    return name.upper()


def to_struct_name(prefix):
    """Convert a prefix like "collisions__aabb" to a struct-style name
    like "GA_Collisions__AABB".

    Convention: split on __ to get path-level segments, then within each
    segment split on _ and capitalize each word.  Words of 4 chars or fewer
    are fully uppercased (acronym heuristic).
    """
    segments = prefix.split("__")
    result = "GA"
    for seg in segments:
        words = seg.split("_")
        capitalized_parts = []
        for word in words:
            if not word:
                continue
            if len(word) <= 4:
                capitalized_parts.append(word.upper())
            else:
                capitalized_parts.append(word[0].upper() + word[1:])
        result += "_" + "_".join(capitalized_parts)
    return result


# ---------------------------------------------------------------------------
# Region helpers (GEN-BEGIN / GEN-END style)
# ---------------------------------------------------------------------------

def insert_between_markers(text, begin_marker, end_marker, new_line,
                           *, duplicate_check=None):
    """Insert *new_line* just before *end_marker* inside *text*.

    If *duplicate_check* is given and already appears between the markers
    the text is returned unchanged.
    """
    begin_idx = text.find(begin_marker)
    end_idx = text.find(end_marker)
    if begin_idx == -1 or end_idx == -1:
        _fatal(f"could not find markers '{begin_marker}' / '{end_marker}'")

    region = text[begin_idx:end_idx]
    if duplicate_check and duplicate_check in region:
        return text  # already present

    return text[:end_idx] + new_line + "\n" + text[end_idx:]


def ensure_include_in_gen_region(filepath, include_line):
    """Ensure an #include line exists between GEN-BEGIN and GEN-END.

    Returns True if added, False if already present.
    """
    text = read_file(filepath)
    new_text = insert_between_markers(
        text, "// GEN-BEGIN", "// GEN-END",
        include_line,
        duplicate_check=include_line.strip())
    if new_text == text:
        return False
    write_file(filepath, new_text)
    return True


# ---------------------------------------------------------------------------
# Field parsing
# ---------------------------------------------------------------------------

def parse_fields(filepath):
    """Parse fields between FIELDS-BEGIN and FIELDS-END.

    Returns list of (field_type, field_name) tuples.
    """
    if not os.path.isfile(filepath):
        return []
    text = read_file(filepath)
    lines = text.split("\n")
    in_region = False
    fields = []
    for line in lines:
        if "// FIELDS-BEGIN" in line:
            in_region = True
            continue
        if "// FIELDS-END" in line:
            in_region = False
            continue
        if in_region:
            trimmed = line.strip()
            # Skip empty lines and comments
            if (not trimmed or trimmed.startswith("//")
                    or trimmed.startswith("/*")):
                continue
            # Remove trailing semicolon
            trimmed = trimmed.rstrip(";").strip()
            # Split into type and name — last word is the name
            parts = trimmed.split()
            if len(parts) >= 2:
                field_name = parts[-1]
                field_type = " ".join(parts[:-1])
                fields.append((field_type, field_name))
    return fields


# ---------------------------------------------------------------------------
# Accessor helpers
# ---------------------------------------------------------------------------

def accessor_exists_in_impl(text, accessor_marker):
    """Check if an accessor comment marker exists in GEN-IMPL region."""
    lines = text.split("\n")
    in_region = False
    for line in lines:
        if "// GEN-IMPL-BEGIN" in line:
            in_region = True
            continue
        if "// GEN-IMPL-END" in line:
            in_region = False
            continue
        if in_region:
            if line.strip() == accessor_marker:
                return True
    return False


def generate_accessors_for_field(filepath, struct_name, field_type,
                                 field_name, header_kind):
    """Generate accessor functions for a field and insert before
    GEN-IMPL-END."""
    text = read_file(filepath)
    lower_struct = struct_name.lower()
    accessor_block = ""

    # Value accessor
    marker = f"// ACCESSOR: {field_name}"
    if not accessor_exists_in_impl(text, marker):
        if header_kind == "union":
            accessor_block += (
                f"\n{marker}\n"
                f"static inline\n"
                f"{field_type} get_{field_name}_from__{lower_struct}(\n"
                f"        Game_Action *p_game_action) {{\n"
                f"    return p_game_action\n"
                f"        ->{struct_name}\n"
                f"        .{field_name}\n"
                f"        ;\n"
                f"}}"
            )
        else:
            accessor_block += (
                f"\n{marker}\n"
                f"static inline\n"
                f"{field_type} get_{field_name}_from__{lower_struct}(\n"
                f"        Game_Action *p_game_action) {{\n"
                f"    return (GET_P_GAME_ACTION_PAYLOAD_AS_P(p_game_action, {struct_name}))\n"
                f"        .{field_name}\n"
                f"        ;\n"
                f"}}"
            )

    # Pointer accessor
    p_marker = f"// ACCESSOR: p_{field_name}"
    if not accessor_exists_in_impl(text, p_marker):
        if header_kind == "union":
            accessor_block += (
                f"\n\n{p_marker}\n"
                f"static inline\n"
                f"{field_type} *get_p_{field_name}_from__{lower_struct}(\n"
                f"        Game_Action *p_game_action) {{\n"
                f"    return &p_game_action\n"
                f"        ->{struct_name}\n"
                f"        .{field_name}\n"
                f"        ;\n"
                f"}}"
            )
        else:
            accessor_block += (
                f"\n\n{p_marker}\n"
                f"static inline\n"
                f"{field_type} *get_p_{field_name}_from__{lower_struct}(\n"
                f"        Game_Action *p_game_action) {{\n"
                f"    return &(GET_P_GAME_ACTION_PAYLOAD_AS_P(p_game_action, {struct_name}))\n"
                f"        .{field_name}\n"
                f"        ;\n"
                f"}}"
            )

    if accessor_block:
        marker_str = "// GEN-IMPL-END"
        idx = text.find(marker_str)
        if idx != -1:
            text = text[:idx] + accessor_block + "\n" + text[idx:]
        write_file(filepath, text)


# ---------------------------------------------------------------------------
# Header generation: union (intermediate) headers
# ---------------------------------------------------------------------------

def generate_union_header(filepath, prefix, guard_name, struct_name,
                          injection_tag):
    """Generate a union (intermediate) header file like
    ga_types__collisions.h."""
    impl_guard = guard_name[:-2] + "_IMPL_H" if guard_name.endswith("_H") \
        else guard_name + "_IMPL_H"

    content = (
        f"/// This file is deterministically generated. Do not edit manually\n"
        f"/// outside of designated GEN-BEGIN / GEN-END regions.\n"
        f"#ifndef {guard_name}\n"
        f"#define {guard_name}\n"
        f"#define GA_TYPE_CONTEXT\n"
        f"\n"
        f"#ifndef DEFINES_H\n"
        f"#include <defines.h>\n"
        f"#endif\n"
        f"\n"
        f"#include <util/custom_type_macro.h>\n"
        f"\n"
        f"LAV_UNION__BEGIN({struct_name}){{\n"
        f"\n"
        f"#ifndef INJECTION_ACTIVE\n"
        f"#define INJECTION_ACTIVE\n"
        f"#define INJECTION_ACTIVE__{injection_tag}\n"
        f"#endif\n"
        f"    struct {{\n"
        f"// FIELDS-BEGIN\n"
        f"// FIELDS-END\n"
        f"        union {{\n"
        f"// GEN-BEGIN\n"
        f"// GEN-END\n"
        f"        }};\n"
        f"    }};\n"
        f"\n"
        f"#ifdef INJECTION_ACTIVE__{injection_tag}\n"
        f"#undef INJECTION_ACTIVE__{injection_tag}\n"
        f"#undef INJECTION_ACTIVE\n"
        f"#endif\n"
        f"\n"
        f"}} {struct_name};\n"
        f"\n"
        f"#undef GA_TYPE_CONTEXT\n"
        f"#endif // Header guard\n"
        f"\n"
        f"#ifndef INJECTION_ACTIVE\n"
        f"#ifndef {impl_guard}\n"
        f"#define {impl_guard}\n"
        f"\n"
        f"// GEN-IMPL-BEGIN\n"
        f"// GEN-IMPL-END\n"
        f"\n"
        f"#endif // Impl Header guard\n"
        f"#endif // INJECTION_ACTIVE\n"
    )
    write_file(filepath, content)


# ---------------------------------------------------------------------------
# Header generation: leaf (type) headers
# ---------------------------------------------------------------------------

def generate_leaf_header(filepath, prefix, guard_name, struct_name,
                         impl_guard):
    """Generate a leaf (type) header file like
    ga_type__collisions__aabb__update__pos_vec_i32.h."""
    content = (
        f"/// This file is deterministically generated. Do not edit manually\n"
        f"/// outside of designated GEN / FIELDS regions.\n"
        f"#if !defined({guard_name}) \\\n"
        f"    || defined(INJECTION_ACTIVE)\n"
        f"\n"
        f"#ifndef INJECTION_ACTIVE\n"
        f"#define {guard_name}\n"
        f"#endif\n"
        f"#define GA_TYPE_CONTEXT\n"
        f"\n"
        f"#ifndef DEFINES_H\n"
        f"#include <defines.h>\n"
        f"#endif\n"
        f"\n"
        f"#include <util/custom_type_macro.h>\n"
        f"\n"
        f"LAV_TYPE__BEGIN({struct_name}){{\n"
        f"// FIELDS-BEGIN\n"
        f"// FIELDS-END\n"
        f"}} {struct_name};\n"
        f"\n"
        f"#undef GA_TYPE_CONTEXT\n"
        f"#endif // Header guard\n"
        f"\n"
        f"#ifndef INJECTION_ACTIVE\n"
        f"#ifndef {impl_guard}\n"
        f"#define {impl_guard}\n"
        f"\n"
        f"// GEN-IMPL-BEGIN\n"
        f"// GEN-IMPL-END\n"
        f"\n"
        f"#endif // Impl Header guard\n"
        f"#endif // INJECTION_ACTIVE\n"
    )
    write_file(filepath, content)


# ---------------------------------------------------------------------------
# Game action .h generation
# ---------------------------------------------------------------------------

def generate_game_action_header(filepath, leaf_prefix, leaf_struct_name,
                                guard_name, func_suffix,
                                type_include_path, union_include_paths,
                                leaf_type_file):
    """Generate the game_action .h file under
    ./include/game_action/implemented/."""
    fields = parse_fields(leaf_type_file)

    fields_params = ""
    dispatch_params = ""
    dispatch_args = ""
    for ftype, fname in fields:
        fields_params += f",\n        {ftype} {fname}"
        dispatch_params += f",\n        {ftype} {fname}"
        dispatch_args += f",\n            {fname}"

    union_includes = ""
    for upath in union_include_paths:
        if upath:
            union_includes += f'\n#include "{upath}"'

    content = (
        f"/// This file is deterministically generated.\n"
        f"/// Implement the #error stubs in the corresponding .c file.\n"
        f"#ifndef {guard_name}\n"
        f"#define {guard_name}\n"
        f"\n"
        f'#include "defines.h"\n'
        f'#include "defines_weak.h"\n'
        f'#include "game.h"\n'
        f"{union_includes}\n"
        f'#include "{type_include_path}"\n'
        f"\n"
        f"void register_game_action__{func_suffix}_for__server(\n"
        f"        Game_Action_Logic_Table *p_game_action_logic_table);\n"
        f"\n"
        f"static inline\n"
        f"void register_game_action__{func_suffix}_for__offline(\n"
        f"        Game_Action_Logic_Table *p_game_action_logic_table) {{\n"
        f"    register_game_action__{func_suffix}_for__server(\n"
        f"            p_game_action_logic_table);\n"
        f"}}\n"
        f"\n"
        f"void register_game_action__{func_suffix}_for__client(\n"
        f"        Game_Action_Logic_Table *p_game_action_logic_table);\n"
        f"\n"
        f"void initialize_game_action_for__{func_suffix}(\n"
        f"        Game_Action *p_game_action{fields_params});\n"
        f"\n"
        f"static inline\n"
        f"bool dispatch_game_action__{func_suffix}(\n"
        f"        Game *p_game{dispatch_params}) {{\n"
        f"    Game_Action ga;\n"
        f"    initialize_game_action_for__{func_suffix}(\n"
        f"            &ga{dispatch_args});\n"
        f"    return dispatch_game_action_to__server(\n"
        f"            p_game,\n"
        f"            &ga);\n"
        f"}}\n"
        f"\n"
        f"#endif\n"
    )
    write_file(filepath, content)


# ---------------------------------------------------------------------------
# Game action .c generation
# ---------------------------------------------------------------------------

def generate_game_action_source(filepath, header_include, func_suffix,
                                leaf_struct_name, leaf_type_file):
    """Generate the game_action .c file under
    ./source/game_action/implemented/."""
    fields = parse_fields(leaf_type_file)

    fields_params = ""
    for ftype, fname in fields:
        fields_params += f",\n        {ftype} {fname}"

    content = (
        f"/// This file is deterministically generated.\n"
        f"/// Implement the #error stubs below.\n"
        f'#include "{header_include}"\n'
        f'#include "defines.h"\n'
        f'#include "defines_weak.h"\n'
        f'#include "game.h"\n'
        f'#include "game_action/game_action_logic_entry.h"\n'
        f'#include "game_action/game_action_logic_table.h"\n'
        f'#include "process/process.h"\n'
        f"\n"
        f"void m_process__game_action__{func_suffix}(\n"
        f"        Process *p_this_process,\n"
        f"        Game *p_game) {{\n"
        f'#error "Implement m_process__game_action__{func_suffix}"\n'
        f"}}\n"
        f"\n"
        f"void register_game_action__{func_suffix}_for__server(\n"
        f"        Game_Action_Logic_Table *p_game_action_logic_table) {{\n"
        f'#error "Implement register_game_action__{func_suffix}_for__server"\n'
        f"}}\n"
        f"\n"
        f"void register_game_action__{func_suffix}_for__client(\n"
        f"        Game_Action_Logic_Table *p_game_action_logic_table) {{\n"
        f'#error "Implement register_game_action__{func_suffix}_for__client"\n'
        f"}}\n"
        f"\n"
        f"void initialize_game_action_for__{func_suffix}(\n"
        f"        Game_Action *p_game_action{fields_params}) {{\n"
        f'#error "Implement initialize_game_action_for__{func_suffix}"\n'
        f"}}\n"
    )
    write_file(filepath, content)


# ---------------------------------------------------------------------------
# Registrar helpers
# ---------------------------------------------------------------------------

def ensure_include_in_source_file(filepath, include_line):
    """Ensure an #include line exists in a source file.

    Inserts after the last existing #include line.
    Returns True if added, False if already present.
    """
    text = read_file(filepath)
    if include_line in text:
        return False

    lines = text.split("\n")
    last_include_idx = -1
    for i, line in enumerate(lines):
        if line.strip().startswith("#include"):
            last_include_idx = i

    if last_include_idx >= 0:
        lines.insert(last_include_idx + 1, include_line)
    else:
        lines.insert(0, include_line)

    write_file(filepath, "\n".join(lines))
    return True


def ensure_call_in_named_gen_region(filepath, region_name, call_text):
    """Ensure a registration call exists between named GEN-BEGIN/GEN-END
    markers.

    Returns True if added, False if already present.
    """
    begin_marker = f"// GEN-{region_name}-BEGIN"
    end_marker = f"// GEN-{region_name}-END"

    text = read_file(filepath)

    if begin_marker not in text:
        _fatal(f"{begin_marker} not found in {filepath}")
    if end_marker not in text:
        _fatal(f"{end_marker} not found in {filepath}")

    # Check if already present
    begin_idx = text.find(begin_marker)
    end_idx = text.find(end_marker)
    region = text[begin_idx:end_idx]
    if call_text in region:
        return False

    # Build the indented call block
    insertion = (
        f"\n"
        f"    {call_text}(\n"
        f"            p_game_action_logic_table);\n"
    )

    text = text[:end_idx] + insertion + "    " + text[end_idx:]
    write_file(filepath, text)
    return True


# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate game action type headers, boilerplate .h/.c, "
                    "and registrar wiring for a Lavender project.")
    parser.add_argument("path",
                        help="Relative path to leaf type "
                             "(e.g. collisions/aabb/update__pos_vec_i32.h)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose output")
    args = parser.parse_args()

    verbose = args.verbose

    def log_verbose(msg):
        if verbose:
            print(msg)

    rel_path = args.path
    parts = validate_path(rel_path)

    leaf_name = parts[-1]
    dir_parts = parts[:-1]

    # ------------------------------------------------------------------
    # Step 1: Create directories and intermediate union headers
    # ------------------------------------------------------------------
    current_dir = BASE_DIR
    accumulated_prefix = ""

    root_union_header_name = ""
    root_union_dir_path = ""

    for i, component in enumerate(dir_parts):
        current_dir = os.path.join(current_dir, component)

        if not accumulated_prefix:
            accumulated_prefix = component
        else:
            accumulated_prefix = f"{accumulated_prefix}__{component}"

        os.makedirs(current_dir, exist_ok=True)

        union_header_name = f"ga_types__{accumulated_prefix}.h"
        union_header_path = os.path.join(current_dir, union_header_name)

        upper_prefix = to_upper(accumulated_prefix)
        guard_name = f"GA_TYPES__{upper_prefix}_H"
        struct_name = to_struct_name(accumulated_prefix)
        injection_tag = upper_prefix

        # Track root for step 5
        if i == 0:
            root_union_header_name = union_header_name
            root_union_dir_path = dir_parts[0]

        if not os.path.isfile(union_header_path):
            log_verbose(f"Generating union header: {union_header_path}")
            generate_union_header(
                union_header_path, accumulated_prefix,
                guard_name, struct_name, injection_tag)

        # Generate accessors for union header fields (if any)
        if os.path.isfile(union_header_path):
            union_fields = parse_fields(union_header_path)
            if union_fields:
                log_verbose(
                    f"Generating accessors for union fields in "
                    f"{union_header_path}")
                for ftype, fname in union_fields:
                    generate_accessors_for_field(
                        union_header_path, struct_name,
                        ftype, fname, "union")

        # If not the first level, parent union header includes this one
        if i > 0:
            parent_prefix = build_prefix(dir_parts, i)
            parent_dir = os.path.dirname(current_dir)
            parent_header_name = f"ga_types__{parent_prefix}.h"
            parent_header_path = os.path.join(
                parent_dir, parent_header_name)

            include_dir_path = "/".join(dir_parts[:i + 1])
            include_line = (
                f'#include "game_action/types/implemented/'
                f'{include_dir_path}/{union_header_name}"')

            if os.path.isfile(parent_header_path):
                log_verbose(
                    f"Ensuring include of {union_header_name} in "
                    f"{parent_header_path}")
                ensure_include_in_gen_region(
                    parent_header_path, include_line)

    # ------------------------------------------------------------------
    # Step 2: Create the leaf header
    # ------------------------------------------------------------------
    if accumulated_prefix:
        leaf_prefix = f"{accumulated_prefix}__{leaf_name}"
    else:
        leaf_prefix = leaf_name

    leaf_header_name = f"ga_type__{leaf_prefix}.h"

    if dir_parts:
        leaf_dir = current_dir
    else:
        leaf_dir = BASE_DIR
        os.makedirs(leaf_dir, exist_ok=True)

    leaf_header_path = os.path.join(leaf_dir, leaf_header_name)

    upper_leaf_prefix = to_upper(leaf_prefix)
    leaf_guard = f"GA_TYPE__{upper_leaf_prefix}_H"
    leaf_impl_guard = f"GA_TYPE__{upper_leaf_prefix}_IMPL_H"
    leaf_struct_name = to_struct_name(leaf_prefix)

    if not os.path.isfile(leaf_header_path):
        log_verbose(f"Generating leaf header: {leaf_header_path}")
        generate_leaf_header(
            leaf_header_path, leaf_prefix,
            leaf_guard, leaf_struct_name, leaf_impl_guard)

    # ------------------------------------------------------------------
    # Step 3: Ensure the parent union header includes the leaf
    # ------------------------------------------------------------------
    if dir_parts:
        parent_union_prefix = accumulated_prefix
        parent_union_header_name = f"ga_types__{parent_union_prefix}.h"
        parent_union_header_path = os.path.join(
            leaf_dir, parent_union_header_name)

        include_dir_path = "/".join(dir_parts)
        leaf_include_line = (
            f'#include "game_action/types/implemented/'
            f'{include_dir_path}/{leaf_header_name}"')

        if os.path.isfile(parent_union_header_path):
            log_verbose(
                f"Ensuring include of {leaf_header_name} in "
                f"{parent_union_header_path}")
            ensure_include_in_gen_region(
                parent_union_header_path, leaf_include_line)

    # ------------------------------------------------------------------
    # Step 4: Accessor generation for the leaf header
    # ------------------------------------------------------------------
    if os.path.isfile(leaf_header_path):
        fields = parse_fields(leaf_header_path)
        if fields:
            log_verbose(
                f"Generating accessors for fields in {leaf_header_path}")
            for ftype, fname in fields:
                generate_accessors_for_field(
                    leaf_header_path, leaf_struct_name,
                    ftype, fname, "leaf")
        else:
            log_verbose(
                f"No fields found in {leaf_header_path}. Add fields "
                f"between FIELDS-BEGIN and FIELDS-END, then re-run.")

    # ------------------------------------------------------------------
    # Step 5: Ensure root union header is included in
    #         ga_types__implemented.h
    # ------------------------------------------------------------------
    implemented_header = os.path.join(
        BASE_DIR, "ga_types__implemented.h")

    if root_union_header_name and os.path.isfile(implemented_header):
        root_include_line = (
            f'#include "game_action/types/implemented/'
            f'{root_union_dir_path}/{root_union_header_name}"')
        log_verbose(
            f"Ensuring include of {root_union_header_name} in "
            f"{implemented_header}")
        ensure_include_in_gen_region(
            implemented_header, root_include_line)
    elif root_union_header_name and not os.path.isfile(implemented_header):
        log_verbose(
            f"Warning: {implemented_header} not found. "
            f"Cannot add root include.")
    elif not dir_parts:
        # Leaf directly under implemented/
        leaf_include_for_root = (
            f'#include "game_action/types/implemented/'
            f'{leaf_header_name}"')
        if os.path.isfile(implemented_header):
            log_verbose(
                f"Ensuring include of {leaf_header_name} in "
                f"{implemented_header}")
            ensure_include_in_gen_region(
                implemented_header, leaf_include_for_root)
        else:
            log_verbose(
                f"Warning: {implemented_header} not found. "
                f"Cannot add root include.")

    # ------------------------------------------------------------------
    # Step 6: Generate game_action .h and .c files
    # ------------------------------------------------------------------
    func_suffix = leaf_prefix

    # Build subdirectory path
    ga_subdir_path = "/".join(dir_parts) if dir_parts else ""

    # Header file path
    ga_include_dir = os.path.join(
        ".", "include", "game_action", "implemented")
    if ga_subdir_path:
        ga_include_dir = os.path.join(ga_include_dir, ga_subdir_path)
    os.makedirs(ga_include_dir, exist_ok=True)

    ga_header_filename = f"game_action__{leaf_prefix}.h"
    ga_header_path = os.path.join(ga_include_dir, ga_header_filename)

    # Source file path
    ga_source_dir = os.path.join(
        ".", "source", "game_action", "implemented")
    if ga_subdir_path:
        ga_source_dir = os.path.join(ga_source_dir, ga_subdir_path)
    os.makedirs(ga_source_dir, exist_ok=True)

    ga_source_filename = f"game_action__{leaf_prefix}.c"
    ga_source_path = os.path.join(ga_source_dir, ga_source_filename)

    # Guard name for the .h
    ga_header_guard = f"GAME_ACTION__{to_upper(leaf_prefix)}_H"

    # Type include path (relative from include/)
    type_include_rel_path = "game_action/types/implemented"
    if ga_subdir_path:
        type_include_rel_path += f"/{ga_subdir_path}"
    type_include_rel_path += f"/{leaf_header_name}"

    # Build union include paths (all intermediate union headers)
    union_include_paths = []
    union_acc_prefix = ""
    union_dir_acc = ""
    for i, dp in enumerate(dir_parts):
        if not union_acc_prefix:
            union_acc_prefix = dp
            union_dir_acc = dp
        else:
            union_acc_prefix = f"{union_acc_prefix}__{dp}"
            union_dir_acc = f"{union_dir_acc}/{dp}"
        union_hdr = (
            f"game_action/types/implemented/"
            f"{union_dir_acc}/ga_types__{union_acc_prefix}.h")
        union_include_paths.append(union_hdr)

    # Header include path for the .c file
    ga_header_include_path = "game_action/implemented"
    if ga_subdir_path:
        ga_header_include_path += f"/{ga_subdir_path}"
    ga_header_include_path += f"/{ga_header_filename}"

    # Generate .h if missing
    if not os.path.isfile(ga_header_path):
        log_verbose(f"Generating game action header: {ga_header_path}")
        generate_game_action_header(
            ga_header_path, leaf_prefix, leaf_struct_name,
            ga_header_guard, func_suffix,
            type_include_rel_path, union_include_paths,
            leaf_header_path)
    else:
        log_verbose(
            f"Game action header already exists: {ga_header_path}")

    # Generate .c if missing
    if not os.path.isfile(ga_source_path):
        log_verbose(f"Generating game action source: {ga_source_path}")
        generate_game_action_source(
            ga_source_path, ga_header_include_path,
            func_suffix, leaf_struct_name, leaf_header_path)
    else:
        log_verbose(
            f"Game action source already exists: {ga_source_path}")

    # ------------------------------------------------------------------
    # Step 7: Register in game_action_registrar.c
    # ------------------------------------------------------------------
    registrar_path = os.path.join(
        ".", "source", "game_action", "implemented",
        "game_action_registrar.c")

    if os.path.isfile(registrar_path):
        # Ensure the #include for the game action header is present
        registrar_include_line = f'#include "{ga_header_include_path}"'
        if ensure_include_in_source_file(
                registrar_path, registrar_include_line):
            log_verbose(
                f"Added include of {ga_header_filename} to "
                f"{registrar_path}")
        else:
            log_verbose(
                f"Include of {ga_header_filename} already present in "
                f"{registrar_path}")

        # Add registration calls to each GEN region
        offline_call = (
            f"register_game_action__{func_suffix}_for__offline")
        client_call = (
            f"register_game_action__{func_suffix}_for__client")
        server_call = (
            f"register_game_action__{func_suffix}_for__server")

        if ensure_call_in_named_gen_region(
                registrar_path, "OFFLINE", offline_call):
            log_verbose(
                f"Added {offline_call} to GEN-OFFLINE region")
        else:
            log_verbose(
                f"{offline_call} already present in GEN-OFFLINE region")

        if ensure_call_in_named_gen_region(
                registrar_path, "CLIENT", client_call):
            log_verbose(
                f"Added {client_call} to GEN-CLIENT region")
        else:
            log_verbose(
                f"{client_call} already present in GEN-CLIENT region")

        if ensure_call_in_named_gen_region(
                registrar_path, "SERVER", server_call):
            log_verbose(
                f"Added {server_call} to GEN-SERVER region")
        else:
            log_verbose(
                f"{server_call} already present in GEN-SERVER region")
    else:
        log_verbose(
            f"Warning: {registrar_path} not found. "
            f"Cannot add registration calls.")

    # Output the leaf header path on success
    print(leaf_header_path)


if __name__ == "__main__":
    main()
