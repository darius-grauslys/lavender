m_sort__heapify__sort_list — core/source/sort/sort_list/heap_sort.c

Performs one incremental step of bottom-up heap construction (Floyd's algorithm) on a Sort_List. Sifts down the node at the current heapification index, then advances toward the root. When the root (index 0) is processed, marks heapify as complete and initializes the heap-sort index for the subsequent extraction phase.

Pre-conditions:
1. p_sort_list must be a non-null pointer to a writable Sort_List that has been initialized via initialize_sort_list_as__heap (or initialize_sort_list_as__heap_sort).
2. sort_data.index_of__heapification must be a valid heap node index (0 to last non-leaf node) or INDEX__UNKNOWN__SORT_NODE (indicating heapify is already complete).
3. sort_data.index_of__heap_sort must be set to the full list length (done by request_resorting_of__heap_sort during initialization) so that sift_down_in__heap considers the entire list as the heap.
4. f_sort_heuristic must be non-null (set during initialization).
5. All Sort_Nodes in p_node_list must be allocated and have valid p_node_data.
6. The list length must be even (enforced by initialize_sort_list_as__heap in debug builds).

Post-conditions:
1. If index_of__heapification was INDEX__UNKNOWN__SORT_NODE on entry: no mutation occurs; returns true (heapify already complete).
2. If index_of__heapification was > 0 on entry: the node at that index has been sifted down to satisfy the heap property relative to its subtree; index_of__heapification is decremented by 1; returns false (more steps needed).
3. If index_of__heapification was 0 on entry: the root node has been sifted down (heap property now satisfied for the entire list); sort_data.index_of__heapification is set to INDEX__UNKNOWN__SORT_NODE (heapify complete); sort_data.index_of__heap_sort is set to the full list length (preparing for the extraction phase); returns true (heapify complete).

Correctness Verdict: Correct

Semantic Alignment:
The function correctly implements one step of bottom-up heap construction. It processes nodes from the last non-leaf node (set by request_resorting_of__heap) down to the root, sifting each down. When the root is reached, it marks heapify as complete and sets up index_of__heap_sort for the subsequent m_sort__heap_sort__sort_list phase. The computation matches the semantic intent of Floyd's heapify algorithm.

Implementation Correctness:
Type compatibility — all types are correct. index_of__heapification is Index__u16, matching the struct field. INDEX__UNKNOWN__SORT_NODE is defined as (INDEX__UNKNOWN__u16 >> 1) = 0x7FFF, which is the correct sentinel value. The decrement of a uint16_t is safe because it only occurs when index_of__heapification > 0 (the == 0 case is handled by the if-block), so no underflow is possible.
No undefined behavior — no null dereference (p_sort_list is assumed non-null by contract; callers like run_sort__once validate this first), no out-of-bounds access (index_of__heapification is always a valid index set by request_resorting_of__heap), no type punning.
Validation — no null check for p_sort_list is present, but this is consistent with the codebase convention; validation is the caller's responsibility (run_sort__once and run_sort both check for null before dispatching to m_sort).

Side Effects:
Mutates p_sort_list->sort_data.index_of__heapification (decremented or set to INDEX__UNKNOWN__SORT_NODE) and p_sort_list->sort_data.index_of__heap_sort (set to full list length when heapify completes). Also mutates the Sort_Node array contents via sift_down_in__heap (which may swap nodes and update their index_for__next_node fields). No side effects outside of p_sort_list.

Note: When index_of__heapification reaches 0, the function performs a second sift_down_in__heap call on the root node. This is redundant — the first sift_down already ensures the heap property is satisfied for the root's subtree, and all child subtrees were processed in prior steps. The second call is a no-op (sift_down_in__heap will find no violations and return immediately). This is a minor inefficiency, not a correctness issue.
