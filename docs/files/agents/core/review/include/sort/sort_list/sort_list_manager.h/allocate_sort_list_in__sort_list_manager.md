allocate_sort_list_in__sort_list_manager — core/source/sort/sort_list/sort_list_manager.c

Allocates a Sort_List from the Sort_List_Manager's pool, assigning it a contiguous block of Sort_Nodes of the requested size. Returns nullptr on failure.

Pre-conditions:
1. p_sort_list_manager must be a non-null pointer to an initialized Sort_List_Manager.
2. quantity_of__nodes must be > 0 (a request for 0 nodes is semantically meaningless, though not explicitly guarded).
3. quantity_of__nodes must not exceed SORT_NODE__MAXIMUM_QUANTITY_OF (512).

Post-conditions:
1. On success: returns a pointer to a Sort_List that has been marked as allocated (is_allocated = true).
2. On success: the returned Sort_List's p_node_list points to a contiguous block of Sort_Nodes, and size_of__p_node_list is set to quantity_of__nodes.
3. On success: p_sort_list_manager->quantity_of__allocated_sort_lists is incremented by 1.
4. On success: p_sort_list_manager->quantity_of__allocated_sort_nodes is incremented by quantity_of__nodes.
5. On failure: returns 0 (nullptr). In debug builds, may abort. No allocation counters are modified on the sort_list path (but sort_nodes may have been partially allocated before the abort).

Correctness Verdict: Incorrect

Semantic Alignment:
The function's intent is to allocate a Sort_List with a contiguous block of Sort_Nodes. The implementation logic itself is sound: it validates available resources, finds the next free Sort_List slot, delegates node allocation to allocate_sort_nodes_in__sort_list_manager, and updates the manager's bookkeeping counters. However, the function is critically dependent on two inline helper functions defined in sort_list_manager.h:

  - get_quantity_of__available_sort_lists_in__sort_list_manager
  - get_quantity_of__available_sort_nodes_in__sort_list_manager

Both of these helper functions contain copy-paste bugs where the wrong "allocated" counter is subtracted:

1. get_quantity_of__available_sort_lists_in__sort_list_manager computes:
   SORT_LIST__MAXIMUM_QUANTITY_OF (64) - get_quantity_of__allocated_sort_NODES_in__sort_list_manager(...)
   It should instead compute:
   SORT_LIST__MAXIMUM_QUANTITY_OF (64) - get_quantity_of__allocated_sort_LISTS_in__sort_list_manager(...)

2. get_quantity_of__available_sort_nodes_in__sort_list_manager computes:
   SORT_NODE__MAXIMUM_QUANTITY_OF (512) - get_quantity_of__allocated_sort_LISTS_in__sort_list_manager(...)
   It should instead compute:
   SORT_NODE__MAXIMUM_QUANTITY_OF (512) - get_quantity_of__allocated_sort_NODES_in__sort_list_manager(...)

The two "available" functions have their subtract terms swapped. This means:

- The "no available sort list entries" check (line: if (!get_quantity_of__available_sort_lists_in__sort_list_manager(...))) computes 64 - (allocated nodes) instead of 64 - (allocated lists). Since allocated nodes (up to 512) can exceed 64, this unsigned subtraction underflows, wrapping to a very large number, effectively always passing the check. This defeats the guard entirely.

- The "node size exceeds available" check (line: if (quantity_of__remaining_nodes < quantity_of__nodes)) computes available nodes as 512 - (allocated lists) instead of 512 - (allocated nodes). Since allocated lists is typically small (max 64), this overestimates available nodes, potentially allowing allocation requests that exceed actual available nodes.

These bugs mean the function's pre-condition checks are unreliable, and the function may proceed with allocation when it should not, or fail to detect resource exhaustion. The semantic intent is not fulfilled due to these helper function bugs.

Implementation Correctness:
Type compatibility: All parameter types match their target fields exactly. p_sort_list_manager is Sort_List_Manager*, quantity_of__nodes is Quantity__u32 (uint32_t), and p_sort_list->size_of__p_node_list is a 31-bit bitfield of Quantity__u32 — assignment is safe.

Undefined behavior: No broken pointer arithmetic, no null dereference (null checks exist in debug paths), no type punning, no out-of-bounds access within the function itself. The function delegates to allocate_sort_nodes_in__sort_list_manager which performs the actual node indexing.

Validation: The function performs appropriate validation for its role (checking available lists and nodes before proceeding). However, the validation is undermined by the swapped counter bug in the inline helpers. The debug-only null checks for p_sort_list and p_sort_list->p_node_list are appropriate.

Side Effects:
1. Mutates p_sort_list_manager->quantity_of__allocated_sort_lists (incremented by 1).
2. Mutates p_sort_list_manager->quantity_of__allocated_sort_nodes (incremented by quantity_of__nodes).
3. Mutates the returned Sort_List: sets p_node_list, size_of__p_node_list, and is_allocated (via set_sort_list_as__allocated).
4. Delegates to allocate_sort_nodes_in__sort_list_manager which marks Sort_Node entries as allocated (is_allocated = true) in the sort_nodes pool.
5. In debug failure paths, may call debug_abort (terminates program) and set_sort_list_as__deallocated (redundant since the sort list was never marked allocated at that point).
