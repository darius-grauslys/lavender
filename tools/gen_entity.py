#!/usr/bin/env python3
"""
Generate entity boilerplate .h and .c files from the empty-entity templates,
and ensure the entity is registered in entity_registrar.c.

Usage example:
    python tools/gen_entity.py --name zombie \\
        --gen-f-Dispose --gen-f-Update --gen-f-Enable --gen-f-Disable \\
        --gen-f-Serialize --gen-f-Deserialize

    python tools/gen_entity.py --name skeleton --output undead \\
        --gen-f-Update --f-Update m_entity_handler__update_skeleton
"""

import argparse
import os
import re
import sys

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

FUNC_NAMES = ["Dispose", "Update", "Enable", "Disable", "Serialize", "Deserialize"]


def _validate_name(value):
    if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', value):
        raise argparse.ArgumentTypeError(
            f"Invalid --name '{value}': must start with an alpha character or '_' "
            "and contain only alphanumeric characters and '_'."
        )
    return value


def _validate_m_prefix(value):
    if not value.startswith("m_"):
        raise argparse.ArgumentTypeError(
            f"Invalid function value '{value}': must begin with 'm_'."
        )
    return value


def build_parser():
    parser = argparse.ArgumentParser(
        description="Generate an entity .h/.c pair and register it.")

    parser.add_argument("--name", required=True, type=_validate_name,
                        help="Entity name (alphanumeric + '_', starts with alpha or '_').")
    parser.add_argument("--output", default=None,
                        help="Optional sub-directory under entity/implemented/.")

    for func in FUNC_NAMES:
        parser.add_argument(f"--f-{func}", default=None, type=_validate_m_prefix,
                            metavar="M_FUNC",
                            help=f"Custom function pointer for {func} (must start with 'm_').")
        parser.add_argument(f"--gen-f-{func}", action="store_true", default=False,
                            help=f"Generate the default {func} handler body.")

    parser.add_argument("--f-Update-Begin", default=None, type=_validate_m_prefix,
                        metavar="M_FUNC",
                        help="Custom function pointer for the Update-Begin slot (must start with 'm_').")

    return parser

# ---------------------------------------------------------------------------
# Name helpers
# ---------------------------------------------------------------------------


def to_lower(name):
    return name.lower()


def to_upper(name):
    return name.upper()


def to_entity_kind(name):
    """
    Convert e.g. 'zombie_warrior' -> 'Zombie_Warrior'
    (first letter of each '_'-separated word upper-cased).
    """
    return "_".join(word.capitalize() for word in name.split("_"))

# ---------------------------------------------------------------------------
# Header generation
# ---------------------------------------------------------------------------


def generate_header(name, output_subdir):
    upper = to_upper(name)
    lower = to_lower(name)

    if output_subdir:
        guard = f"AG__ENTITY_{output_subdir.upper().replace('/', '_')}_{upper}_H"
    else:
        guard = f"AG__ENTITY_{upper}_H"

    lines = [
        f"#ifndef {guard}",
        f"#define {guard}",
        "",
        '#include "defines.h"',
        "",
        f"void register_entity_{lower}_into__entity_manager(",
        "        Entity_Manager *p_entity_manager);",
        "",
        f"#endif",
        "",
    ]
    return "\n".join(lines)

# ---------------------------------------------------------------------------
# Source generation
# ---------------------------------------------------------------------------


