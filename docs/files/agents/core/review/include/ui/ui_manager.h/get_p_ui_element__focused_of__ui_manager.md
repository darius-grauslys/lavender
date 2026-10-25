get_p_ui_element__focused_of__ui_manager — core/source/ui/ui_manager.c

Lazily retrieves the currently focused UI_Element from a UI_Manager, clearing the internal focus pointer if the referenced element is no longer marked as focused.

Pre-conditions:
1. p_ui_manager must be a non-null pointer to a validly initialized UI_Manager.
2. If p_ui_manager->p_ui_element__focused is non-null, it must point to a valid UI_Element object. If it is NULL (0), no dereference occurs.

Post-conditions:
1. If p_ui_manager->p_ui_element__focused was non-null and is_ui_element__focused() returned false, then p_ui_manager->p_ui_element__focused is set to NULL (0).
2. If p_ui_manager->p_ui_element__focused was non-null and is_ui_element__focused() returned true, p_ui_manager->p_ui_element__focused remains unchanged.
3. If p_ui_manager->p_ui_element__focused was NULL (0), it remains NULL.
4. The function returns the (possibly updated) value of p_ui_manager->p_ui_element__focused.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly implements lazy focus validation. It checks whether the internally tracked focused element is still marked as focused (via the UI_FLAGS__BIT_IS_FOCUSED bit in the element's ui_flags). If the element is no longer focused, the pointer is cleared to NULL so stale references are not returned. The short-circuit evaluation of the && operator ensures is_ui_element__focused is only called when p_ui_element__focused is non-null, preventing a null pointer dereference. The logic is consistent with the sibling function does_ui_manager_have__focused_ui_element (lines 18-27), which performs the same stale-focus cleanup pattern.

Implementation Correctness:
Type compatibility — p_ui_manager->p_ui_element__focused is of type UI_Element *, and assigning 0 (NULL) to it is type-correct. The return type UI_Element * matches the field type. No implicit conversions or truncation.
Undefined behavior — no null dereference, no broken pointer arithmetic, no type punning, no out-of-bounds access. The short-circuit && guards against calling is_ui_element__focused on a null pointer.
Validation — no validation of p_ui_manager itself is performed. This is consistent with the codebase's convention; sibling functions such as does_ui_manager_have__focused_ui_element also do not validate p_ui_manager. Validation of p_ui_manager is the caller's responsibility.

Side Effects:
The function mutates p_ui_manager->p_ui_element__focused, setting it to NULL if the previously tracked focused element is no longer focused. This is the only observable side effect.
