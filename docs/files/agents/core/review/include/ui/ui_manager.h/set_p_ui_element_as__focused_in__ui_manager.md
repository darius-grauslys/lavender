# set_p_ui_element_as__focused_in__ui_manager

**File of origin:** `core/source/ui/ui_manager.c`

## Semantic

Sets the UI_Manager's tracked focused UI_Element pointer to the given UI_Element. This is a low-level setter that updates only the manager's internal pointer; it does not modify the focus flag on the UI_Element itself.

## Pre-conditions

1. `p_ui_manager` must be a valid, non-null pointer to an allocated and initialized UI_Manager struct.
2. `p_ui_element` may be null (to clear focus) or a valid pointer to a UI_Element. The function does not dereference `p_ui_element`, so null is acceptable.

## Post-conditions

1. `p_ui_manager->p_ui_element__focused` is set to the value of `p_ui_element` (which may be null).
2. No other state on the UI_Manager or UI_Element is modified.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation faithfully fulfills its semantic intent: it assigns the `p_ui_element` pointer directly to `p_ui_manager->p_ui_element__focused`. The field `p_ui_element__focused` in the `UI_Manager` struct (defined in `core/include/defines.h`, struct `UI_Manager_t`) is of type `UI_Element *`, and the parameter `p_ui_element` is also of type `UI_Element *`, so there is an exact type match with no implicit conversions or truncation.

The function deliberately does not call `set_ui_element_as__focused` (which sets the `UI_FLAGS__BIT_IS_FOCUSED` flag on the element). This is appropriate — the caller at line 308 of `ui_manager.c` has already determined focus through `detect_focus_in__ui_manager` and the element's focus flag is managed separately. The function's role is narrowly scoped to updating the manager's tracking pointer, which aligns with the codebase pattern where `get_p_ui_element__focused_of__ui_manager` and `drop_ui_element_focus_for__ui_manager` all operate on this same pointer.

## Implementation Correctness

- **Type compatibility:** The parameter type `UI_Element *` matches the struct field type `UI_Element *` exactly. No implicit conversions or truncation occur.
- **Undefined behavior:** None. The function performs a simple pointer assignment. It does not dereference `p_ui_element`, so passing null is safe.
- **Validation:** No validation is performed on either parameter. This is appropriate for a `static inline` low-level setter — validation (including null checks on `p_ui_manager`) is the caller's responsibility, consistent with the pattern used by other inline helpers in this file (e.g., `set_ui_manager_as__dirty`, `set_ui_manager_as__NOT_dirty`).

## Side Effects

- Mutates `p_ui_manager->p_ui_element__focused` by assigning `p_ui_element` to it.
- Does not call any other functions or modify any other state.