def generate_source(name, args):
    lower = to_lower(name)
    kind = to_entity_kind(name)

    gen_flags = {}
    f_values = {}
    for func in FUNC_NAMES:
        gen_flags[func] = getattr(args, f"gen_f_{func}")
        f_values[func] = getattr(args, f"f_{func}")

    f_update_begin = getattr(args, "f_Update_Begin", None)

    parts = []

    # -- includes --
    parts.append('#include "defines.h"')
    parts.append('#include "defines_weak.h"')
    parts.append('#include "entity/entity.h"')
    parts.append("")

    # -- Dispose handler --
    if gen_flags["Dispose"]:
        parts.append(f"void m_entity_handler__dispose_{lower}(")
        parts.append("        Entity *p_this_entity,")
        parts.append("        Game *p_game,")
        parts.append("        World *p_world) {")
        parts.append("    m_entity_dispose_handler__default(")
        parts.append("            p_this_entity, ")
        parts.append("            p_game, ")
        parts.append("            p_world);")
        parts.append("}")
        parts.append("")

    # -- Update handler --
    if gen_flags["Update"]:
        parts.append(f"void m_entity_handler__update_{lower}(")
        parts.append("        Entity *p_this_entity,")
        parts.append("        Game *p_game,")
        parts.append("        World *p_world) {")
        parts.append("}")
        parts.append("")

    # -- Enable handler --
    if gen_flags["Enable"]:
        parts.append(f"void m_entity_handler__enable_{lower}(")
        parts.append("        Entity *p_this_entity,")
        parts.append("        Game *p_game,")
        parts.append("        World *p_world) {")
        parts.append("    m_entity_enable_handler__default(")
        parts.append("            p_this_entity, ")
        parts.append("            p_game, ")
        parts.append("            p_world);")
        parts.append("}")
        parts.append("")

    # -- Disable handler --
    if gen_flags["Disable"]:
        parts.append(f"void m_entity_handler__disable_{lower}(")
        parts.append("        Entity *p_this_entity,")
        parts.append("        Game *p_game,")
        parts.append("        World *p_world) {")
        parts.append("    m_entity_disable_handler__default(")
        parts.append("            p_this_entity, ")
        parts.append("            p_game, ")
        parts.append("            p_world);")
        parts.append("}")
        parts.append("")

    # -- Serialize handler --
    if gen_flags["Serialize"]:
        parts.append(f"PLATFORM_Write_File_Error m_entity_serialization_handler__{lower}(")
        parts.append("        Entity *p_entity_self, ")
        parts.append("        Game *p_game,")
        parts.append("        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,")
        parts.append("        World *p_world,")
        parts.append("        Serialization_Request *p_serialization_request) {")
        parts.append("    return PLATFORM_Write_File_Error__None;")
        parts.append("}")
        parts.append("")

    # -- Deserialize handler --
    if gen_flags["Deserialize"]:
        parts.append(f"PLATFORM_Read_File_Error *m_entity_deserialization_handler__{lower}(")
        parts.append("        Entity *p_entity_self, ")
        parts.append("        Game *p_game,")
        parts.append("        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,")
        parts.append("        World *p_world,")
        parts.append("        Serialization_Request *p_serialization_request) {")
        parts.append("    return PLATFORM_Read_File_Error__None;")
        parts.append("}")
        parts.append("")

    # -- registration function (always generated) --
    parts.append(f"void register_entity_{lower}_into__entity_manager(")
    parts.append("        Entity_Manager *p_entity_manager) {")
    parts.append(f"    Entity_Functions entity_functions__{lower};")
    parts.append(f"    memset(&entity_functions__{lower},")
    parts.append("            0,")
    parts.append("            sizeof(Entity_Functions));")
    parts.append("")

    # Update handler assignment
    if f_update_begin:
        parts.append(f"    entity_functions__{lower}.m_entity_update_handler =")
        parts.append(f"        {f_update_begin};")
    elif f_values["Update"]:
        parts.append(f"    entity_functions__{lower}.m_entity_update_handler =")
        parts.append(f"        {f_values['Update']};")
    elif gen_flags["Update"]:
        parts.append(f"    entity_functions__{lower}.m_entity_update_handler =")
        parts.append(f"        m_entity_handler__update_{lower};")
    parts.append("")

    # Dispose handler assignment
    if gen_flags["Dispose"]:
        val = f_values["Dispose"] if f_values["Dispose"] else f"m_entity_handler__dispose_{lower}"
        parts.append(f"    entity_functions__{lower}.m_entity_dispose_handler =")
        parts.append(f"        {val};")
        parts.append("")

    # Enable handler assignment
    if gen_flags["Enable"]:
        val = f_values["Enable"] if f_values["Enable"] else f"m_entity_handler__enable_{lower}"
        parts.append(f"    entity_functions__{lower}.m_entity_enable_handler =")
        parts.append(f"        {val};")
        parts.append("")

    # Disable handler assignment
    if gen_flags["Disable"]:
        val = f_values["Disable"] if f_values["Disable"] else f"m_entity_handler__disable_{lower}"
        parts.append(f"    entity_functions__{lower}.m_entity_disable_handler =")
        parts.append(f"        {val};")
        parts.append("")

    # Serialize handler assignment
    if gen_flags["Serialize"]:
        val = f_values["Serialize"] if f_values["Serialize"] else f"m_entity_serialization_handler__{lower}"
        parts.append(f"    entity_functions__{lower}.m_entity_serialize_handler =")
        parts.append(f"        {val};")
        parts.append("")

    # Deserialize handler assignment
    if gen_flags["Deserialize"]:
        val = f_values["Deserialize"] if f_values["Deserialize"] else f"m_entity_deserialization_handler__{lower}"
        parts.append(f"    entity_functions__{lower}.m_entity_deserialize_handler =")
        parts.append(f"        {val};")
        parts.append("")

    parts.append("    register_entity_into__entity_manager(")
    parts.append("            p_entity_manager, ")
    parts.append(f"            Entity_Kind__{kind},")
    parts.append(f"            entity_functions__{lower});")
    parts.append("}")
    parts.append("")

    return "\n".join(parts)

