get_ui_element__compose_handler — core/include/ui/ui_element.h, lines 631-636

## Semantic

Returns the `m_ui_compose_handler` function pointer stored in a `UI_Element`, which is used to compose (render) the UI element via its tile span.

## Pre-conditions

1. `p_ui_element` must be a valid, non-null pointer to an initialized `UI_Element` struct. The function dereferences `p_ui_element` directly without a null check; passing null results in undefined behavior.

## Post-conditions

1. Returns the value of the `m_ui_compose_handler` field from the `UI_Element` struct. The returned value is of type `m_UI_Compose` (a function pointer typedef) and may be `NULL` if no compose handler has been set.
2. No state is modified; the function is a pure accessor.

## Correctness Verdict

Correct

## Semantic Alignment

The implementation faithfully fulfills its semantic intent. It directly returns the `m_ui_compose_handler` field from the `UI_Element` struct. The return type (`m_UI_Compose`) exactly matches the field type (`m_UI_Compose`), so there are no type mismatches or implicit conversions.

## Implementation Correctness

- **Type compatibility:** The return type `m_UI_Compose` and the struct field `m_ui_compose_handler` are the same type. No implicit conversions or truncation occur.
- **Undefined behavior:** The function dereferences `p_ui_element` without null-checking. This is consistent with the pattern of other plain getter functions in this file (e.g., `get_ui_element__typed_handler`, `get_ui_element__transformed_handler`), which also do not null-check. Null safety is instead handled by the companion `does_ui_element_have__*` functions (e.g., `does_ui_element_have__compose_handler`), which perform the null check before calling this getter.
- **Validation:** No validation is performed, which is appropriate for this function's role as a simple accessor. It is the caller's responsibility to ensure `p_ui_element` is valid.

## Side Effects

No side effects. The function is a pure read-only accessor that returns a copy of the `m_ui_compose_handler` function pointer.
