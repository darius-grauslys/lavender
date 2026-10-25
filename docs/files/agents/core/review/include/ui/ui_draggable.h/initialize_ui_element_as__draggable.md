initialize_ui_element_as__draggable — core/source/ui/ui_draggable.c, lines 11-27

Resets a UI_Element to its initial conditions and configures it as a Draggable element by setting its kind, dragged handler, and dropped handler.

Pre-conditions:
1. p_ui_draggable must be a non-null pointer to a valid, previously-initialized UI_Element (the function reads p_parent, p_child, p_next, and ui_flags from the struct before zeroing it).
2. m_ui_dragged_handler is a function pointer of type m_UI_Dragged; it may be NULL (no null-check is performed, but downstream code checks for NULL before invoking it).

Post-conditions:
1. p_ui_draggable is zeroed (except Serialization_Header) via initialize_ui_element, which also sets p_parent, p_child, p_next, the_kind_of_ui_element__this_is, ui_flags, and default dispose/compose/transformed handlers.
2. p_ui_draggable->the_kind_of_ui_element__this_is is set to UI_Element_Kind__Draggable.
3. p_ui_draggable->m_ui_dragged_handler is set to the provided m_ui_dragged_handler.
4. p_ui_draggable->m_ui_dropped_handler is set to m_ui_draggable__dropped_handler__default.
5. All other handler fields (clicked, receive_drop, held, typed) are zeroed (NULL) by the memset in initialize_ui_element.
6. The kind-specific union data and ui_tile_span are zeroed.
7. p_parent, p_child, p_next, and ui_flags are preserved from the struct's pre-existing state (read as function arguments before the memset).

Correctness Verdict: Correct

Semantic Alignment:
This is a Lavender-style initialization (NOT RAII). It cleans up the struct to its initial conditions by zeroing all fields except the Serialization_Header, then configures it as a Draggable element. The function does not acquire any resources; it only sets struct fields and handler pointers. The semantic intent — to prepare a UI element as a draggable — is fulfilled: the element kind is set to UI_Element_Kind__Draggable, a dragged handler is installed (caller-provided), and a default dropped handler is installed.

Implementation Correctness:
Type compatibility — all parameter types match their target field types exactly. m_ui_dragged_handler is of type m_UI_Dragged, which matches the field type. m_ui_draggable__dropped_handler__default has signature void(UI_Element*, Game*, Graphics_Window*) which matches the m_UI_Dropped typedef. UI_Element_Kind__Draggable is the correct enum value for the kind field. ui_flags is read as UI_Flags__u16 and passed as UI_Flags__u16. No implicit conversions or truncation.
No undefined behavior — no broken pointer arithmetic, no null dereference (p_ui_draggable is assumed non-null per pre-condition, consistent with the rest of the codebase), no type punning, no out-of-bounds access. The function arguments p_ui_draggable->p_parent, p_ui_draggable->p_child, p_ui_draggable->p_next, and p_ui_draggable->ui_flags are evaluated before the call to initialize_ui_element, so they are safely read before the memset zeroes the struct.
Validation — no validation is performed, which is appropriate for this low-level initialization function. The caller is responsible for ensuring p_ui_draggable is valid and m_ui_dragged_handler is either a valid function pointer or intentionally NULL.

Side Effects:
The function mutates *p_ui_draggable. Specifically:
1. All fields after Serialization_Header are zeroed (via initialize_ui_element's memset).
2. p_parent, p_child, p_next are set to their pre-existing values (preserved).
3. the_kind_of_ui_element__this_is is set to UI_Element_Kind__Draggable.
4. ui_flags is set to its pre-existing value (preserved, though the UI_FLAGS__BIT_IS_USING__SPRITE_OR_UI_TILE_SPAN bit may be cleared by initialize_ui_element's call to set_ui_element__compose_handler).
5. m_ui_dispose_handler, m_ui_compose_handler, and m_ui_transformed_handler are set to their default handlers by initialize_ui_element.
6. m_ui_dragged_handler is set to the provided handler.
7. m_ui_dropped_handler is set to m_ui_draggable__dropped_handler__default.
