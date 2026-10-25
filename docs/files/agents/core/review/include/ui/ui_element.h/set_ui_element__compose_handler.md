set_ui_element__compose_handler — core/include/ui/ui_element.h

Sets the compose handler on a UI_Element and marks it as using a UI tile span.

Pre-conditions:
1. p_ui_element must be a non-null pointer to a writable UI_Element object.
2. m_ui_compose_handler may be NULL or a valid function pointer of type m_UI_Compose (void (*)(UI_Element *, Game *, Graphics_Window *)).

Post-conditions:
1. p_ui_element is mutated: the UI_FLAGS__BIT_IS_USING__SPRITE_OR_UI_TILE_SPAN flag is cleared, marking the element as using a UI tile span (not a sprite).
2. p_ui_element->m_ui_compose_handler is assigned the value of m_ui_compose_handler.

Correctness Verdict: Correct

Semantic Alignment:
The function fulfills its semantic intent: it configures a UI_Element to use a UI tile span by clearing the sprite/tile-span flag bit, then assigns the provided compose handler. This is consistent with does_ui_element_have__compose_handler, which checks both is_ui_element__using_ui_tile_span and a non-null compose handler. The two operations are correctly ordered — the flag is set before the handler is assigned, ensuring the element's state is consistent.

Implementation Correctness:
Type compatibility — the parameter type m_UI_Compose matches the field type m_ui_compose_handler exactly. No implicit conversions or truncation.
No undefined behavior — no pointer arithmetic, no null dereference (consistent with sibling functions set_ui_element__dispose_handler, set_ui_element__clicked_handler, etc., which also do not null-check), no type punning, no out-of-bounds access.
No validation is needed — this is a low-level inline setter. The caller is responsible for ensuring p_ui_element is valid, consistent with the pattern used by all other set_ui_element__*_handler functions in this file.

Side Effects:
Mutates p_ui_element: clears the UI_FLAGS__BIT_IS_USING__SPRITE_OR_UI_TILE_SPAN bit in ui_flags and assigns m_ui_compose_handler.