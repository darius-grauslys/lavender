set_ui_element__held_handler — core/include/ui/ui_element.h

Sets the "held" handler callback on a UI_Element struct.

Pre-conditions:
1. p_ui_element must be a non-null pointer to a writable UI_Element object.
2. m_ui_held_handler may be NULL or any valid function pointer of type m_UI_Held.

Post-conditions:
1. p_ui_element->m_ui_held_handler is assigned the value of the m_ui_held_handler parameter.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly assigns the m_ui_held_handler parameter to the corresponding m_ui_held_handler field of the UI_Element struct. The parameter type (m_UI_Held) matches the field type exactly. The implementation is a straightforward assignment with no semantic drift.

Implementation Correctness:
Type compatibility — the parameter type m_UI_Held matches the struct field type m_ui_held_handler (m_UI_Held) exactly. No implicit conversions or truncation.
Undefined behavior — no pointer arithmetic, no null dereference (caller must ensure p_ui_element is non-null), no type punning, no out-of-bounds access.
Validation — no validation is performed, which is consistent with the function's role as a simple setter and with all other analogous handler setters in this file (e.g., set_ui_element__dispose_handler, set_ui_element__clicked_handler). The caller is responsible for passing a valid pointer.

Side Effects:
Mutates p_ui_element->m_ui_held_handler by assigning the provided m_ui_held_handler value to it.
