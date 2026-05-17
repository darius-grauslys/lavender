#!/usr/bin/env python3
"""gen_chunk_generator.py — Register Chunk_Generator_Kind entries and create stubs.

Usage:
    python tools/lavender_tools/gen_chunk_generator.py --name <Name>

Adds a ``Chunk_Generator_Kind__<Name>`` enum entry to
``include/types/implemented/world/chunk_generator_kind.h``,
creates stub ``.h/.c`` files in ``include/world/implemented/`` and
``source/world/implemented/``, and patches ``chunk_generator_registrar.c``.
"""

from __future__ import annotations

import argparse
import os
import re
import sys

from lavender_tools import tool_history

_NAME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]*$")

_KIND_HEADER_REL = "include/types/implemented/world/chunk_generator_kind.h"
_REGISTRAR_SOURCE_REL = "source/world/implemented/chunk_generator_registrar.c"
_REGISTRAR_HEADER_REL = "include/world/implemented/chunk_generator_registrar.h"
_STUB_HEADER_REL = "include/world/implemented/chunk_generator__{name_lower}.h"
_STUB_SOURCE_REL = "source/world/implemented/chunk_generator__{name_lower}.c"

_GEN_BEGIN = "// GEN-BEGIN"
_GEN_END = "// GEN-END"


def _find_gen_block(content, begin_tag, end_tag):
    b = content.find(begin_tag)
    if b == -1:
        return None
    after_b = content.find("\n", b)
    if after_b == -1:
        return None
    after_b += 1
    e = content.find(end_tag, after_b)
    if e == -1:
        return None
    return (after_b, e)


def _append_to_block(content, begin_tag, end_tag, new_text, dedup_key):
    bounds = _find_gen_block(content, begin_tag, end_tag)
    if bounds is None:
        print(f"  [skip] {begin_tag}/{end_tag} markers not found.")
        return content
    existing = content[bounds[0]:bounds[1]]
    if dedup_key in existing:
        print(f"  [skip] already present: {dedup_key}")
        return content
    insert = new_text if new_text.endswith("\n") else new_text + "\n"
    return content[:bounds[1]] + insert + content[bounds[1]:]


def _update_kind_enum(name: str) -> bool:
    entry = f"Chunk_Generator_Kind__{name}"
    if not os.path.isfile(_KIND_HEADER_REL):
        print(f"ERROR: {_KIND_HEADER_REL} not found.")
        return False

    with open(_KIND_HEADER_REL, "r") as fh:
        content = fh.read()

    if entry in content:
        print(f"  [enum] {entry} already exists, skipping.")
        return True

    content = _append_to_block(content, _GEN_BEGIN, _GEN_END,
                               f"    {entry},", entry)

    with open(_KIND_HEADER_REL, "w") as fh:
        fh.write(content)
    tool_history.record_modify(_KIND_HEADER_REL)
    print(f"  [enum] added {entry}")
    return True


def _create_stub_files(name: str, name_lower: str) -> bool:
    h_path = _STUB_HEADER_REL.format(name_lower=name_lower)
    c_path = _STUB_SOURCE_REL.format(name_lower=name_lower)

    guard = f"CHUNK_GENERATOR__{name_lower.upper()}_H"
    func_name = f"m_chunk_generator__{name_lower}"

    if not os.path.isfile(h_path):
        os.makedirs(os.path.dirname(h_path), exist_ok=True)
        h_content = (
            f"#ifndef {guard}\n"
            f"#define {guard}\n"
            f"\n"
            f"#include \"defines.h\"\n"
            f"\n"
            f"void {func_name}(\n"
            f"        Process *p_this_process,\n"
            f"        Game *p_game);\n"
            f"\n"
            f"#endif\n"
        )
        with open(h_path, "w") as fh:
            fh.write(h_content)
        tool_history.record_create(h_path)
        print(f"  [created] {h_path}")
    else:
        print(f"  [skip] {h_path} already exists.")

    if not os.path.isfile(c_path):
        os.makedirs(os.path.dirname(c_path), exist_ok=True)
        c_content = (
            f"#include \"world/implemented/chunk_generator__{name_lower}.h\"\n"
            f"#include \"defines.h\"\n"
            f"#include \"defines_weak.h\"\n"
            f"#include \"world/chunk.h\"\n"
            f"#include \"world/global_space.h\"\n"
            f"\n"
            f"void {func_name}(\n"
            f"        Process *p_this_process,\n"
            f"        Game *p_game) {{\n"
            f"    // TODO: implement chunk generation for {name}\n"
            f"    Global_Space *p_global_space = p_this_process->p_process_data;\n"
            f"    Chunk *p_chunk = get_p_chunk_from__global_space(p_global_space);\n"
            f"    if (!p_chunk) return;\n"
            f"\n"
            f"    // Generate tiles here.\n"
            f"}}\n"
        )
        with open(c_path, "w") as fh:
            fh.write(c_content)
        tool_history.record_create(c_path)
        print(f"  [created] {c_path}")
    else:
        print(f"  [skip] {c_path} already exists.")

    return True


def _update_registrar(name: str, name_lower: str) -> bool:
    path = _REGISTRAR_SOURCE_REL
    if not os.path.isfile(path):
        print(f"ERROR: {path} not found.")
        return False

    with open(path, "r") as fh:
        content = fh.read()

    func_name = f"m_chunk_generator__{name_lower}"
    entry = f"Chunk_Generator_Kind__{name}"

    if func_name in content:
        print(f"  [registrar] {func_name} already registered, skipping.")
        return True

    # Add include
    include_line = f'#include "world/implemented/chunk_generator__{name_lower}.h"'
    if include_line not in content:
        # Find last #include and insert after
        lines = content.split("\n")
        last_inc = -1
        for i, line in enumerate(lines):
            if line.startswith("#include"):
                last_inc = i
        if last_inc >= 0:
            lines.insert(last_inc + 1, include_line)
            content = "\n".join(lines)

    # Add registration call before closing brace
    reg_call = (
        f"    register_chunk_generator_into__chunk_generator_table(\n"
        f"            p_chunk_generator_table,\n"
        f"            {entry},\n"
        f"            {func_name});"
    )

    lines = content.split("\n")
    closing = -1
    for i, line in enumerate(lines):
        if line.strip() == "}":
            closing = i
    if closing == -1:
        print(f"ERROR: closing brace not found in {path}.")
        return False

    lines.insert(closing, reg_call)
    content = "\n".join(lines)

    with open(path, "w") as fh:
        fh.write(content)
    tool_history.record_modify(path)
    print(f"  [registrar] added {func_name} to {path}")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="gen_chunk_generator.py",
        description="Register a Chunk_Generator_Kind and create stub files.",
    )
    parser.add_argument("--name", required=True,
                        help="Chunk generator name (e.g., Overworld, Underground).")

    args = parser.parse_args()
    name = args.name
    name_lower = name.lower()

    if not _NAME_RE.match(name):
        print(f"ERROR: Invalid name '{name}'.")
        sys.exit(1)

    if not _update_kind_enum(name):
        sys.exit(1)
    if not _create_stub_files(name, name_lower):
        sys.exit(1)
    if not _update_registrar(name, name_lower):
        sys.exit(1)

    print(f"Done: Chunk_Generator_Kind__{name}")


if __name__ == "__main__":
    main()
