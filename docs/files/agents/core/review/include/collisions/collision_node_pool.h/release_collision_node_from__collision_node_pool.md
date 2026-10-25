release_collision_node_from__collision_node_pool — core/source/collisions/collision_node_pool.c

Marks a Collision_Node as deallocated by resetting its serialization header to the unknown identifier, returning it to the pool's free state (Lavender-style initialization / pool cleanup).

Pre-conditions:
1. p_collision_node_pool must be a non-null pointer to an initialized Collision_Node_Pool.
2. p_collision_node must be a non-null pointer to a Collision_Node that is an element of p_collision_node_pool->collision_nodes.
3. The node should be currently allocated (the function does not verify this).

Post-conditions:
1. p_collision_node->_serialization_header is reset to IDENTIFIER__UNKNOWN__u64 with size_of__struct = sizeof(Collision_Node), marking the node as deallocated.
2. p_collision_node->p_linked_list__collision_node_entries__tail is NOT reset — left stale.

Correctness Verdict: Incorrect

Semantic Alignment:
The function does not fully reset the node to its initial conditions. While initialize_collision_node (called during allocation) sets p_linked_list__collision_node_entries__tail = 0, the release function omits this reset. The serialization header reset is correct, but the node is not fully cleaned to its initial conditions as expected per Lavender's "initialization = cleanup to initial conditions" semantics. This is inconsistent with the sibling release_collision_node_entry_from__collision_node_pool, which calls initialize_collision_node_entry that fully resets all fields of the entry.

Implementation Correctness:
Type compatibility — the u32 index variable receives a ptrdiff_t from pointer subtraction. This is safe: valid indices fit in u32, and out-of-range indices wrap to values exceeding QUANTITY_OF__GLOBAL_SPACE, which the bounds check then catches. sizeof(Collision_Node) fits in Quantity__u32 for this struct. No truncation issues.
Undefined behavior — in debug mode, neither p_collision_node_pool nor p_collision_node is null-checked before use. If p_collision_node_pool is null, the dereference of p_collision_node_pool->collision_nodes is a null dereference (UB). If p_collision_node is null, the pointer subtraction p_collision_node - p_collision_node_pool->collision_nodes is UB. The sibling release_collision_node_entry_from__collision_node_pool null-checks both parameters before its bounds check; this function should too.
Validation — the debug validation is incomplete compared to the sibling entry-release function, which null-checks both pointers. For a pool management function, null-checking both parameters in debug mode is appropriate.

Side Effects:
Mutates p_collision_node->_serialization_header (resets uuid to IDENTIFIER__UNKNOWN__u64, sets size_of__struct to sizeof(Collision_Node)). Does NOT reset p_collision_node->p_linked_list__collision_node_entries__tail.
