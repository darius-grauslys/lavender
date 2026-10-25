initialize_sort_list_as__heap_sort — core/source/sort/sort_list/heap_sort.c

Configures a Sort_List to perform heap sort by delegating to initialize_sort_list_as__heap for heap structure setup and then setting the m_sort function pointer to m_sort__heap_sort__sort_list.

Pre-conditions:
1. p_sort_list must be a non-null pointer to a writable, already-allocated Sort_List (checked in debug builds only via debug_abort).
2. The sort list must have an even number of elements (checked in debug builds only via debug_abort). This is because heap sort in this engine requires even-length node lists — the heap is built using paired child indices.

Post-conditions:
1. p_sort_list is mutated: all Sort_Node index_for__next_node fields are updated to point to their left-child heap indices (via initialize_sort_list_as__heap → update_heap_sort_node__index_for__next_node).
2. p_sort_list->m_sort is set to m_sort__heap_sort__sort_list (overriding the m_sort__heapify__sort_list value set by initialize_sort_list_as__heap).
3. p_sort_list->sort_data.index_of__heapification is set to the parent index of the last node (via request_resorting_of__heap), indicating the heap is not yet heapified and needs heapification steps.
4. p_sort_list->sort_data.index_of__heap_sort is set to the full length of the list (via request_resorting_of__heap_sort), indicating no sorting has been performed yet.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly fulfills its semantic intent: it configures a Sort_List for heap sort by first setting up the heap data structure (node indices, sort data fields) via initialize_sort_list_as__heap, then overriding m_sort to point to m_sort__heap_sort__sort_list. The override is necessary and correct — initialize_sort_list_as__heap sets m_sort to m_sort__heapify__sort_list (the heapify phase function), and without the override, m_sort__heapify__sort_list would return early with a debug warning once heapification completes (since it checks for INDEX__UNKNOWN__SORT_NODE and returns true without switching m_sort). By overriding m_sort to m_sort__heap_sort__sort_list, the sort-phase function becomes the active sort handler, which is designed to handle both phases: it checks is_heap__heapifed and if not heapified, should call m_sort__heapify__sort_list to perform one step of heapification before proceeding to the sort phase.

Note: There is a downstream bug in m_sort__heap_sort__sort_list (lines 283-313) where, when the heap is not yet heapified, it recursively calls m_sort__heap_sort__sort_list(p_sort_list) directly instead of calling m_sort__heapify__sort_list(p_sort_list). This causes infinite recursion when run_sort__once is invoked, because the heap is not heapified after initialization (index_of__heapification is set to a valid index, not INDEX__UNKNOWN__SORT_NODE). This bug resides in m_sort__heap_sort__sort_list, not in initialize_sort_list_as__heap_sort itself — the function correctly delegates to initialize_sort_list_as__heap and correctly sets m_sort to m_sort__heap_sort__sort_list.

Implementation Correctness:
Type compatibility — m_sort is of type m_Sort (bool (*)(Sort_List *)). Both m_sort__heapify__sort_list and m_sort__heap_sort__sort_list are bool functions taking Sort_List *, so assigning m_sort__heap_sort__sort_list to p_sort_list->m_sort is type-safe with no implicit conversions or truncation.
Undefined behavior — no broken pointer arithmetic, no null dereference (p_sort_list is checked in debug builds), no type punning, no out-of-bounds access. The pointer arithmetic in update_heap_sort_node__index_for__next_node (p_sort_node - p_sort_list->p_node_list) is safe because p_sort_node is always obtained from get_p_sort_node_by__index_from__sort_list within the bounds of the node list.
Validation — the null and odd-length checks are appropriate for debug builds. In release builds (NDEBUG defined), these checks are omitted, which is consistent with the codebase's pattern of relying on caller correctness for performance-critical paths.

Side Effects:
Mutates p_sort_list and its associated Sort_Node array:
1. Updates each Sort_Node's index_for__next_node to its left-child heap index (or INDEX__UNKNOWN__SORT_NODE if out of bounds).
2. Sets p_sort_list->m_sort to m_sort__heap_sort__sort_list.
3. Sets p_sort_list->sort_data.index_of__heapification to the parent index of the last node (requesting heapification).
4. Sets p_sort_list->sort_data.index_of__heap_sort to the list length (requesting heap sort).
