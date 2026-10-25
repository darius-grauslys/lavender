set_ui_element_priority_higher_than__this_ui_element_in__ui_manager — core/source/ui/ui_manager.c, lines 837-855

Ensures that p_ui_element__higher_priority has a lower array index (i.e., higher visual priority) than p_ui_element__lower_priortiy by swapping their positions in the UI_Manager's priority ptr array when the higher-priority element currently has a higher index.

Pre-conditions:
1. p_ui_manager must be a non-null pointer to an initialized UI_Manager with allocated members (pM_ptr_array_of__ui_elements must be non-null).
2. p_ui_element__higher_priority must be a non-null pointer to a UI_Element that is currently tracked in p_ui_manager->pM_ptr_array_of__ui_elements.
3. p_ui_element__lower_priortiy must be a non-null pointer to a UI_Element that is currently tracked in p_ui_manager->pM_ptr_array_of__ui_elements.

Post-conditions:
1. If p_ui_element__higher_priority already has a lower or equal index than p_ui_element__lower_priortiy, no change is made to the ptr array.
2. If p_ui_element__higher_priority has a higher index than p_ui_element__lower_priortiy, the two entries are swapped in p_ui_manager->pM_ptr_array_of__ui_elements so that p_ui_element__higher_priority now occupies a lower index (higher priority).

Correctness Verdict: Incorrect

Semantic Alignment:
The logic correctly checks whether the "higher priority" element already has a lower or equal index, and only invokes the swap when it does not. The semantic intent — to ensure p_ui_element__higher_priority has higher priority (lower index) than p_ui_element__lower_priortiy — is fulfilled by the branching and swap call.

Implementation Correctness:
- Type compatibility: get_ui_element__priority returns Quantity__u16 (uint16_t), but the local variables priority_of__former and priority_of__later are declared as Quantity__u8 (uint8_t). This is an implicit narrowing conversion/truncation. While MAX_QUANTITY_OF__UI_ELEMENTS is currently 128 (so indices fit within u8), this is a latent type mismatch that would silently produce incorrect priority comparisons if the array size limit were ever raised above 256.
- Undefined behavior: If either UI_Element is not found in the manager's ptr array, get_p_ptr_ui_element_from__ptr_array_in__ui_manager returns null. get_ui_element__priority then performs pointer arithmetic on this null pointer (null_ptr - base_array_ptr), which is undefined behavior in C. Furthermore, swap_priority_of__ui_elenents_within__ui_manager (the callee invoked when the swap condition is met) also dereferences potentially-null pointers returned by get_p_ptr_ui_element_from__ptr_array_in__ui_manager without any null check, leading to null pointer dereference.
- Validation: The function performs no validation of its parameters. Unlike other functions in the same file (e.g., release__ui_element_from__ui_manager, allocate_ui_element_from__ui_manager, compose_all_ui_elements_in__ui_manager), which include #ifndef NDEBUG null checks on p_ui_manager and other critical pointers, this function has no such guards. The lack of validation is inappropriate given the function's direct use of pointer arithmetic and pointer dereference on results of lookups.

Side Effects:
May mutate p_ui_manager->pM_ptr_array_of__ui_elements by swapping two pointer entries (via swap_priority_of__ui_elenents_within__ui_manager). No other observable state is modified.
