is_heap__heapifed — core/include/sort/sort_list/heap_sort.h

Checks whether heapification of the sort list's heap is complete.

Pre-conditions:
1. p_sort_list must be a non-null pointer to a valid Sort_List object.

Post-conditions:
1. Returns true if p_sort_list->sort_data.index_of__heapification equals INDEX__UNKNOWN__SORT_NODE, indicating heapification is complete.
2. Returns false otherwise.
3. No mutation occurs; the function is read-only.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly tests whether the heap is fully heapified by comparing index_of__heapification against INDEX__UNKNOWN__SORT_NODE. The Sort_Data union's struct member index_of__heapification is documented as "if equals INDEX__UNKNOWN__SORT_NODE then heapify is complete." The implementation matches this semantic intent exactly. The function delegates to is_sort_data__heapifed, which performs the comparison correctly.

Implementation Correctness:
Type compatibility — p_sort_list is a Sort_List*, and p_sort_list->sort_data is a Sort_Data, whose address is passed to is_sort_data__heapifed(Sort_Data *). Types match exactly. The comparison p_sort_data->index_of__heapification == INDEX__UNKNOWN__SORT_NODE compares two Index__u16 (uint16_t) values — no implicit conversions or truncation.
Undefined behavior — no pointer arithmetic, no null dereference (pre-condition requires non-null), no type punning, no out-of-bounds access. The union is accessed only through its struct member, which is well-defined.
No validation is needed beyond the non-null pre-condition — this is a simple predicate function. Null checking is the caller's responsibility (consistent with the codebase pattern for inline accessors).

Side Effects:
No side effects — the function reads from p_sort_list->sort_data and returns a bool. No mutation of any state occurs.
