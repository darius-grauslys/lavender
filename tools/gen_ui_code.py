#!/usr/bin/env python3
"""gen_ui_code – generate C source/header from a UI XML description.

Usage:
    python tools/gen_ui_code.py <source.xml> [config_field value ...]

This script reads the same XML format consumed by ``ui_builder.py`` and
produces functionally identical C code with correct indentation.
It also updates ``source/ui/implemented/ui_window_registrar.c`` to include
and register the generated UI window function.

The generated .c/.h files are **code-identical** to ``ui_builder.py``
output except for whitespace/indentation improvements.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import deque
from typing import Dict, List, Optional, Sequence, Tuple

# ---------------------------------------------------------------------------
# Tiny XML helpers
# ---------------------------------------------------------------------------

def xml_str(node, attr: str, default: str = "") -> str:
    return node.attrib.get(attr, default)


def xml_int(node, attr: str, default: int = 0) -> int:
    raw = node.attrib.get(attr)
    return default if raw is None else int(raw)


def xml_int_tuple(node, attr: str, default: Tuple[int, ...] = ()) -> Tuple[int, ...]:
    raw = node.attrib.get(attr)
    return default if raw is None else tuple(map(int, raw.split(",")))


# ---------------------------------------------------------------------------
# Small value objects
# ---------------------------------------------------------------------------

class Include:
    def __init__(self, path: str):
        self.path = path


class UISignature:
    def __init__(self, xml_tag: str, c_signatures: str):
        self.xml_tag = xml_tag
        self.c_signatures = c_signatures


# ---------------------------------------------------------------------------
# Config – parsed from the <config> XML node
# ---------------------------------------------------------------------------

class Config:
    def __init__(self, path_to_source_xml: str):
        self.is_visualizing: bool = True
        self.BACKEND: str = "PLATFORM"
        self.signatures: List[UISignature] = []
        self.source_xml: str = path_to_source_xml
        self.source_name: str = os.path.splitext(
            os.path.basename(self.source_xml)
        )[0]
        self.associated_header_sub_dir_in__include_folder: str = ""
        self.output__c_path: str = "./output.c"
        self.output__h_path: str = "./output.h"
        self.window_size: Tuple[int, int] = (256, 256)
        self.includes: List[Include] = []
        self.base_dir: str = "./"
        self.is_outputting: bool = True

    def update_from_xml(self, xml_node) -> None:
        self.includes = []
        for elem in xml_node:
            tag = elem.tag
            if tag == "ui_func_signature":
                self.signatures.append(
                    UISignature(
                        xml_str(elem, "for", ""),
                        xml_str(elem, "c_signatures", ""),
                    )
                )
            elif tag == "platform":
                self.BACKEND = xml_str(elem, "target", self.BACKEND)
                self.window_size = xml_int_tuple(
                    elem, "size", self.window_size
                )
            elif tag == "output":
                self.base_dir = xml_str(elem, "base_dir", self.base_dir)
                self.output__c_path = xml_str(
                    elem, "c_path", self.output__c_path
                )
                self.output__h_path = xml_str(
                    elem, "h_path", self.output__h_path
                )
            elif tag == "background":
                pass  # only used by viewer
            elif tag == "include":
                self.associated_header_sub_dir_in__include_folder = xml_str(
                    elem, "sub_dir", ""
                )
                for header in elem:
                    self.includes.append(
                        Include(xml_str(header, "path", ""))
                    )


# ---------------------------------------------------------------------------
# CodeWriter – accumulates C source with correct indentation
# ---------------------------------------------------------------------------

TAB = "    "
P_UI_MANAGER = "p_ui_manager"
P_UI_ITERATOR = "p_ui_iterator"


class CodeWriter:
    def __init__(self):
        self._parts: List[str] = []
        self.indent_level: int = 0

    def raw(self, text: str) -> None:
        self._parts.append(text)

    def line(self, text: str = "", *, semicolon: bool = False) -> None:
        prefix = TAB * self.indent_level
        suffix = ";\n" if semicolon else "\n"
        self._parts.append(f"{prefix}{text}{suffix}")

    def blank_line(self) -> None:
        self._parts.append("\n")

    def stmt(self, text: str) -> None:
        self.line(text, semicolon=True)

    def call_str(self, func: str, args: Sequence) -> str:
        joined = ", ".join(str(a) for a in args)
        return f"{func}({joined})"

    def write_call(self, func: str, args: Sequence) -> None:
        self.stmt(self.call_str(func, args))

    def write_assignment(self, lhs: str, rhs: str) -> None:
        self.stmt(f"{lhs} = {rhs}")

    def write_local_decl(self, c_type: str, name: str, init: str = "0") -> None:
        self.stmt(f"{c_type}{name} = {init}")

    def write_include(self, path: str) -> None:
        self.raw(f"#include <{path}>\n")

    def open_brace(self, header: str = "") -> None:
        if header:
            self.raw(f"{header}{{\n")
        else:
            self.raw("{\n")
        self.indent_level += 1

    def close_brace(self) -> None:
        self.indent_level -= 1
        prefix = TAB * self.indent_level
        self.raw(f"{prefix}}}\n")

    def get_source(self) -> str:
        return "".join(self._parts)


# ---------------------------------------------------------------------------
# Context – tracks position / stride / iteration state for nested elements
# ---------------------------------------------------------------------------

class Context:
    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        stride_x: int = 0,
        stride_y: int = 0,
        position: Tuple[int, ...] = (0, 0, 0),
        quantity_of_elements: int = 1,
    ):
        self.x = x
        self.y = y
        self.stride_x = stride_x
        self.stride_y = stride_y
        self.position = position
        self.quantity_of_elements = quantity_of_elements
        self.index_of_iteration: str = ""
        self.index_of_element: int = 0
        self.quantity_of_sub_elements: int = 0
        self.p_ui_element: str = ""
        self._saved_indent: int = 0

    @classmethod
    def from_xml(cls, xml_element, parent: "Context") -> "Context":
        return cls(
            x=parent.x
            + parent.stride_x * parent.index_of_element
            + xml_int(xml_element, "x", 0),
            y=parent.y
            + parent.stride_y * parent.index_of_element
            + xml_int(xml_element, "y", 0),
            stride_x=xml_int(xml_element, "stride__x", 0),
            stride_y=xml_int(xml_element, "stride__y", 0),
            position=(
                parent.position
                if "position" not in xml_element.attrib
                else xml_int_tuple(xml_element, "position", parent.position)
            ),
            quantity_of_elements=xml_int(xml_element, "size", 1),
        )


# ---------------------------------------------------------------------------
# RectangleSpec – describes a UI region geometry
# ---------------------------------------------------------------------------

class RectangleSpec:
    def __init__(self, x=0, y=0, width=0, height=0, color=(55, 55, 55)):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

    @classmethod
    def from_xml(cls, xml_element) -> "RectangleSpec":
        return cls(
            x=xml_int(xml_element, "x", 0),
            y=xml_int(xml_element, "y", 0),
            width=xml_int(xml_element, "width", 0),
            height=xml_int(xml_element, "height", 0),
            color=xml_int_tuple(xml_element, "color", (55, 55, 55)),
        )


# ---------------------------------------------------------------------------
# GeneratorState – shared mutable state
# ---------------------------------------------------------------------------

class GeneratorState:
    def __init__(self, config: Config):
        self.config = config
        self.writer = CodeWriter()
        self.header = CodeWriter()
        self.symbol_table: Dict[str, str] = {}
        self.current_element_id: int = 0
        self.context_stack: deque = deque()
        self.signature_map: Dict[str, UISignature] = {}

    @property
    def ctx(self) -> Context:
        return self.context_stack[-1]

    @property
    def parent_ctx(self) -> Context:
        return self.context_stack[-2]

    def push_context(self, ctx: Context) -> None:
        ctx._saved_indent = self.writer.indent_level
        self.context_stack.append(ctx)

    def pop_context(self) -> Context:
        ctx = self.context_stack.pop()
        self.writer.indent_level = ctx._saved_indent
        return ctx

    def advance_element_id(self, count: int = 1) -> None:
        self.current_element_id += count

    def named_ui_index(self, name: str, uid: int) -> str:
        return f"{self.config.source_name.upper()}_{name.upper()}_{uid}"

    def emit_named_index_if_present(self, xml_element) -> None:
        name = xml_str(xml_element, "name", "")
        if name:
            macro = self.named_ui_index(name, self.current_element_id)
            self.symbol_table[name] = macro
            self.header.raw(
                f"#define {macro} {self.current_element_id}\n"
            )

    def get_rect_spec_args(self, rect: RectangleSpec) -> List[str]:
        ctx = self.ctx
        iter_mul = (
            ""
            if not ctx.index_of_iteration
            else f"* {ctx.index_of_iteration}"
        )
        x_expr = f"{rect.x + ctx.x} + {ctx.stride_x}{iter_mul}"
        y_expr = f"{rect.y + ctx.y} + {ctx.stride_y}{iter_mul}"
        return [
            str(rect.width),
            str(rect.height),
            f"get_vector__3i32({x_expr}, {y_expr}, 0)",
        ]

    def get_vector_3i32_arg(
        self, xml_element,
        x_attr, y_attr, z_attr,
        x_off="0", y_off="0", z_off="0",
    ) -> str:
        x = xml_str(xml_element, x_attr, "0")
        y = xml_str(xml_element, y_attr, "0")
        z = xml_str(xml_element, z_attr, "0")
        return (
            f"get_vector__3i32("
            f"{x} + {x_off}, "
            f"{y} + {y_off}, "
            f"{z} + {z_off})"
        )


# ---------------------------------------------------------------------------
# Element handlers
# ---------------------------------------------------------------------------

def _get_c_sig(state: GeneratorState, xml_tag: str) -> str:
    """Resolve the C function name for an XML tag."""
    sig = state.signature_map.get(xml_tag)
    if sig and sig.c_signatures:
        return sig.c_signatures.split(",")[0]
    return ""


def _allocate_hitbox(state, xml_element, name=None, rect=None):
    if rect is None:
        rect = RectangleSpec.from_xml(xml_element)
    if name is None:
        name = state.ctx.p_ui_element
    args = ["p_game", "p_gfx_window", name] + state.get_rect_spec_args(rect)
    state.writer.write_call("allocate_hitbox_for__ui_element", args)
    return rect


def _set_tile_span(state, xml_element):
    w = state.writer
    name = state.ctx.p_ui_element
    span_var = f"ui_tile_span__{name}"
    w.stmt(f"UI_Tile_Span {span_var}")
    w.write_call(
        xml_str(xml_element, "span", "MISSING_FUNCTION_IN_XML"),
        [f"&{span_var}"],
    )
    w.write_call(
        "set_ui_tile_span_of__ui_element",
        [name, f"&{span_var}"],
    )


def _set_texture(state, xml_element, name=None):
    w = state.writer
    if name is None:
        name = state.ctx.p_ui_element
    tex_var = f"texture_for__{name}"
    w.raw(f"{TAB * w.indent_level}Texture {tex_var};")
    w.raw("\n")
    w.write_call(
        "get_texture_by__alias",
        [
            "get_p_aliased_texture_manager_from__game(p_game)",
            xml_str(xml_element, "name_of__texture", "MISSING_TEXTURE_NAME"),
            f"&{tex_var}",
        ],
    )
    return tex_var


def _set_sprite(state, xml_element, name=None, texture_var=None):
    w = state.writer
    if name is None:
        name = state.ctx.p_ui_element
    sprite_var = f"p_sprite_for__{name}"
    size = xml_str(xml_element, "size_of__texture", "8x8")
    w.write_assignment(
        f"Sprite *{sprite_var}",
        w.call_str(
            "allocate_sprite_from__sprite_manager",
            [
                "get_p_gfx_context_from__game(p_game)",
                "get_p_sprite_manager_from__graphics_window(p_game, p_gfx_window)",
                "p_gfx_window",
                f"GET_UUID_P({name})",
                texture_var or "0",
                f"TEXTURE_FLAG__SIZE_{size}",
            ],
        ),
    )
    w.write_call(
        "set_frame_index_of__sprite",
        [sprite_var, xml_str(xml_element, "index_of__sprite_frame", "0")],
    )
    w.write_call("set_ui_element_as__using_sprite", [name])


def _set_text(state, xml_element):
    w = state.writer
    text_arg = xml_str(xml_element, "text", "")
    if not text_arg:
        return
    text_name = f"text_for__{state.ctx.p_ui_element}"
    font_expr = xml_str(
        xml_element, "font_expression", "MISSING_FONT_EXPRESSION_IN_XML"
    )
    w.write_call(
        "initialize_ui_element_as__text_with__const_c_str",
        [text_name, font_expr, text_arg, f"strnlen({text_arg}, 32)"],
    )
    w.write_call(
        "set_ui_element__transformed_handler",
        [state.ctx.p_ui_element,
         xml_str(xml_element, "transform_handler", "0")],
    )
    _allocate_hitbox(state, xml_element, name=text_name)
    w.write_call(
        "set_ui_element_as__the_parent_of__this_ui_element",
        [P_UI_MANAGER, state.ctx.p_ui_element, text_name],
    )


# --- Individual element handlers ---

def handle_group(xml_element, state: GeneratorState) -> None:
    ctx = Context.from_xml(xml_element, state.ctx)
    state.push_context(ctx)
    state.emit_named_index_if_present(xml_element)
    for child in xml_element:
        construct_element(child, state)
        state.writer.blank_line()
    parent = state.parent_ctx
    popped = state.pop_context()
    parent.quantity_of_sub_elements += popped.quantity_of_elements


def handle_grid(xml_element, state: GeneratorState) -> None:
    ctx = Context.from_xml(xml_element, state.ctx)
    state.push_context(ctx)
    state.emit_named_index_if_present(xml_element)
    w = state.writer
    last_index = -1
    for _ in range(ctx.quantity_of_elements):
        for child in xml_element:
            construct_element(child, state)
            w.blank_line()
        if last_index != -1:
            w.write_assignment(
                f"{P_UI_ITERATOR}_previous_previous->p_next",
                w.call_str(
                    "get_p_ui_element_by__index_from__ui_manager",
                    [P_UI_MANAGER, last_index],
                ),
            )
        w.write_assignment(
            f"{P_UI_ITERATOR}_previous_previous",
            f"{P_UI_ITERATOR}_previous",
        )
        last_index = state.current_element_id
    parent = state.parent_ctx
    popped = state.pop_context()
    parent.quantity_of_sub_elements += popped.quantity_of_elements


def handle_allocate_ui(xml_element, state: GeneratorState,
                       name_override=None) -> None:
    sig = _get_c_sig(state, "allocate_ui") or \
          "allocate_ui_element_from__ui_manager"
    ctx = Context.from_xml(xml_element, state.ctx)
    state.push_context(ctx)

    name = name_override or xml_str(xml_element, "name", P_UI_ITERATOR)
    state.emit_named_index_if_present(xml_element)
    w = state.writer

    if name != P_UI_ITERATOR:
        w.write_assignment(
            f"UI_Element *{name}",
            w.call_str(sig, [P_UI_MANAGER]),
        )
    else:
        w.write_assignment(
            P_UI_ITERATOR,
            w.call_str(sig, [P_UI_MANAGER]),
        )
    state.ctx.p_ui_element = name

    for child in xml_element:
        construct_element(child, state)

    qty = state.ctx.quantity_of_elements
    state.pop_context()
    state.advance_element_id(qty)


def handle_allocate_ui_container(xml_element, state: GeneratorState) -> None:
    ctx = Context.from_xml(xml_element, state.ctx)
    state.emit_named_index_if_present(xml_element)
    state.push_context(ctx)
    w = state.writer
    sig = _get_c_sig(state, "allocate_ui_container") or \
          "allocate_many_ui_elements_from__ui_manager_in__succession"
    size = ctx.quantity_of_elements

    w.write_assignment(
        P_UI_ITERATOR,
        w.call_str(sig, [P_UI_MANAGER, size]),
    )

    loop_var = f"index_of__iteration__{len(state.context_stack) - 1}"
    state.ctx.index_of_iteration = loop_var
    w.line(
        f"for (Index__u32 {loop_var}=0;"
        f"{P_UI_ITERATOR};"
        f"iterate_to_next__ui_element(&{P_UI_ITERATOR}),{loop_var}++) {{"
    )
    w.indent_level += 1

    w.write_assignment(
        f"{P_UI_ITERATOR}_previous", P_UI_ITERATOR
    )

    for child in xml_element:
        state.ctx.p_ui_element = P_UI_ITERATOR
        construct_element(child, state)

    state.advance_element_id(size)
    w.indent_level -= 1
    w.line("}")

    parent = state.parent_ctx
    popped = state.pop_context()
    parent.quantity_of_sub_elements += popped.quantity_of_elements


def handle_alloc_child(xml_element, state: GeneratorState) -> None:
    state.ctx.index_of_element -= 1
    w = state.writer
    sig = _get_c_sig(state, "alloc_child") or \
          "allocate_ui_element_from__ui_manager_as__child"
    w.write_assignment(
        f"{P_UI_ITERATOR}_child",
        w.call_str(
            sig,
            ["p_game", "p_gfx_window", P_UI_MANAGER, P_UI_ITERATOR],
        ),
    )
    state.ctx.p_ui_element = f"{P_UI_ITERATOR}_child"
    for child in xml_element:
        construct_element(child, state)
    state.advance_element_id(state.ctx.quantity_of_elements)


def handle_background(xml_element, state: GeneratorState) -> None:
    rect = RectangleSpec.from_xml(xml_element)
    w = state.writer
    sig = _get_c_sig(state, "background") or \
          "SDL_initialize_ui_element_as__background"
    args = [state.ctx.p_ui_element] + state.get_rect_spec_args(rect)
    args.append(xml_str(xml_element, "p_gfx_window", "0"))
    w.write_call(sig, args)


def handle_button(xml_element, state: GeneratorState) -> None:
    w = state.writer
    sig = _get_c_sig(state, "button") or \
          "initialize_ui_element_as__button"
    args = [
        state.ctx.p_ui_element,
        xml_str(xml_element, "m_Clicked_Handler",
                "m_ui_button__clicked_handler__default"),
        xml_str(xml_element, "is_toggleable", "false"),
        xml_str(xml_element, "is_toggled", "false"),
    ]
    w.write_call(sig, args)
    _set_text(state, xml_element)
    _allocate_hitbox(state, xml_element)


def handle_window_element(xml_element, state: GeneratorState) -> None:
    rect = RectangleSpec.from_xml(xml_element)
    w = state.writer
    sig = _get_c_sig(state, "window_element") or \
          "initialize_ui_element_as__window_element_and__open_window"
    ox = xml_int(xml_element, "offset_window__x", 0)
    oy = xml_int(xml_element, "offset_window__y", 0)
    oz = xml_int(xml_element, "offset_window__z", 0)
    args = [
        state.ctx.p_ui_element,
        "p_game",
        xml_str(xml_element, "window_kind",
                "Graphics_Window_Kind__Unknown"),
        "GET_UUID_P(p_gfx_window)",
        f"get_vector__3i32({ox},{oy},{oz})",
    ]
    w.write_call(sig, args)
    _set_text(state, xml_element)
    _allocate_hitbox(state, xml_element)


def handle_slider(xml_element, state: GeneratorState) -> None:
    name = state.ctx.p_ui_element
    rect = _allocate_hitbox(state, xml_element, name)
    _set_tile_span(state, xml_element)
    w = state.writer
    sig = _get_c_sig(state, "slider") or \
          "initialize_ui_element_as__slider"
    args = [
        name,
        state.get_vector_3i32_arg(
            xml_element,
            "spanning_width", "spanning_height", "spanning_depth",
            "0", "0", "0",
        ),
        xml_str(xml_element, "m_Dragged_Handler",
                "m_ui_slider__dragged_handler__default"),
        xml_str(xml_element, "snapped_x_or__y", "true"),
    ]
    w.write_call(sig, args)

    # slider button sub-element
    btn_name = f"{name}__slider_button"
    handle_allocate_ui(xml_element, state, name_override=btn_name)
    tex_var = _set_texture(state, xml_element, btn_name)
    _set_sprite(state, xml_element, btn_name, tex_var)

    size_str = xml_str(xml_element, "size_of__texture", "8x8")
    dims = size_str.split("x")
    btn_rect = RectangleSpec.from_xml(xml_element)
    btn_rect.width = int(dims[0])
    btn_rect.height = int(dims[1])
    _allocate_hitbox(state, xml_element, btn_name, btn_rect)
    w.write_call(
        "set_ui_element_as__the_parent_of__this_ui_element",
        [P_UI_MANAGER, name, btn_name],
    )


def handle_draggable(xml_element, state: GeneratorState) -> None:
    name = state.ctx.p_ui_element
    _allocate_hitbox(state, xml_element, name)
    sig = _get_c_sig(state, "draggable") or \
          "initialize_ui_element_as__draggable"
    state.writer.write_call(
        sig,
        [
            name,
            xml_str(xml_element, "m_Dragged_Handler",
                    "m_ui_draggable__dragged_handler__default"),
        ],
    )


def handle_drop_zone(xml_element, state: GeneratorState) -> None:
    name = state.ctx.p_ui_element
    _allocate_hitbox(state, xml_element, name)
    sig = _get_c_sig(state, "drop_zone") or \
          "initialize_ui_element_as__drop_zone"
    state.writer.write_call(
        sig,
        [
            name,
            xml_str(xml_element, "m_Receive_Drop_Handler",
                    "m_ui_drop_zone__receive_drop_handler__default"),
        ],
    )


def handle_code(xml_element, state: GeneratorState) -> None:
    w = state.writer
    raw_text = xml_element.text or ""
    statements = list(filter(None, re.split(r"\n *", raw_text)))
    if not statements:
        return
    w.line(statements[0].format(state.ctx.p_ui_element))
    for stmt_text in statements[1:]:
        if "$" in stmt_text:
            tokens = [
                t.strip()
                for t in re.findall(r"[^();]+|[();]", stmt_text)
                if t.strip()
            ]
            for i, tok in enumerate(tokens):
                if "$" in tok:
                    sym = tok.lstrip("$")
                    resolved = state.symbol_table.get(sym)
                    if resolved is not None:
                        tokens[i] = (
                            f"({resolved}"
                            f" + index_of__ui_element_offset__u16)"
                        )
                    else:
                        tokens[i] = "SYMBOL_NOT_FOUND"
            stmt_text = " ".join(tokens)
        w.line(stmt_text.format(state.ctx.p_ui_element))


# ---------------------------------------------------------------------------
# Element dispatcher
# ---------------------------------------------------------------------------

# Maps XML tag names to handler functions.
# NOTE: "allocate_ui" is the correct tag used in XML files, despite
# AllocateUIElement using "alloc_ui" in gen_ui_elements/containers.py.
_HANDLER_MAP = {
    "group": handle_group,
    "grid": handle_grid,
    "allocate_ui": handle_allocate_ui,
    "allocate_ui_container": handle_allocate_ui_container,
    "alloc_child": handle_alloc_child,
    "background": handle_background,
    "button": handle_button,
    "window_element": handle_window_element,
    "slider": handle_slider,
    "draggable": handle_draggable,
    "drop_zone": handle_drop_zone,
    "code": handle_code,
}


def construct_element(xml_element, state: GeneratorState) -> None:
    tag = xml_element.tag
    handler = _HANDLER_MAP.get(tag)
    if handler is None:
        # Check if it's registered in signatures (for custom tags)
        if tag in state.signature_map:
            print(f"warning: no built-in handler for tag '{tag}'")
        else:
            print(f"unknown element: {tag}")
        return
    handler(xml_element, state)
    state.ctx.index_of_element += 1


# ---------------------------------------------------------------------------
# Source generation
# ---------------------------------------------------------------------------

def generate_source(xml_node_ui, state: GeneratorState) -> None:
    cfg = state.config
    w = state.writer
    h = state.header

    print(f"GEN: {cfg.associated_header_sub_dir_in__include_folder}"
          f"\\{cfg.source_name}")

    # -- includes --
    cfg.includes.insert(
        0,
        Include(
            f"{cfg.associated_header_sub_dir_in__include_folder}"
            f"{cfg.source_name}.h"
        ),
    )
    for inc in cfg.includes:
        w.write_include(inc.path)

    # -- header preamble --
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

    # -- source preamble --
    w.raw(
        "// THIS CODE IS AUTO GENERATED. "
        "Go to ./core/assets/ui/xml/ instead of modifying this file.\n"
    )
    w.raw(f"\nbool {func_name}({param_list})")
    w.open_brace()

    # -- local variables --
    w.write_local_decl("UI_Element *", P_UI_ITERATOR)
    w.write_local_decl("UI_Element *", f"{P_UI_ITERATOR}_previous_previous")
    w.write_local_decl("UI_Element *", f"{P_UI_ITERATOR}_previous")
    w.write_local_decl("UI_Element *", f"{P_UI_ITERATOR}_child")

    # -- root context --
    root_ctx = Context()
    root_ctx.p_ui_element = ""
    state.push_context(root_ctx)

    state.current_element_id = xml_int(
        xml_node_ui, "offset_of__ui_index", 0
    )

    # -- optional tile-map setup --
    tile_map_size = xml_str(
        xml_node_ui, "ui_tile_map__size", "UI_Tile_Map_Size__None"
    )
    has_tile_map = tile_map_size != "UI_Tile_Map_Size__None"

    if has_tile_map:
        w.write_assignment(
            "p_gfx_window->ui_tile_map__wrapper",
            w.call_str(
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
                w.call_str(
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

    # -- child elements --
    for child in xml_node_ui:
        construct_element(child, state)

    # -- epilogue --
    w.line("return true", semicolon=True)
    w.close_brace()
    h.raw("#endif\n")


# ---------------------------------------------------------------------------
# Output writer
# ---------------------------------------------------------------------------

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
        print(f"  [wrote] {full}")


# ---------------------------------------------------------------------------
# UI Window Registrar updater
# ---------------------------------------------------------------------------

_REGISTRAR_REL_PATH = "source/ui/implemented/ui_window_registrar.c"
_REGISTRAR_HEADER_PATH = "include/ui/implemented/ui_window_registrar.h"


def _update_ui_window_registrar(config: Config) -> None:
    """Add an include and register_ui_window_into__ui_context call.

    Idempotent: if the entry already exists, does nothing.
    """
    registrar_path = os.path.join(config.base_dir, _REGISTRAR_REL_PATH)
    if not os.path.exists(registrar_path):
        print(f"  [skip registrar] {registrar_path} not found")
        return

    # Derive the include path and function name from config
    sub_dir = config.associated_header_sub_dir_in__include_folder
    source_name = config.source_name
    include_path = f"{sub_dir}{source_name}.h"
    func_name = f"allocate_ui_for__{source_name}"

    text = open(registrar_path, "r").read()

    # Check if already registered
    if func_name in text:
        print(f"  [registrar] already contains {func_name}, skipping")
        return

    lines = text.split("\n")

    # --- Add include ---
    # Find the last #include line and insert after it
    last_include_idx = -1
    for i, line in enumerate(lines):
        if line.startswith("#include"):
            last_include_idx = i

    include_line = f'#include "{include_path}"'
    if include_line not in text:
        lines.insert(last_include_idx + 1, include_line)
        # Re-find the closing brace since we shifted lines
        text = "\n".join(lines)
        lines = text.split("\n")

    # --- Add registration call ---
    # Find the closing brace of register_ui_windows()
    closing_brace_idx = -1
    for i, line in enumerate(lines):
        if line.strip() == "}":
            closing_brace_idx = i

    if closing_brace_idx == -1:
        print(f"  [registrar] could not find closing brace in {registrar_path}")
        return

    # Build the registration call matching AncientsGame style
    # We need a UI_Window_Kind. Derive from the source_name.
    # e.g. "ui_window__game__test" -> "UI_Window_Kind__Game__Test"
    window_kind = _derive_window_kind(source_name)

    reg_call = (
        f"    register_ui_window_into__ui_context(\n"
        f"            p_ui_context, \n"
        f"            {func_name}, \n"
        f"            f_ui_window__close__default, \n"
        f"            {window_kind},\n"
        f"            0, 16); // TODO: magic num sprite quant"
    )

    lines.insert(closing_brace_idx, reg_call)

    with open(registrar_path, "w") as fh:
        fh.write("\n".join(lines))

    print(f"  [registrar] added {func_name} to {registrar_path}")


def _derive_window_kind(source_name: str) -> str:
    """Derive UI_Window_Kind__ enum from a source name.

    e.g. 'ui_window__game__test' -> 'UI_Window_Kind__Game__Test'
    """
    # Strip the "ui_window__" prefix
    suffix = source_name
    if suffix.startswith("ui_window__"):
        suffix = suffix[len("ui_window__"):]

    # Split on __ and capitalize each part
    parts = suffix.split("__")
    capitalized = "__".join(p.capitalize() for p in parts)
    return f"UI_Window_Kind__{capitalized}"


# ---------------------------------------------------------------------------
# Read & generate
# ---------------------------------------------------------------------------

def read_ui(path: str, config: Config) -> Optional[GeneratorState]:
    try:
        tree = ET.parse(path)
        root = tree.getroot()
    except ET.ParseError as exc:
        print(f"Error reading xml: {exc}")
        return None

    xml_config = root.find("config")
    xml_ui = root.find("ui")
    if xml_config is None:
        print("xml is missing config node.")
        return None
    if xml_ui is None:
        print("xml is missing ui node.")
        return None

    config.update_from_xml(xml_config)

    state = GeneratorState(config)
    # Build signature map for C function resolution
    for sig in config.signatures:
        state.signature_map[sig.xml_tag] = sig

    try:
        generate_source(xml_ui, state)
    except KeyError as exc:
        print(f"Missing field: {exc}")
        return None

    if config.is_outputting:
        _write_output(config, state)
        _update_ui_window_registrar(config)

    return state


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage:\n"
            "  gen_ui_code.py <source.xml> [config_field value ...]\n"
        )
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
