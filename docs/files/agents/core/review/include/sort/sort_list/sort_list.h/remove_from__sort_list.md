remove_from__sort_list — core/source/sort/sort_list/sort_list.c, lines 145-167

Linearly searches the sort list for a node whose p_node_data pointer matches p_data, and clears it (sets p_node_data to 0). Returns after the first match.

Pre-conditions:
1. p_sort_list must be a non-null pointer to a properly initialized Sort_List (initialized via initialize_sort_list_as__allocated, so p_node_list is non-null and size_of__p_node_list is set).
2. p_data should be a non-null pointer to data previously inserted via insert_into__sort_list or append_into__sort_list. Passing NULL is undefined in intent (see Implementation Correctness).
3. The sort list's p_node_list must be a valid, contiguous array of Sort_Node objects of length size_of__p_node_list.

Post-conditions:
1. If a node with p_node_data == p_data is found, that node's p_node_data is set to 0 (NULL) and the function returns immediately.
2. If no matching node is found, the sort list is unchanged.
3. Only the first matching node is cleared; subsequent matches are not affected.

Correctness Verdict: Incorrect

Semantic Alignment:
The function's stated intent is to linearly search all nodes in the list for a matching p_data pointer and clear it. However, the implementation uses get_p_sort_node_by__index_from__sort_list to obtain each node pointer. This helper function returns NULL (0) when a node's is_allocated field is false. The loop in remove_from__sort_list then immediately dereferences the result (p_sort_node->p_node_data) without checking for NULL, causing undefined behavior (null pointer dereference) whenever an unallocated node is encountered.

This is not merely a theoretical issue: insert_into__sort_list never sets is_allocated to true (it uses direct array access: p_sort_list->p_node_list[index].p_node_data = p_data), so nodes inserted via the standard insert path remain with is_allocated == false (assuming zeroed memory from initialize_sort_node_as__empty). Consequently, get_p_sort_node_by__index_from__sort_list will return NULL for these nodes, and remove_from__sort_list will dereference NULL on the first iteration.

The correct approach — consistent with insert_into__sort_list — is to access the node list directly via p_sort_list->p_node_list[index_of__sort_node] rather than routing through get_p_sort_node_by__index_from__sort_list.

Additionally, the function does not set is_allocated to false when clearing a node's p_node_data. In Lavender semantics, "removal" should reset the node to its initial conditions. The is_allocated flag should be cleared to properly mark the node as free, consistent with the pool-cleanup interpretation of initialization. However, since insert_into__sort_list also does not set is_allocated to true, this is a broader inconsistency in the sort list API.

Implementation Correctness:
- Null pointer dereference (critical): get_p_sort_node_by__index_from__sort_list can return NULL when is_sort_node__allocated returns false. The code dereferences this pointer unconditionally at p_sort_node->p_node_data, which is undefined behavior. This is the primary bug.
- Missing p_data validation: In debug builds, p_sort_list is null-checked, but p_data is not. If p_data is NULL, the comparison p_sort_node->p_node_data == p_data could match empty nodes (whose p_node_data is NULL), causing unintended removal of uninitialized slots.
- Type compatibility: All types are compatible. p_node_data is void*, p_data is void*, and the comparison and assignment are type-correct.
- No out-of-bounds access: The loop bounds are correct (0 to get_length_of__sort_list - 1), and the index is always valid when passed to get_p_sort_node_by__index_from__sort_list.

Side Effects:
- Mutates p_sort_list->p_node_list[index].p_node_data (sets to 0) for the first matching node.
- Does not mutate is_allocated, heuristic_value, or index_for__next_node.
- No other observable side effects (no I/O, no global state changes).
