request_resorting_of__heap_sort — core/source/sort/sort_list/heap_sort.c

Sets the heap-sort boundary index to the current length of the sort list, marking the start of the heap-sort phase where elements are extracted one-by-one from the root.

Pre-conditions:
1. p_sort_list must be a non-null pointer to a valid, initialized Sort_List object.
2. p_sort_list->sort_data.index_of__heap_sort must be writable (it is a direct member of the Sort_Data union, which is a direct member of Sort_List).
3. get_length_of__sort_list(p_sort_list) must return a valid count (the caller is responsible for ensuring the Sort_List is properly allocated and populated).

Post-conditions:
1. p_sort_list->sort_data.index_of__heap_sort is set to get_length_of__sort_list(p_sort_list).
2. No other fields of Sort_List or Sort_Data are modified.
3. The function returns void; no return value.

Correctness Verdict: Correct

Semantic Alignment:
The function's intent is to initialize the heap-sort boundary to the full length of the sort list. In heap sort, the boundary index tracks the end of the active heap region (elements from index 0 to index_of__heap_sort-1 are part of the heap). Setting it to the full list length at initialization is correct — it means the entire list is initially considered as the heap. The implementation directly assigns get_length_of__sort_list(p_sort_list) to index_of__heap_sort, which matches the semantic intent. No fields are omitted or reordered.

Implementation Correctness:
Type compatibility — get_length_of__sort_list returns Quantity__u32, while index_of__heap_sort is Index__u16 (uint16_t). This is an implicit narrowing conversion from u32 to u16. In practice, SORT_NODE__MAXIMUM_QUANTITY_OF is 512, so the length will always fit in a u16, but the type mismatch is a potential concern for static analysis.
No undefined behavior — no null dereference (caller ensures p_sort_list is valid), no pointer arithmetic, no type punning, no out-of-bounds access.
No validation is performed within the function — this is consistent with the function's role as a low-level setter. The caller (initialize_sort_list_as__heap and m_sort__heapify__sort_list) is responsible for ensuring p_sort_list is valid.

Side Effects:
Mutates p_sort_list->sort_data.index_of__heap_sort by setting it to get_length_of__sort_list(p_sort_list). No other state is modified.
