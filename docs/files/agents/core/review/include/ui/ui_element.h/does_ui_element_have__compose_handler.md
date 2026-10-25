does_ui_element_have__compose_handler — core/include/ui/ui_element.h

Checks whether a UI element has a compose handler set, by verifying the element is using a UI tile span (not a sprite) and that the compose handler function pointer is non-null.

Pre-conditions:
1. p_ui_element must be a non-null pointer to a valid UI_Element object.

Post-conditions:
1. Returns true if p_ui_element is using a UI tile span AND the m_ui_compose_handler field is non-null.
2. Returns false otherwise (including if the element is using a sprite, or if the handler is null).
3. No state is mutated; the function is read-only.

Correctness Verdict: Incorrect

Semantic Alignment:
The function's intent is to check whether a UI element has a compose handler. The logic correctly combines two checks: (1) whether the element is using a UI tile span (via is_ui_element__using_ui_tile_span), and (2) whether the m_ui_compose_handler field is non-null (via get_ui_element__compose_handler). The semantic intent is fulfilled by the combination of these two checks.

However, the function does NOT check for a null p_ui_element pointer before dereferencing it. This is inconsistent with every other does_ui_element_have__* sibling function in the same file, all of which begin with `p_ui_element &&` before accessing the struct:

- does_ui_element_have__dispose_handler:       `return p_ui_element && p_ui_element->m_ui_dispose_handler;`
- does_ui_element_have__clicked_handler:       `return p_ui_element && p_ui_element->m_ui_clicked_handler;`
- does_ui_element_have__dragged_handler:       `return p_ui_element && p_ui_element->m_ui_dragged_handler;`
- does_ui_element_have__dropped_handler:       `return p_ui_element && p_ui_element->m_ui_dropped_handler;`
- does_ui_element_have__receive_drop_handler:  `return p_ui_element && p_ui_element->m_ui_receive_drop_handler;`
- does_ui_element_have__held_handler:          `return p_ui_element && p_ui_element->m_ui_held_handler;`
- does_ui_element_have__typed_handler:         `return p_ui_element && p_ui_element->m_ui_typed_handler;`
- does_ui_element_have__transformed_handler:   `return p_ui_element && p_ui_element->m_ui_transformed_handler;`

Every sibling guards against null p_ui_element. This function does not.

Implementation Correctness:
Type compatibility — m_UI_Compose is a function pointer type (typedef void (*m_UI_Compose)(...)). When used in a boolean context within the && expression, a non-null pointer evaluates to true and a null pointer evaluates to false. This is correct.

Undefined behavior — If p_ui_element is NULL, the function dereferences it through is_ui_element__using_ui_tile_span → is_ui_element__using_sprite_or__ui_tile_span, which directly accesses p_ui_element->ui_flags without a null guard. This is a null pointer dereference, which is undefined behavior. The same issue exists in get_ui_element__compose_handler, which directly accesses p_ui_element->m_ui_compose_handler.

The fix should add a null check for p_ui_element as the first operand:
    return p_ui_element
        && is_ui_element__using_ui_tile_span(p_ui_element)
        && get_ui_element__compose_handler(p_ui_element);

Validation — The null check is appropriate for this function's role as a "does it have" query, consistent with all sibling functions. The absence of this check is a bug.

Side Effects:
No side effects — the function only reads struct fields and returns a boolean. No state is mutated.
