is_heap_sort__sorted — core/include/sort/sort_list/heap_sort.h

Checks whether the heapsort phase has completed by testing if the active heap size (index_of__heap_sort) has been reduced to 1 or fewer elements.

Pre-conditions:
1. p_sort_list must be a non-null pointer to a valid, initialized Sort_List.
2. p_sort_list->sort_data.index_of__heap_sort must be a valid Index__u16 value representing the current heap size. It is initialized to get_length_of__sort_list(p_sort_list) by request_resorting_of__heap_sort() and decremented by decrement_index_of__heap_sort_from__sort_list().
3. The Sort_List must have been initialized via initialize_sort_list_as__heap() or initialize_sort_list_as__heap_sort() so that sort_data.index_of__heap_sort is set to a meaningful value.

Post-conditions:
1. Returns true if index_of__heap_sort <= 1, indicating the heapsort is complete (the active heap has 0 or 1 elements remaining).
2. Returns false if index_of__heap_sort > 1, indicating more sorting steps are needed.
3. No mutation of p_sort_list or any state occurs; the function is read-only.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly implements the termination condition for heapsort. In the standard heapsort algorithm, after building the max-heap, the root (maximum element) is repeatedly swapped with the last element of the active heap, the heap size is decremented, and the root is sifted down. When the heap size reaches 1, the array is fully sorted. The check `index_of__heap_sort <= 1` correctly captures this: when index_of__heap_sort is 1, only the root remains in the active heap (trivially sorted), and when it is 0, the heap is empty (also sorted). The use of `<=` rather than `==` is safe and correct because index_of__heap_sort never underflows below 1 before this check returns true — the function is called at the top of m_sort__heap_sort__sort_list before any decrement occurs, and the initial value is always >= 0.

Implementation Correctness:
Type compatibility — get_index_of__heap_sort_from__sort_data returns Index__u16 (uint16_t), and the comparison `<= 1` is between two uint16_t values. No implicit conversions or truncation.
Undefined behavior — no pointer arithmetic, no null dereference (consistent with other static inline functions in heap_sort.h which also do not null-check), no type punning, no out-of-bounds access.
Validation — no validation is needed for this inline query function. Null-checking is the caller's responsibility, consistent with the codebase convention for static inline accessors in this header (e.g., is_sort_data__heapifed, is_heap__heapifed, get_index_of__heap_sort_from__sort_data all follow the same pattern).

Side Effects:
No side effects — the function is a pure read-only query. It does not mutate p_sort_list or any of its members.
