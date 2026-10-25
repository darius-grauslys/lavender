request_resorting_of__heap — core/source/sort/sort_list/heap_sort.c

Sets the heapification starting index to the parent of the last node in the sort list, initiating the heapify phase of heapsort.

Pre-conditions:
1. p_sort_list must be a non-null pointer to an initialized Sort_List.
2. The sort list must have a length of at least 1 (i.e., size_of__p_node_list >= 1). If the length is 0, the subtraction in get_length_of__sort_list(p_sort_list) - 1 would underflow (uint32_t wrap to UINT32_MAX), producing an invalid parent index.
3. No debug validation is performed within this function; null-checking and length validation are the caller's responsibility.

Post-conditions:
1. p_sort_list->sort_data.index_of__heapification is set to the parent index of the last node in the sort list, computed as (get_length_of__sort_list(p_sort_list) - 1 - 1) >> 1, i.e., (length - 2) >> 1.
2. No other fields of p_sort_list or sort_data are modified.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly computes the starting index for heapification. In a standard heapsort, heapification begins at the parent of the last leaf node. For a 0-indexed array of length N, the last node is at index N-1, and its parent is at ((N-1) - 1) / 2 = (N-2) / 2. The function delegates to get_heap_sort_index_of__parent_sort_node which computes (index - 1) >> 1, correctly producing the parent index. The result is stored in sort_data.index_of__heapification, which is the field read by m_sort__heapify__sort_list to drive the heapification loop. The implementation fulfills its semantic intent.

Implementation Correctness:
Type compatibility — get_length_of__sort_list returns Quantity__u32 (uint32_t). The subtraction of 1 is performed in uint32_t arithmetic. The result is passed to get_heap_sort_index_of__parent_sort_node which takes Index__u16 (uint16_t). This causes an implicit narrowing conversion from u32 to u16. However, this is acceptable because the parent index of any node in a sort list with at most SORT_NODE__MAXIMUM_QUANTITY_OF (512) nodes will fit within 16 bits. No truncation occurs for valid inputs.
Undefined behavior — no pointer arithmetic beyond simple struct member access, no null dereference (caller must ensure non-null), no type punning, no out-of-bounds access. The function only writes to a single struct field.
Validation — no validation is performed within this function. This is appropriate for its role as a low-level setter; the caller (e.g., initialize_sort_list_as__heap) is expected to have already validated the sort list state.

Side Effects:
Mutates p_sort_list->sort_data.index_of__heapification. No other observable side effects.