# ---------------------------------------------------------------------------
# Registrar patching
# ---------------------------------------------------------------------------

REGISTRAR_PATH = os.path.join("source", "entity", "implemented", "entity_registrar.c")


def patch_registrar(name, header_include_path):
    lower = to_lower(name)
    call = f"register_entity_{lower}_into__entity_manager(p_entity_manager);"

    if not os.path.isfile(REGISTRAR_PATH):
        print(f"WARNING: {REGISTRAR_PATH} not found – skipping registrar patch.",
              file=sys.stderr)
        return

    with open(REGISTRAR_PATH, "r") as f:
        content = f.read()

    # Locate the GEN-BEGIN / GEN-END block
    pattern = re.compile(
        r'(    // GEN-BEGIN\n)(.*?)(    // GEN-END)',
        re.DOTALL,
    )
    m = pattern.search(content)
    if not m:
        print(f"WARNING: Could not find GEN-BEGIN/GEN-END in {REGISTRAR_PATH}.",
              file=sys.stderr)
        return

    gen_block = m.group(2)

    # Already registered?
    if call in gen_block:
        print(f"Entity '{name}' already registered in {REGISTRAR_PATH}.")
        return

    # Build the include directive
    include_directive = f'#include "{header_include_path}"'

    # Add include at top of file if not present
    if include_directive not in content:
        # Insert after the last #include before the GEN-BEGIN block
        last_include = content.rfind("#include", 0, m.start())
        if last_include != -1:
            end_of_line = content.index("\n", last_include)
            content = (content[:end_of_line + 1]
                       + include_directive + "\n"
                       + content[end_of_line + 1:])
        else:
            content = include_directive + "\n" + content

    # Re-search after possible include insertion shifted offsets
    m = pattern.search(content)
    gen_block = m.group(2)

    # Append the registration call inside the GEN block
    new_gen_block = gen_block
    if not new_gen_block.endswith("\n"):
        new_gen_block += "\n"
    new_gen_block += f"    {call}\n"

    content = (content[:m.start(2)]
               + new_gen_block
               + content[m.start(3):])

    with open(REGISTRAR_PATH, "w") as f:
        f.write(content)

    print(f"Registered entity '{name}' in {REGISTRAR_PATH}.")

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = build_parser()
    args = parser.parse_args()

    name = args.name
    output_subdir = args.output  # may be None

    # Build target directories relative to cwd
    if output_subdir:
        include_dir = os.path.join("include", "entity", "implemented", output_subdir)
        source_dir = os.path.join("source", "entity", "implemented", output_subdir)
    else:
        include_dir = os.path.join("include", "entity", "implemented")
        source_dir = os.path.join("source", "entity", "implemented")

    os.makedirs(include_dir, exist_ok=True)
    os.makedirs(source_dir, exist_ok=True)

    lower = to_lower(name)
    h_filename = f"{lower}.h"
    c_filename = f"{lower}.c"

    h_path = os.path.join(include_dir, h_filename)
    c_path = os.path.join(source_dir, c_filename)

    if os.path.exists(h_path):
        print(f"ERROR: {h_path} already exists. Aborting.", file=sys.stderr)
        sys.exit(1)
    if os.path.exists(c_path):
        print(f"ERROR: {c_path} already exists. Aborting.", file=sys.stderr)
        sys.exit(1)

    # Generate contents
    header_content = generate_header(name, output_subdir)
    source_content = generate_source(name, args)

    with open(h_path, "w") as f:
        f.write(header_content)
    print(f"Generated header: {h_path}")

    with open(c_path, "w") as f:
        f.write(source_content)
    print(f"Generated source: {c_path}")

    # Build the include path as it would appear in a #include directive
    if output_subdir:
        header_include_path = f"entity/implemented/{output_subdir}/{h_filename}"
    else:
        header_include_path = f"entity/implemented/{h_filename}"

    patch_registrar(name, header_include_path)


if __name__ == "__main__":
    main()
