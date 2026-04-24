"""Core classes shared by all UI element generators."""

from __future__ import annotations

import os
import re
import string
from collections import deque
from dataclasses import dataclass, field
from typing import (
    Any,
    Deque,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
)


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
    """A single ``#include`` directive."""

    def __init__(self, path: str):
        self.path = path


class Background:
    """A background image layer used by the viewer."""

    def __init__(self, path: str, layer: int, x: int = 0, y: int = 0):
        self.path = path
        self.layer = layer
        self.x = x
        self.y = y
        self.image = None  # populated by the viewer only
        self.modification_time = (
            os.path.getmtime(path) if path and os.path.exists(path) else 0
        )


class UISignature:
    """Maps an XML tag name to a C function signature and a handler class."""

    def __init__(self, xml_tag: str, c_signatures: str, handler_cls: type):
        self.xml_tag = xml_tag
        self.c_signatures: List[str] = c_signatures.split(",")
        self.handler_cls = handler_cls


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
        self.backgrounds: List[Background] = [
            Background("", i) for i in range(4)
        ]
        self.includes: List[Include] = []
        self.base_dir: str = "./"
        self.is_outputting: bool = True

    # ------------------------------------------------------------------
    def update_from_xml(self, xml_node, *, resize_callback=None) -> None:
        """Populate *self* from a ``<config>`` XML element."""
        self.includes = []
        for elem in xml_node:
            tag = elem.tag

            if tag == "ui_func_signature":
                # Signature registration is handled externally so that the
                # element registry can be consulted.  We store raw data here.
                self.signatures.append(
                    _RawSignatureSpec(
                        xml_str(elem, "for", ""),
                        xml_str(elem, "c_signatures", ""),
                    )
                )

            elif tag == "platform":
                self.BACKEND = xml_str(elem, "target", self.BACKEND)
                self.window_size = xml_int_tuple(
                    elem, "size", self.window_size
                )
                if resize_callback:
                    resize_callback(self.window_size)

            elif tag == "output":
                self.base_dir = xml_str(elem, "base_dir", self.base_dir)
                self.output__c_path = xml_str(
                    elem, "c_path", self.output__c_path
                )
                self.output__h_path = xml_str(
                    elem, "h_path", self.output__h_path
                )

            elif tag == "background":
                layer = next(
                    (
                        i
                        for i, b in enumerate(self.backgrounds)
                        if b.image is None and b.path == ""
                    ),
                    0,
                )
                layer = xml_int(elem, "layer", layer)
                self.backgrounds[layer] = Background(
                    xml_str(elem, "path", ""),
                    layer,
                    xml_int(elem, "x", 0),
                    xml_int(elem, "y", 0),
                )

            elif tag == "include":
                self.associated_header_sub_dir_in__include_folder = xml_str(
                    elem, "sub_dir", ""
                )
                for header in elem:
                    self.includes.append(
                        Include(xml_str(header, "path", ""))
                    )


class _RawSignatureSpec:
    """Temporary holder until the element registry resolves the handler."""

    def __init__(self, xml_tag: str, c_signatures: str):
        self.xml_tag = xml_tag
        self.c_signatures = c_signatures


# ---------------------------------------------------------------------------
# CodeWriter – accumulates C source with correct indentation
# ---------------------------------------------------------------------------

class CodeWriter:
    """Builds a C source string while tracking indentation."""

    TAB = "    "

    def __init__(self):
        self._parts: List[str] = []
        self.indent_level: int = 0

    # -- low-level ---------------------------------------------------------

    def raw(self, text: str) -> None:
        """Append *text* verbatim (no indentation added)."""
        self._parts.append(text)

    def line(self, text: str = "", *, semicolon: bool = False) -> None:
        """Write an indented line.  Adds ``\\n`` automatically."""
        prefix = self.TAB * self.indent_level
        suffix = ";\n" if semicolon else "\n"
        self._parts.append(f"{prefix}{text}{suffix}")

    def blank_line(self) -> None:
        self._parts.append("\n")

    def stmt(self, text: str) -> None:
        """Indented statement terminated with ``;\\n``."""
        self.line(text, semicolon=True)

    # -- helpers -----------------------------------------------------------

    def call(self, func: str, args: Sequence[Any]) -> str:
        """Return ``func(arg1, arg2, ...)`` as a string (no newline)."""
        joined = ", ".join(str(a) for a in args)
        return f"{func}({joined})"

    def write_call(self, func: str, args: Sequence[Any]) -> None:
        """Write an indented ``func(args);\\n``."""
        self.stmt(self.call(func, args))

    def write_assignment(self, lhs: str, rhs: str) -> None:
        self.stmt(f"{lhs} = {rhs}")

    def write_local_decl(self, c_type: str, name: str, init: str = "0") -> None:
        self.stmt(f"{c_type} {name} = {init}")

    def write_include(self, path: str) -> None:
        self.raw(f"#include <{path}>\n")

    def open_brace(self, header: str = "") -> None:
        if header:
            self.line(f"{header} {{")
        else:
            self.line("{")
        self.indent_level += 1

    def close_brace(self) -> None:
        self.indent_level -= 1
        self.line("}")

    def indent(self) -> None:
        self.indent_level += 1

    def dedent(self) -> None:
        self.indent_level -= 1

    # -- result ------------------------------------------------------------

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

    @classmethod
    def from_xml(cls, xml_element, parent: "Context") -> "Context":
        ctx = cls(
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
        return ctx


# ---------------------------------------------------------------------------
# RectangleSpec – describes a visual rectangle for the viewer
# ---------------------------------------------------------------------------

class RectangleSpec:
    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 0,
        height: int = 0,
        color: Tuple[int, ...] = (55, 55, 55),
    ):
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

    @classmethod
    def at_parent_position(
        cls,
        xml_element,
        width: int,
        height: int,
        color: Optional[Tuple[int, ...]] = None,
    ) -> "RectangleSpec":
        spec = cls.from_xml(xml_element)
        spec.width = width
        spec.height = height
        if color is not None:
            spec.color = color
        return spec


