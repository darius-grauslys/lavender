does_ui_element_have__receive_drop_handler — core/include/ui/ui_element.h

Checks whether a UI_Element has a non-null receive-drop handler assigned (i.e., the m_ui_receive_drop_handler function pointer field is set to a valid handler).

Pre-conditions:
1. p_ui_element may be NULL — the function handles this safely via short-circuit evaluation of the && operator.
2. If p_ui_element is non-NULL, it must point to a valid, initialized UI_Element struct whose m_ui_receive_drop_handler field is accessible.

Post-conditions:
1. Returns true if p_ui_element is non-null AND p_ui_element->m_ui_receive_drop_handler is non-null (i.e., a handler has been set).
2. Returns false if p_ui_element is NULL or if m_ui_receive_drop_handler is NULL (i.e., no handler has been set).
3. The UI_Element struct is not mutated — this is a read-only query.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly fulfills its semantic intent: it returns whether the UI element has a receive-drop handler set. The implementation uses the standard C idiom of evaluating a function pointer in a boolean context (non-null = true, null = false). This is consistent with the pattern used by all other `does_ui_element_have__*` functions in the same header (e.g., does_ui_element_have__dispose_handler, does_ui_element_have__clicked_handler, does_ui_element_have__held_handler, etc.), which all use the same `p_ui_element && p_ui_element->m_ui_<handler>` pattern.

Implementation Correctness:
Type compatibility — p_ui_element is of type UI_Element * and m_ui_receive_drop_handler is of type m_UI_Receive_Drop (a function pointer typedef defined in core/include/defines.h as `typedef void (*m_UI_Receive_Drop)(UI_Element *, UI_Element *, Game *, Graphics_Window *)`). The expression `p_ui_element->m_ui_receive_drop_handler` evaluates the function pointer in a boolean context, which is well-defined in C (any non-null pointer converts to true, any null pointer converts to false). No implicit conversions or truncation issues.
Undefined behavior — No pointer arithmetic, no null dereference (the && short-circuit ensures p_ui_element is checked before accessing its member), no type punning, no out-of-bounds access.
Validation — The null check on p_ui_element is appropriate and consistent with the codebase pattern for these "does_have" query functions. No additional validation is required for this simple accessor.

Side Effects:
No side effects. The function is a pure query that only reads the p_ui_element pointer and its m_ui_receive_drop_handler field. No memory is allocated, no state is mutated, and no I/O occurs.
