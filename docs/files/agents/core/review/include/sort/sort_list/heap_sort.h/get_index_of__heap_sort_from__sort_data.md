get_index_of__heap_sort_from__sort_data — core/include/sort/sort_list/heap_sort.h

Returns the current heap sort index stored in a Sort_Data union.

Pre-conditions:
1. p_sort_data must be a non-null pointer to a valid Sort_Data object.

Post-conditions:
1. Returns the value of p_sort_data->index_of__heap_sort, an Index__u16 (uint16_t) representing the current position in the heap sort algorithm.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly fulfills its semantic intent. It is a simple accessor that reads the index_of__heap_sort field from the Sort_Data union. The field is part of the Heapsort struct variant (defined in defines.h, lines 1443-1444) alongside index_of__heapification. The function does exactly what its name implies — retrieves the heap sort index from sort data. No semantic drift.

Implementation Correctness:
Type compatibility — the return type Index__u16 (uint16_t) exactly matches the type of the index_of__heap_sort field (Index__u16), so there is no implicit conversion or truncation.
Undefined behavior — no pointer arithmetic, no null dereference (assuming the caller passes a valid non-null pointer, which is the caller's responsibility), no type punning, no out-of-bounds access. The function dereferences p_sort_data once to read a single field.
Validation — no validation is performed, which is appropriate for this file's pattern. The sibling accessor is_sort_data__heapifed (lines 44-49 of heap_sort.h) likewise omits null checks, unlike the inline functions in sort_list.h. This is consistent within heap_sort.h. The caller is responsible for ensuring p_sort_data is valid.

Side Effects:
No side effects — this is a pure read accessor. It does not modify p_sort_data or any other state.
