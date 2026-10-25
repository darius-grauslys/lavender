rotate_heap — core/source/sort/sort_list/heap_sort.c

Swaps the root node (index 0) with the last node in the sort list, then updates the
index_for__next_node fields of both swapped nodes to reflect their new positions.

Pre-conditions:
1. p_sort_list must be a non-null pointer to a valid Sort_List.
2. p_sort_list->p_node_list must be non-null and point to a contiguous array of
   Sort_Node elements.
3. get_length_of__sort_list(p_sort_list) must be greater than 0; otherwise
   (length - 1) underflows (Quantity__u32 is uint32_t) and produces an out-of-range
   index.
4. The sort list must have been initialized as a heap (via initialize_sort_list_as__heap
   or initialize_sort_list_as__heap_sort) so that index_for__next_node fields are valid.
5. The Sort_Nodes at index 0 and index (length - 1) must be allocated (is_allocated == true);
   otherwise get_p_sort_node_by__index_from__sort_list returns NULL and
   swap_sort_nodes_in__heap dereferences a null pointer.

Post-conditions:
1. The Sort_Node at index 0 and the Sort_Node at index (length - 1) are swapped
   (their full struct contents are exchanged).
2. Both swapped nodes have their index_for__next_node fields recomputed via
   update_heap_sort_node__index_for__next_node, which sets the field to
   (new_index << 1) + 1 (the left-child index) or INDEX__UNKNOWN__SORT_NODE
   if that index is out of bounds.

Correctness Verdict: Correct

Semantic Alignment:
The function fulfills its documented semantic intent: "Swaps the root with the last leaf."
It delegates to swap_sort_nodes_in__heap, which performs a full struct copy-swap of the
two nodes and then calls update_heap_sort_node__index_for__next_node on each. The
index update uses pointer arithmetic (p_sort_node - p_sort_list->p_node_list) to
determine each node's actual array position after the swap, ensuring index_for__next_node
correctly reflects the left child of the node's new position. This is correct.

Implementation Correctness:
Type compatibility — get_p_sort_node_by__index_from__sort_list expects Index__u16
(uint16_t), but get_length_of__sort_list returns Quantity__u32 (uint32_t). The
expression (length - 1) is implicitly narrowed from uint32_t to uint16_t. This is
safe given SORT_NODE__MAXIMUM_QUANTITY_OF is 512 and SORT_LIST__MAXIMUM_QUANTITY_OF
is 64, so no truncation occurs in practice.
Undefined behavior — no undefined behavior when all pre-conditions hold. No pointer
arithmetic errors, no null dereference, no type punning, no out-of-bounds access.
Validation — no validation is performed in this function. This is consistent with the
codebase pattern for non-inline functions in .c files (e.g., swap_sort_nodes_in__heap
also performs no null checks). Debug assertions exist in inline header functions
(e.g., get_length_of__sort_list) and in initialization functions, but not in this
non-inline sort-step function. The caller is responsible for ensuring valid state.

Side Effects:
Mutates the Sort_Node structs at index 0 and index (length - 1): their full contents
are swapped (including p_node_data, heuristic_value, index_for__next_node, and
is_allocated), and then index_for__next_node is overwritten for both to reflect
their new positions. No other state is modified.
