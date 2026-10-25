swap_priority_of__ui_elenents_within__ui_manager — core/source/ui/ui_manager.c

Swaps the positions (and thus rendering priority) of two UI_Element pointers in the UI_Manager's internal pointer array `pM_ptr_array_of__ui_elements`.

Pre-conditions:
1. p_ui_manager must be a non-null pointer to an initialized UI_Manager with allocated members (pM_ptr_array_of__ui_elements must be non-null and populated).
2. p_ui_element__this must be a pointer to a UI_Element that is currently registered in p_ui_manager's pointer array (i.e., allocated from this manager and not yet released).
3. p_ui_element__other must be a pointer to a UI_Element that is currently registered in p_ui_manager's pointer array (i.e., allocated from this manager and not yet released).
4. Both elements must be distinct entries in the pointer array (though the function does handle the same-element case as a no-op).

Post-conditions:
1. The two UI_Element pointers are swapped in the pointer array at the indices where they were found.
2. The UI_Element objects themselves are not mutated; only the pointer array entries are exchanged.
3. The UI_Manager's dirty flag is NOT set (unlike allocate_ui_element_from__ui_manager and release__ui_element_from__ui_manager, which both call set_ui_manager_as__dirty).

Correctness Verdict: Incorrect

Semantic Alignment:
The function's intent is to swap the priority (array index) of two UI elements. When both elements are valid and present, the swap logic is correct — it exchanges the two pointer slots. When both elements are the same (`p_ui_element__this == p_ui_element__other`), the function performs a redundant no-op (sets the slot to itself twice), which is semantically correct though wasteful. However, the implementation fails to validate that both elements are actually present in the manager's pointer array. The helper function `get_p_ptr_ui_element_from__ptr_array_in__ui_manager` returns NULL (0) when an element is not found, and this function dereferences the return value without any check, causing undefined behavior (null pointer dereference) whenever either element is missing from the manager. The core semantic intent is fulfilled for valid inputs, but the lack of validation for invalid inputs makes the function unsafe to call.

Implementation Correctness:
Type compatibility — parameter types match exactly: `p_ptr_ui_element__this` and `p_ptr_ui_element__other` are `UI_Element**`, and the values assigned (`*p_ptr_ui_element__this = p_ui_element__other`) are `UI_Element*`. No implicit conversions or truncation.
Undefined behavior — null pointer dereference: `get_p_ptr_ui_element_from__ptr_array_in__ui_manager` returns NULL when an element is not found in the pointer array. The function then dereferences this NULL pointer with `*p_ptr_ui_element__this = p_ui_element__other;` and `*p_ptr_ui_element__other = p_ui_element__this;`, which is undefined behavior. This is the primary correctness defect.
No out-of-bounds access — the helper function iterates within `max_quantity_of__ui_elements` bounds, so no array out-of-bounds access occurs.
No validation — the function lacks `#ifndef NDEBUG` parameter validation that other public API functions in this file consistently use (e.g., `initialize_ui_manager`, `release__ui_element_from__ui_manager`, `compose_all_ui_elements_in__ui_manager`). The caller `release__ui_element_from__ui_manager` does check the return of the same helper and reports "intrinsic violated" on NULL, demonstrating the codebase's expectation that this condition can occur.

Side Effects:
Mutates the UI_Manager's `pM_ptr_array_of__ui_elements` by exchanging the pointer values at two indices. Does NOT mark the UI_Manager as dirty (no call to `set_ui_manager_as__dirty`), which may be an oversight since priority changes affect rendering order. Does NOT mutate the UI_Element objects themselves.
