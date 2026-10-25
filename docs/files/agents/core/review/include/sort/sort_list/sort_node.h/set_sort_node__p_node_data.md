set_sort_node__p_node_data — core/include/sort/sort_list/sort_node.h

Sets the p_node_data pointer field of a Sort_Node struct.

Pre-conditions:
1. p_sort_node must be a non-null pointer to a writable Sort_Node object.
2. p_node_data may be NULL or any valid pointer; type is void * with no range constraint.

Post-conditions:
1. p_sort_node->p_node_data is mutated to hold the value of p_node_data.
2. All other fields of p_sort_node (heuristic_value, index_for__next_node, is_allocated) remain unchanged.

Correctness Verdict: Correct

Semantic Alignment:
The implementation assigns p_node_data directly to p_sort_node->p_node_data. This matches the semantic intent of a simple setter. The Sort_Node struct has four fields; this setter modifies only p_node_data, which is appropriate for a targeted setter rather than a full initialization.

Implementation Correctness:
Type compatibility — the parameter type (void *) matches the target field type (void *) exactly. No implicit conversions or truncation.
No undefined behavior — no pointer arithmetic, no null dereference (assuming p_sort_node is non-null per pre-condition), no type punning, no out-of-bounds access.
No validation is needed — this is a low-level static inline setter. The caller is responsible for ensuring p_sort_node is valid.

Side Effects:
Mutates p_sort_node->p_node_data by setting it to p_node_data. No other side effects.
