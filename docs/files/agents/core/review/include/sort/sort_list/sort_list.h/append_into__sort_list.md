append_into__sort_list — core/source/sort/sort_list/sort_list.c

Uses a binary search to find an empty slot (p_node_data == NULL) in the sort list's contiguous node array, then delegates to insert_into__sort_list to place p_data at that index. Intended to append data at the back of the occupied portion of the list.

Pre-conditions:
1. p_sort_list must be a non-null pointer to a writable Sort_List object (checked in debug builds only).
2. p_sort_list->p_node_list must point to a contiguous array of Sort_Node objects (per the Sort_List contract).
3. p_sort_list->size_of__p_node_list must be > 0 (i.e., the list must have been allocated with at least one node). If zero, get_p_sort_node_by__index_from__sort_list returns NULL and the function dereferences it.
4. All Sort_Node entries in p_node_list must have is_allocated == true, so that get_p_sort_node_by__index_from__sort_list returns non-NULL for in-range indices. If any node has is_allocated == false, get_p_sort_node_by__index_from__sort_list returns NULL and the function dereferences it.
5. p_data may be any void pointer (including NULL, though passing NULL would make the node appear "empty" to future calls).
6. The caller is responsible for ensuring the list is not full; the function does not check for a full list.

Post-conditions:
1. p_data is written to p_sort_list->p_node_list[previous].p_node_data, where previous is the index determined by the binary search.
2. The function does not return a value; it has no success/failure indicator.

Correctness Verdict: Incorrect

Semantic Alignment:
The semantic intent (per the header comment: "This will put the element at the back of the list") is to find the first empty slot after the occupied portion of the list and insert p_data there. The implementation does NOT fulfill this intent. The binary search loop condition `while (p_current->p_node_data && !p_next->p_node_data)` causes the loop to terminate prematurely whenever two consecutive nodes are both occupied. A standard binary search for the first empty slot should continue while the search space has not been narrowed to a single point (i.e., while pivot_left < pivot_right). The current condition instead looks for a local transition from occupied to empty, which fails when the occupied portion is large.

Concrete counter-example: Sort list with capacity 8, nodes 0–6 occupied (p_node_data != NULL), node 7 empty.
- index starts at 4 (midpoint). Node 4 is occupied → pivot_left=4, index=(4+8)>>1=6.
- Node 6 is occupied. Loop condition: p_current->p_node_data (true) && !p_next->p_node_data (false, since node 6 is occupied) → loop terminates.
- previous = 4, which is an OCCUPIED slot. insert_into__sort_list overwrites node 4's p_node_data, destroying the existing entry.

The function does not check whether the resolved index points to an already-occupied node before calling insert_into__sort_list, so data loss occurs silently.

Implementation Correctness:
Type compatibility: Parameter types match target field types. p_sort_list is Sort_List*, p_data is void* (assigned to Sort_Node::p_node_data which is void*). Index arithmetic uses Index__u16 throughout; quantity_of__nodes (Quantity__u32) is narrowed to Index__u16 via cast when computing the initial index, and assigned directly to pivot_right (Index__u16). These implicit narrowing conversions are safe within the SORT_NODE__MAXIMUM_QUANTITY_OF limit of 512, but are technically lossy for values > 65535.

Undefined behavior — null pointer dereference:
- get_p_sort_node_by__index_from__sort_list can return NULL when is_sort_node__allocated is false (i.e., is_allocated bit is 0). If the initial call returns NULL (e.g., when size_of__p_node_list is 0, or when any node lacks is_allocated == true), then p_current and p_next are NULL. The do-while body immediately dereferences p_next->p_node_data without a null check, which is undefined behavior.
- Within the loop, p_next is reassigned via get_p_sort_node_by__index_from__sort_list on each iteration. If any call returns NULL (e.g., due to a node with is_allocated == false), the subsequent dereference of p_next->p_node_data or p_current->p_node_data is undefined behavior.
- There is no null check on p_current or p_next anywhere in the function.

Undefined behavior — no full-list guard:
- If all nodes in the list are occupied, the binary search terminates at an occupied index (as shown in the counter-example above), and insert_into__sort_list silently overwrites existing data. There is no check for whether the list is full before inserting.

Validation:
- The only validation is a debug-mode null check on p_sort_list. There is no validation for:
  - p_sort_list->p_node_list being non-null
  - p_sort_list->size_of__p_node_list being non-zero
  - Nodes having is_allocated == true
  - The target slot being empty (i.e., whether the list is full)
- Whether validation is appropriate depends on the function's role. Given that append_into__sort_list is a public API function (declared in sort_list.h), some defensive validation for the empty-list and null-node cases would be warranted. At minimum, the null-dereference risk when get_p_sort_node_by__index_from__sort_list returns NULL should be guarded.

Side Effects:
- Mutates p_sort_list->p_node_list[previous].p_node_data by assigning p_data to it.
- If previous points to an already-occupied node (due to the binary search bug), the previous p_node_data value is silently overwritten and lost.
- No other side effects; does not modify sort_data, f_sort_heuristic, m_sort, or any other Sort_List field.
