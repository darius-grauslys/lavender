get_quantity_of__ui_elements_in__ui_manager — core/source/ui/ui_manager.c

Counts the number of active (non-null) UI element pointers stored in the UI_Manager's pointer array.

Pre-conditions:
1. p_ui_manager must be a non-null pointer to a valid UI_Manager.
2. p_ui_manager must have been initialized via initialize_ui_manager() and had its members allocated via allocate_ui_manager__members(). After initialize_ui_manager() alone, max_quantity_of__ui_elements is 0 and the loop body does not execute (safe, returns 0).
3. p_ui_manager->pM_ptr_array_of__ui_elements must be a valid pointer to an array of UI_Element* of length max_quantity_of__ui_elements (guaranteed by allocate_ui_manager__members()).
4. max_quantity_of__ui_elements is a Quantity__u16 (uint16_t); the loop iterates from 0 up to (but not including) this value.

Post-conditions:
1. Returns a Quantity__u16 representing the count of non-null entries in pM_ptr_array_of__ui_elements[0..max_quantity_of__ui_elements-1].
2. No state is mutated; the function is read-only.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly fulfills its semantic intent. It iterates over every slot in the pointer array (bounded by max_quantity_of__ui_elements) and increments a counter for each non-null pointer. The pointer array is maintained as a compact array (non-null entries at the front, null entries after the last active element), so scanning the full range and counting non-null entries yields the correct count of active UI elements. The computation matches the semantic intent with no bugs.

Implementation Correctness:
Type compatibility — Index__u16 and Quantity__u16 are both uint16_t, so the loop comparison (index_of__ui_element < max_quantity_of__ui_elements) is a well-typed unsigned comparison with no implicit conversions or truncation. The counter is Quantity__u16 and matches the return type exactly.
Undefined behavior — no pointer arithmetic, no null dereference (assuming pre-conditions hold), no type punning, no out-of-bounds access (loop is bounded by max_quantity_of__ui_elements). If the manager was only initialized (not allocated), max_quantity_of__ui_elements is 0, so the loop does not execute and no array access occurs.
Validation — no null check on p_ui_manager is performed. This is consistent with the codebase pattern for internal utility functions (e.g., does_ui_manager_have__focused_ui_element, get_p_ui_element__focused_of__ui_manager, allocate_ui_manager__members, release_ui_manager__members also omit null checks). Functions with debug null checks tend to be those called from more external entry points (e.g., initialize_ui_manager, compose_all_ui_elements_in__ui_manager, release__ui_element_from__ui_manager). The omission here is a style choice consistent with the codebase, not a correctness bug.

Side Effects:
No side effects. The function is a pure read — it only reads p_ui_manager->max_quantity_of__ui_elements and p_ui_manager->pM_ptr_array_of__ui_elements and returns a count.
