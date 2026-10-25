set_ui_element__dragged_handler — core/include/ui/ui_element.h

Sets the dragged handler callback on a UI_Element.

Pre-conditions:
1. p_ui_element must be a non-null pointer to a writable UI_Element object.
2. m_ui_dragged_handler may be NULL (it is a function pointer of type m_UI_Dragged).

Post-conditions:
1. p_ui_element->m_ui_dragged_handler is mutated to hold the value passed as m_ui_dragged_handler.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly assigns the handler to the corresponding struct field. The parameter type (m_UI_Dragged) matches the struct field type (m_UI_Dragged m_ui_dragged_handler in UI_Element) exactly. This is consistent with all other setter functions in the same file (e.g., set_ui_element__clicked_handler, set_ui_element__dropped_handler, set_ui_element__held_handler, etc.), which follow the same pattern of directly assigning the handler function pointer to the struct field.

Implementation Correctness:
Type compatibility — the parameter type m_UI_Dragged matches the target field type m_UI_Dragged exactly. No implicit conversions or truncation.
Undefined behavior — no pointer arithmetic, no null dereference (assuming p_ui_element is non-null per pre-conditions), no type punning, no out-of-bounds access.
Validation — no validation is needed; this is a low-level struct field assignment. The caller is responsible for ensuring p_ui_element is valid. This is consistent with the pattern used by all other setter functions in the same header.

Side Effects:
The only observable effect is writing the m_ui_dragged_handler field of the pointed-to UI_Element struct.