# ---------------------------------------------------------------------------
# GeneratorState – mutable state shared across all element generators
# ---------------------------------------------------------------------------

P_UI_MANAGER = "p_ui_manager"
P_UI_ITERATOR = "p_ui_iterator"


class GeneratorState:
    """Shared mutable state threaded through every element generator."""

    def __init__(self, config: Config):
        self.config = config
        self.writer = CodeWriter()
        self.header = CodeWriter()
        self.symbol_table: Dict[str, str] = {}
        self.current_element_id: int = 0
        self.context_stack: Deque[Context] = deque()
        self.squares: list = []  # list of (x, y, w, h, color) for viewer
        self.element_registry: Dict[str, "UIElement"] = {}

    # -- convenience accessors ---------------------------------------------

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

    # -- element id helpers ------------------------------------------------

    def element_id_expr(self) -> str:
        return f"({self.current_element_id} + index_of__ui_element_offset__u16)"

    def advance_element_id(self, count: int = 1) -> None:
        self.current_element_id += count

    # -- header helpers ----------------------------------------------------

    def named_ui_index(self, name: str, uid: int) -> str:
        return f"{self.config.source_name.upper()}_{name.upper()}_{uid}"

    def emit_named_index_if_present(self, xml_element) -> None:
        name = xml_str(xml_element, "name", "")
        if name:
            macro = self.named_ui_index(name, self.current_element_id)
            self.symbol_table[name] = macro
            self.header.line(
                f"#define {macro} {self.current_element_id}"
            )

    # -- rect spec helpers -------------------------------------------------

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
        self,
        xml_element,
        x_attr: str,
        y_attr: str,
        z_attr: str,
        x_off: str = "0",
        y_off: str = "0",
        z_off: str = "0",
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

    # -- viewer square helpers ---------------------------------------------

    def add_square(self, x, y, w, h, color):
        self.squares.append((x, y, w, h, color))

    def add_squares_from_context(self, rect: RectangleSpec) -> None:
        ctx = self.ctx
        for i in range(ctx.quantity_of_elements):
            self.add_square(
                rect.x + ctx.x + i * ctx.stride_x - rect.width / 2,
                rect.y + ctx.y + i * ctx.stride_y - rect.height / 2,
                rect.width,
                rect.height,
                rect.color,
            )

    # -- dispatch ----------------------------------------------------------

    def construct_element(self, xml_element) -> None:
        tag = xml_element.tag
        handler = self.element_registry.get(tag)
        if handler is None:
            print(f"unknown element: {tag}")
            return
        handler.generate(xml_element, self)
        self.ctx.index_of_element += 1


# ---------------------------------------------------------------------------
# UIElement – abstract base for every element handler
# ---------------------------------------------------------------------------

class UIElement:
    """Base class for all UI element code generators."""

    xml_tag: str = ""
    c_signature: str = ""

    def generate(self, xml_element, state: GeneratorState) -> None:
        raise NotImplementedError

    # -- shared helpers available to subclasses ----------------------------

    @staticmethod
    def _name_of_ui_element(state: GeneratorState) -> str:
        return state.ctx.p_ui_element

    def _allocate_hitbox(
        self,
        xml_element,
        state: GeneratorState,
        name: Optional[str] = None,
        rect: Optional[RectangleSpec] = None,
    ) -> RectangleSpec:
        if rect is None:
            rect = RectangleSpec.from_xml(xml_element)
        if name is None:
            name = self._name_of_ui_element(state)
        args = ["p_game", "p_gfx_window", name] + state.get_rect_spec_args(rect)
        state.writer.write_call("allocate_hitbox_for__ui_element", args)
        return rect

    def _set_tile_span(self, xml_element, state: GeneratorState) -> None:
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

    def _set_transform_handler(self, xml_element, state: GeneratorState) -> None:
        style = xml_str(xml_element, "transform_handler", "0")
        state.writer.write_call(
            "set_ui_element__transformed_handler",
            [self._name_of_ui_element(state), style],
        )

    def _set_texture(
        self,
        xml_element,
        state: GeneratorState,
        name: Optional[str] = None,
    ) -> str:
        w = state.writer
        if name is None:
            name = self._name_of_ui_element(state)
        tex_var = f"texture_for__{name}"
        w.stmt(f"Texture {tex_var}")
        w.write_call(
            "get_texture_by__alias",
            [
                "get_p_aliased_texture_manager_from__game(p_game)",
                xml_str(xml_element, "name_of__texture", "MISSING_TEXTURE_NAME"),
                f"&{tex_var}",
            ],
        )
        return tex_var

    def _set_sprite(
        self,
        xml_element,
        state: GeneratorState,
        name: Optional[str] = None,
        texture_var: Optional[str] = None,
    ) -> None:
        w = state.writer
        if name is None:
            name = self._name_of_ui_element(state)
        sprite_var = f"p_sprite_for__{name}"
        size = xml_str(xml_element, "size_of__texture", "8x8")
        w.write_assignment(
            f"Sprite *{sprite_var}",
            w.call(
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

    def _set_text(self, xml_element, state: GeneratorState) -> None:
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
        self._set_transform_handler(xml_element, state)
        self._allocate_hitbox(xml_element, state, name=text_name)
        w.write_call(
            "set_ui_element_as__the_parent_of__this_ui_element",
            [P_UI_MANAGER, self._name_of_ui_element(state), text_name],
        )
