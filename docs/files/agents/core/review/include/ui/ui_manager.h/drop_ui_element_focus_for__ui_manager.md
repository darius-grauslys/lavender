drop_ui_element_focus_for__ui_manager — core/source/ui/ui_manager.c

Drops the currently focused UI element by clearing its focused flag and nulling the UI_Manager's focused pointer.

Pre-conditions:
1. p_ui_manager must be a non-null pointer to a valid, initialized UI_Manager object.
2. If p_ui_manager->p_ui_element__focused is non-null, it must point to a valid UI_Element object.

Post-conditions:
1. If p_ui_manager->p_ui_element__focused was non-null, the UI_FLAGS__BIT_IS_FOCUSED bit in that element's ui_flags has been cleared.
2. p_ui_manager->p_ui_element__focused is set to 0 (null).

Correctness Verdict: Correct

Semantic Alignment:
The function fulfills the semantic intent of "dropping" focus. It first checks whether a focused element exists (non-null p_ui_element__focused). If so, it clears the focused flag on that element via set_ui_element_as__NOT_focused. Then it unconditionally nulls the p_ui_element__focused pointer, ensuring the UI_Manager no longer references any focused element. The two-step approach (clear flag, then null pointer) is correct and consistent with the engine's pattern of managing focus state.

Implementation Correctness:
- Type compatibility — p_ui_manager is UI_Manager *, matching the parameter type. p_ui_element__focused is UI_Element *, and set_ui_element_as__NOT_focused accepts UI_Element *, so types are compatible. The assignment of 0 to a UI_Element * is valid (null pointer constant).
- Undefined behavior — No undefined behavior. The null check on p_ui_manager->p_ui_element__focused before calling set_ui_element_as__NOT_focused prevents null dereference. No pointer arithmetic, no type punning, no out-of-bounds access.
- Validation — The null guard on p_ui_element__focused is appropriate for this function's role. The function does not validate p_ui_manager itself, which is acceptable as this is a low-level internal function (static inline) and the caller is responsible for passing a valid UI_Manager.

Side Effects:
- Mutates the ui_flags field of the previously focused UI_Element (if any) by clearing the UI_FLAGS__BIT_IS_FOCUSED bit.
- Mutates p_ui_manager->p_ui_element__focused, setting it to 0 (null).
