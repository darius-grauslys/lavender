foreach_ui_element_in__ui_manager — core/source/ui/ui_manager.c

Iterates over all UI_Element slots in the UI_Manager's pointer array, invoking a caller-provided callback for each allocated (non-deallocated) element.

Pre-conditions:
1. p_ui_manager must be a non-null pointer to an initialized UI_Manager with allocated members (pM_ptr_array_of__ui_elements must be non-null).
2. p_game may be NULL or non-null; it is forwarded to the callback without validation.
3. p_gfx_window may be NULL or non-null; it is forwarded to the callback without validation.
4. f_foreach_ui_element must be a non-null function pointer matching the f_Foreach_UI_Element signature.

Post-conditions:
1. The callback f_foreach_ui_element is invoked once for each UI_Element in p_ui_manager->pM_ptr_array_of__ui_elements that is not deallocated (i.e., not NULL and has a valid UUID).
2. No state of p_ui_manager is modified by this function (it is a read-only iteration).
3. The order of iteration is from index 0 to max_quantity_of__ui_elements - 1.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills the semantic intent: it iterates over all UI element slots and invokes the callback for each active element. The use of IS_DEALLOCATED_P (which checks both for NULL pointers and for deallocated UUIDs) is more thorough than a simple NULL check and correctly skips both unallocated and deallocated slots. This is consistent with the Lavender engine's pattern where "deallocated" means the struct has been reset to its initial conditions (UUID set to IDENTIFIER__UNKNOWN__u32).

Implementation Correctness:
- Type compatibility: The loop variable index_of__ui_element is declared as Index__u32 (uint32_t), but is passed to get_p_ui_element_by__index_from__ui_manager which expects Index__u16 (uint16_t). This is an implicit narrowing conversion. However, the loop is bounded by p_ui_manager->max_quantity_of__ui_elements (Quantity__u16 / uint16_t), so the value never exceeds the range of uint16_t. The conversion is safe in practice.
- The comparison index_of__ui_element < p_ui_manager->max_quantity_of__ui_elements compares uint32_t with uint16_t; the uint16_t is promoted to uint32_t, so no precision loss occurs.
- No undefined behavior: no broken pointer arithmetic, no null dereference (IS_DEALLOCATED_P guards against NULL), no type punning, no out-of-bounds access (the debug build of get_p_ui_element_by__index_from__ui_manager bounds-checks against MAX_QUANTITY_OF__UI_ELEMENTS, and the loop is bounded by max_quantity_of__ui_elements which is set by allocate_ui_manager__members).
- Validation: No parameter validation is performed within the function itself. This is consistent with the function's role as a low-level iteration utility; the caller is responsible for passing valid parameters.

Side Effects:
The function itself has no direct side effects on p_ui_manager or its members. However, it invokes f_foreach_ui_element for each active UI element, and that callback may produce side effects (e.g., composing, rendering, or updating UI elements). Those side effects are the responsibility of the callback, not this function.
