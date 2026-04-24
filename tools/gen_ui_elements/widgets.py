"""Leaf / widget UI element generators."""

from __future__ import annotations

import re
from typing import Optional

from tools.gen_ui_elements.base import (
    UIElement,
    Context,
    GeneratorState,
    RectangleSpec,
    P_UI_ITERATOR,
    P_UI_MANAGER,
    xml_int,
    xml_str,
)


class BackgroundElement(UIElement):
    xml_tag = "background"

    def generate(self, xml_element, state: GeneratorState) -> None:
        rect = RectangleSpec.from_xml(xml_element)
        w = state.writer
        args = [state.ctx.p_ui_element] + state.get_rect_spec_args(rect)
        args.append(xml_str(xml_element, "p_gfx_window", "0"))
        w.write_call(self.c_signature, args)


class ButtonElement(UIElement):
    xml_tag = "button"

    def generate(self, xml_element, state: GeneratorState) -> None:
        rect = RectangleSpec.from_xml(xml_element)
        w = state.writer
        args = [
            state.ctx.p_ui_element,
            xml_str(xml_element, "m_Clicked_Handler",
                    "m_ui_button__clicked_handler__default"),
            xml_str(xml_element, "is_toggleable", "false"),
            xml_str(xml_element, "is_toggled", "false"),
        ]
        w.write_call(self.c_signature, args)
        self._set_text(xml_element, state)
        self._allocate_hitbox(xml_element, state)
        state.add_squares_from_context(rect)


class WindowElementElement(UIElement):
    xml_tag = "window_element"

    def generate(self, xml_element, state: GeneratorState) -> None:
        rect = RectangleSpec.from_xml(xml_element)
        w = state.writer
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
        layer = xml_int(xml_element, "layer", -1)
        if layer >= 0:
            state.config.backgrounds[layer].x = rect.x - ox
            state.config.backgrounds[layer].y = oy - rect.y
        w.write_call(self.c_signature, args)
        self._set_text(xml_element, state)
        self._allocate_hitbox(xml_element, state)
        state.add_squares_from_context(rect)


class SliderElement(UIElement):
    xml_tag = "slider"

    def generate(self, xml_element, state: GeneratorState) -> None:
        from tools.gen_ui_elements.containers import AllocateUIElement

        name = self._name_of_ui_element(state)
        rect = self._allocate_hitbox(xml_element, state, name)
        self._set_tile_span(xml_element, state)
        w = state.writer

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
        w.write_call(self.c_signature, args)
        state.add_squares_from_context(rect)

        # slider button sub-element
        btn_name = f"{name}__slider_button"
        alloc = AllocateUIElement()
        alloc.c_signature = ""
        alloc.generate(xml_element, state, name_override=btn_name)
        tex_var = self._set_texture(xml_element, state, btn_name)
        self._set_sprite(xml_element, state, btn_name, tex_var)

        size_str = xml_str(xml_element, "size_of__texture", "8x8")
        dims = size_str.split("x")
        btn_rect = RectangleSpec.at_parent_position(
            xml_element, int(dims[0]), int(dims[1])
        )
        self._allocate_hitbox(xml_element, state, btn_name, btn_rect)
        w.write_call(
            "set_ui_element_as__the_parent_of__this_ui_element",
            [P_UI_MANAGER, name, btn_name],
        )
        state.add_squares_from_context(btn_rect)


class DraggableElement(UIElement):
    xml_tag = "draggable"

    def generate(self, xml_element, state: GeneratorState) -> None:
        name = self._name_of_ui_element(state)
        rect = RectangleSpec.from_xml(xml_element)
        self._allocate_hitbox(xml_element, state, name)
        state.writer.write_call(
            self.c_signature,
            [
                name,
                xml_str(xml_element, "m_Dragged_Handler",
                        "m_ui_draggable__dragged_handler__default"),
            ],
        )
        state.add_squares_from_context(rect)


class DropZoneElement(UIElement):
    xml_tag = "drop_zone"

    def generate(self, xml_element, state: GeneratorState) -> None:
        name = self._name_of_ui_element(state)
        rect = RectangleSpec.from_xml(xml_element)
        self._allocate_hitbox(xml_element, state, name)
        state.writer.write_call(
            self.c_signature,
            [
                name,
                xml_str(xml_element, "m_Receive_Drop_Handler",
                        "m_ui_drop_zone__receive_drop_handler__default"),
            ],
        )
        state.add_squares_from_context(rect)


class CodeElement(UIElement):
    xml_tag = "code"

    def generate(self, xml_element, state: GeneratorState) -> None:
        w = state.writer
        statements = list(filter(None, re.split(r"\n *", xml_element.text or "")))
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
