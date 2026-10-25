# set_ui_element__dispose_handler

## File of origin
`core/include/ui/ui_element.h`

## Semantic
Sets the dispose handler callback function pointer on a `UI_Element` struct. This handler is invoked when the UI element is being disposed/deinitialized, allowing custom cleanup logic to run. The default handler (`m_ui_element__dispose_handler__default`) marks the UI manager as dirty and recursively disposes child elements.

## Pre-conditions
1. `p_ui_element` must be a valid, non-null pointer to an allocated `UI_Element` struct. No null-check is performed inside the function; ensuring validity is the caller's responsibility.
2. `m_ui_dispose_handler` may be null — passing null clears the handler, effectively unsetting it (verified by `does_ui_element_have__dispose_handler`, which checks both the element pointer and the handler).

## Post-conditions
1. `p_ui_element->m_ui_dispose_handler` is set to the value of `m_ui_dispose_handler`.
2. No other fields of `UI_Element` are modified.

## Correctness Verdict
Correct

## Semantic Alignment
The implementation fulfills the semantic intent. The parameter type `m_UI_Dispose` matches the struct field `m_ui_dispose_handler` exactly (both are `void (*)(UI_Element*, Game*, Graphics_Window*)`). The assignment is straightforward with no reordering, no omitted fields, and no unintended side effects. This setter is called during `initialize_ui_element` to install the default dispose handler, confirming its intended use.

## Implementation Correctness
- **Type compatibility**: The parameter type `m_UI_Dispose` and the struct field `m_ui_dispose_handler` are the same typedef, so assignment is exact with no implicit conversions or truncation.
- **Undefined behavior**: `p_ui_element` is dereferenced without a null check. However, this is consistent with the codebase convention — all sibling setter functions (`set_ui_element__clicked_handler`, `set_ui_element__dragged_handler`, `set_ui_element__dropped_handler`, etc.) follow the same pattern of not null-checking. The corresponding getter/checker functions (`does_ui_element_have__dispose_handler` and siblings) DO perform null checks, establishing a clear design pattern: callers must ensure valid pointers when invoking setters.
- **Validation**: No validation is appropriate for this function's role. Null-checking is the caller's responsibility, consistent with all sibling setter functions in the same file.

## Side Effects
Mutates `p_ui_element->m_ui_dispose_handler` by assigning the provided function pointer to it. No other state is modified.
