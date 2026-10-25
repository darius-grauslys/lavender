update_ui_manager_origin__relative_to — core/source/ui/ui_manager.c

Iterates over all UI elements in the manager and updates each enabled element's origin by the delta between position__old__3i32 and position__new__3i32.

Pre-conditions:
1. p_game must be a non-null pointer to a valid Game instance.
2. p_ui_manager must be a non-null pointer to a properly initialized and allocated UI_Manager (members allocated via allocate_ui_manager__members).
3. position__old__3i32 and position__new__3i32 are any valid Vector__3i32 values (no range constraints).

Post-conditions:
1. Each enabled UI_Element in the manager has its hitbox position updated by the relative delta (position__new__3i32 - position__old__3i32).
2. Disabled UI_Elements are skipped and remain unchanged.
3. The UI_Manager is marked as dirty (via update_ui_element_origin__relative_to, which calls set_ui_manager_as__dirty).

Correctness Verdict: Correct

Semantic Alignment:
The function correctly iterates over all UI elements in the manager and delegates to update_ui_element_origin__relative_to for each enabled element. The iteration logic matches the pattern used by other similar functions in the codebase (e.g., get_quantity_of__ui_elements_in__ui_manager, foreach_ui_element_in__ui_manager). The break on NULL is consistent with the packed ptr array invariant — once a NULL slot is encountered, all subsequent slots are also NULL.

Implementation Correctness:
Type compatibility — the loop variable is Index__u32 (uint32_t), while max_quantity_of__ui_elements is Quantity__u16 (uint16_t). The comparison involves an implicit widening from uint16_t to uint32_t, which is safe. The loop variable is then passed to get_p_ui_element_by__index_from__ui_manager, which expects Index__u16 (uint16_t). This is an implicit narrowing conversion, but since the loop bound is max_quantity_of__ui_elements (a uint16_t), the value will always fit in uint16_t — no data loss occurs in practice. No explicit validation of p_game or p_ui_manager for null is performed, but this is consistent with other iteration functions in this file (e.g., get_highest_priority_ui_element_thats__under_the_cursor, foreach_ui_element_in__ui_manager).
No undefined behavior — no broken pointer arithmetic, no null dereference (p_ui_element is checked before use), no type punning, no out-of-bounds access (loop is bounded by max_quantity_of__ui_elements, and get_p_ui_element_by__index_from__ui_manager has a debug bounds check).
No additional validation is needed — this is a mid-level iteration function. Debug builds of get_p_ui_element_by__index_from__ui_manager already guard against out-of-bounds indices.

Side Effects:
Mutates the hitbox positions of all enabled UI_Elements in the manager. Marks the UI_Manager as dirty via update_ui_element_origin__relative_to (which calls set_ui_manager_as__dirty).
