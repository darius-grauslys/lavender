get_quantity_of__entries_in__collision_node — core/source/collisions/collision_node.c

Counts the number of entries in a collision node's singly-linked list by traversing from the tail (head) node to the end.

Pre-conditions:
1. p_collision_node must be a non-null pointer to an initialized Collision_Node struct.
2. The collision node's p_linked_list__collision_node_entries__tail must either be NULL (empty list) or point to a validly-linked list of Collision_Node_Entry structs chained via p_previous_entry.

Post-conditions:
1) Returns 0 if the linked list is empty (tail is NULL).
2) Returns the exact count of Collision_Node_Entry nodes traversed if the list is non-empty.
3) The Collision_Node and all its linked-list entries are not modified (the parameter is const-qualified).

Correctness Verdict: Correct

Semantic Alignment:
The function traverses the singly-linked list starting from p_linked_list__collision_node_entries__tail and counts each node. Entries are linked via p_previous_entry, forming a LIFO chain from the most-recently-added entry (the "tail" pointer) down to the oldest entry whose p_previous_entry is NULL. The do-while loop correctly counts every node: the first node is counted before the loop condition, then each subsequent non-NULL node returned by iterate_collision_node__entry is counted, until NULL terminates the list. The implementation fulfills its semantic intent of counting entries.

Implementation Correctness:
Type compatibility — the local variable quantity_of__entries is Quantity__u32 (uint32_t), matching the return type exactly. The local pointer p_collision_node__entry is Collision_Node_Entry *, matching the member type of p_linked_list__collision_node_entries__tail. The call &p_collision_node__entry yields Collision_Node_Entry **, matching the parameter type of iterate_collision_node__entry. No implicit conversions or truncation occur.
No undefined behavior — no pointer arithmetic, no out-of-bounds access, no type punning. The NULL guard before the do-while (if !p_collision_node__entry return 0) guarantees that p_collision_node__entry is non-NULL on the first iteration. The while-condition checks the return value of iterate_collision_node__entry, which is only truthy when the pointer was advanced to a non-NULL node, guaranteeing p_collision_node__entry is non-NULL before each subsequent dereference inside iterate_collision_node__entry. The const parameter is respected — only the local pointer variable is advanced, never any struct member.
Validation — no NULL check is performed on p_collision_node itself. Passing NULL would cause a null dereference on the first member access. This is consistent with the codebase convention for pure query functions on collision nodes (e.g., get_p_hitbox_aabb_at__vector_3i32F4_from__collision_node likewise does not validate its Collision_Node parameter). The validation responsibility is on the caller, which is appropriate for a low-level traversal function.

Side Effects:
No side effects. The function only reads from the Collision_Node and its linked-list entries. All modifications (advancing p_collision_node__entry, incrementing quantity_of__entries) are to local stack variables. The const qualifier on the parameter confirms no mutation of the struct or its data.
