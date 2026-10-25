# get_ui_element__transformed_handler

**File of origin:** `core/include/ui/ui_element.h`

## Semantic

Retrieves the `m_UI_Transformed` function pointer (the "transformed handler") stored on a `UI_Element`. This is a simple accessor/getter for the handler field that is invoked when a UI element is transformed.

## Pre-conditions

1. `p_ui_element` must be non-null. The function dereferences it directly without a null check; passing NULL results in undefined behavior.
2. The caller is expected to verify validity (e.g., via `does_ui_element_have__transformed_handler`) before calling this getter, consistent with the codebase's convention for all `get_*` accessor functions.

## Post-conditions

1. Returns the value of `p_ui_element->m_ui_transformed_handler`, which is of type `m_UI_Transformed` (a function pointer). The returned handler may be NULL if no transformed handler has been set on the element.
2. No state is modified; the function is a pure read of the struct field.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation fulfills its semantic intent: it returns the `m_ui_transformed_handler` field from the `UI_Element` struct. The return type (`m_UI_Transformed`) exactly matches the field type declared in the `UI_Element` struct in `defines.h`. No fields are omitted, reordered, or incorrectly accessed.

## Implementation Correctness

- **Type compatibility:** The return type `m_UI_Transformed` matches the field type `m_UI_Transformed` exactly. No implicit conversions or truncation occur.
- **Undefined behavior:** No out-of-bounds access, no broken pointer arithmetic, no type punning. The only potential UB is a null pointer dereference if `p_ui_element` is NULL, but this is by design — the codebase consistently delegates null-checking to the caller via the `does_ui_element_have__*` family of functions (e.g., `does_ui_element_have__transformed_handler` checks both `p_ui_element` and the handler field for truthiness).
- **Validation:** Appropriate for a getter function. The sibling getters (`get_ui_element__typed_handler`, `get_ui_element__compose_handler`) follow the identical pattern of no null check, confirming this is the established convention. Validation is the caller's responsibility.

## Side Effects

No side effects. This is a pure accessor function that reads and returns a single struct field without modifying any state.
