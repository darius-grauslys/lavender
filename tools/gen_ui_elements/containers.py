"""Container-style UI element generators (group, grid, alloc_ui, etc.)."""

from __future__ import annotations

from typing import Optional

from tools.gen_ui_elements.base import (
    UIElement,
    Context,
    GeneratorState,
    P_UI_ITERATOR,
    P_UI_MANAGER,
    xml_int,
    xml_str,
)


class GroupElement(UIElement):
    """``<group>`` – logical grouping, no allocation."""

    xml_tag = "group"

    def generate(self, xml_element, state: GeneratorState) -> None:
        ctx = Context.from_xml(xml_element, state.ctx)
        state.push_context(ctx)
        state.emit_named_index_if_present(xml_element)
        for child in xml_element:
            state.construct_element(child)
            state.writer.blank_line()
        parent = state.parent_ctx
        popped = state.pop_context()
        parent.quantity_of_sub_elements += popped.quantity_of_elements


class GridElement(UIElement):
    """``<grid>`` – repeated group with linked-list stitching."""

    xml_tag = "grid"

    def generate(self, xml_element, state: GeneratorState) -> None:
        ctx = Context.from_xml(xml_element, state.ctx)
        state.push_context(ctx)
        state.emit_named_index_if_present(xml_element)
        w = state.writer
        last_index = -1
        for _ in range(ctx.quantity_of_elements):
            for child in xml_element:
                state.construct_element(child)
                w.blank_line()
            if last_index != -1:
                w.write_assignment(
                    f"{P_UI_ITERATOR}_previous_previous->p_next",
                    w.call(
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


class AllocateUIElement(UIElement):
    """``<alloc_ui>`` – allocate a single UI element from the manager."""

    xml_tag = "alloc_ui"

    def generate(
        self,
        xml_element,
        state: GeneratorState,
        name_override: Optional[str] = None,
    ) -> None:
        sig = self.c_signature or "allocate_ui_element_from__ui_manager"
        ctx = Context.from_xml(xml_element, state.ctx)
        state.push_context(ctx)

        name = name_override or xml_str(xml_element, "name", P_UI_ITERATOR)
        state.emit_named_index_if_present(xml_element)
        w = state.writer

        if name != P_UI_ITERATOR:
            w.write_assignment(
                f"UI_Element *{name}",
                w.call(sig, [P_UI_MANAGER]),
            )
        else:
            w.write_assignment(
                P_UI_ITERATOR,
                w.call(sig, [P_UI_MANAGER]),
            )
        state.ctx.p_ui_element = name

        for child in xml_element:
            state.construct_element(child)

        qty = state.ctx.quantity_of_elements
        state.pop_context()
        state.advance_element_id(qty)


class AllocateUIContainerElement(UIElement):
    """``<allocate_ui_container>`` – allocate N elements and iterate."""

    xml_tag = "allocate_ui_container"

    def generate(self, xml_element, state: GeneratorState) -> None:
        ctx = Context.from_xml(xml_element, state.ctx)
        state.emit_named_index_if_present(xml_element)
        state.push_context(ctx)
        w = state.writer
        size = ctx.quantity_of_elements

        w.write_assignment(
            P_UI_ITERATOR,
            w.call(self.c_signature, [P_UI_MANAGER, size]),
        )

        loop_var = f"index_of__iteration__{len(state.context_stack) - 1}"
        state.ctx.index_of_iteration = loop_var
        w.line(
            f"for (Index__u32 {loop_var}=0;"
            f"{P_UI_ITERATOR};"
            f"iterate_to_next__ui_element(&{P_UI_ITERATOR}),{loop_var}++)"
        )
        w.open_brace()

        w.write_assignment(
            f"{P_UI_ITERATOR}_previous", P_UI_ITERATOR
        )

        for child in xml_element:
            state.ctx.p_ui_element = P_UI_ITERATOR
            state.construct_element(child)

        state.advance_element_id(size)
        w.close_brace()

        parent = state.parent_ctx
        popped = state.pop_context()
        parent.quantity_of_sub_elements += popped.quantity_of_elements


class AllocChildElement(UIElement):
    """``<alloc_child>`` – allocate a child element under the current one."""

    xml_tag = "alloc_child"

    def generate(self, xml_element, state: GeneratorState) -> None:
        state.ctx.index_of_element -= 1
        w = state.writer
        w.write_assignment(
            f"{P_UI_ITERATOR}_child",
            w.call(
                self.c_signature,
                ["p_game", "p_gfx_window", P_UI_MANAGER, P_UI_ITERATOR],
            ),
        )
        state.ctx.p_ui_element = f"{P_UI_ITERATOR}_child"
        for child in xml_element:
            state.construct_element(child)
        state.advance_element_id(state.ctx.quantity_of_elements)
