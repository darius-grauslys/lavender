get_p_sort_node_by__index_from__sort_list — core/source/sort/sort_list/sort_list.c

Returns a pointer to the Sort_Node at the given index within the sort list's contiguous node array, or null if the index is out of bounds or the node is not allocated.

Pre-conditions:
1. p_sort_list must be a non-null pointer to a valid, initialized Sort_List.
2. index_of__sort_node is an Index__u16 (uint16_t); no explicit range constraint beyond the sort list's size.
3. The sort list's p_node_list must be a valid pointer to a contiguous array of Sort_Node objects (as documented by the struct definition).

Post-conditions:
1. If index_of__sort_node >= get_length_of__sort_list(p_sort_list), returns 0 (null).
2. If the Sort_Node at the given index has is_allocated == false, returns 0 (null).
3. Otherwise, returns a pointer to the Sort_Node at p_sort_list->p_node_list[index_of__sort_node].
4. The pointed-to Sort_Node is not mutated by this function.

Correctness Verdict: Incorrect

Semantic Alignment:
The function's intent is to retrieve a pointer to a sort node by index. The bounds check is correct and matches intent. However, the additional is_sort_node__allocated check is semantically misaligned with how the sort list actually tracks node occupancy. Throughout the codebase, the sort list uses p_node_data == 0 (null) to indicate an empty/unoccupied node — not the is_allocated flag. This is evident from:
- insert_into__sort_list directly writes p_node_data without ever setting is_allocated.
- remove_from__sort_list sets p_node_data = 0 without setting is_allocated = false.
- append_into__sort_list checks p_next->p_node_data (not is_allocated) to determine if a node has data.
- initialize_sort_node_as__empty does not set is_allocated = false or clear p_node_data, despite being intended for pool cleanup (Lavender semantics).

The is_allocated flag is only ever set to true in initialize_sort_node_as__allocated and is never set to false anywhere in the codebase. The inline helpers set_sort_node_as__allocated and set_sort_node_as__deallocated exist but are never called. This means the is_allocated check is effectively dead/misleading logic that does not reflect the actual state of sort nodes.

Implementation Correctness:
Type compatibility — all parameter and return types match exactly (Sort_List *, Index__u16 → Sort_Node *). No implicit conversions or truncation.
Undefined behavior — the bounds check correctly prevents out-of-bounds array access. However, the is_allocated check introduces a latent null-dereference hazard in all callers that do not null-check the return value:
- initialize_sort_list_as__allocated: During initialization, nodes have not yet been initialized, so is_allocated may be false (especially if memory is zeroed). get_p_sort_node_by__index_from__sort_list returns 0, and initialize_sort_node_as__empty dereferences the null pointer.
- point_sort_list__sort_nodes_to__this_range: Iterates all indices and dereferences the returned pointer without null-checking. If any node has is_allocated == false, this dereferences null.
- append_into__sort_list: Dereferences the returned pointer (p_current->p_node_data, p_next->p_node_data) without null-checking. If the binary search lands on an unallocated node, this dereferences null.
- remove_from__sort_list: Iterates all indices and dereferences the returned pointer (p_sort_node->p_node_data) without null-checking. If any node has is_allocated == false, this dereferences null.
- get_next_p_sort_node_from__sort_list: This caller intentionally accepts null return as "no next node," but the null is caused by the wrong condition (is_allocated) rather than a meaningful semantic check.

The is_sort_node__allocated check is inconsistent with the sort list's actual occupancy model and introduces null-dereference bugs in multiple callers. The function should simply perform bounds checking and return the pointer to the node at the given index, leaving occupancy determination to the caller (which already checks p_node_data).

Side Effects:
No side effects — the function is read-only with respect to p_sort_list and its contained Sort_Nodes.
