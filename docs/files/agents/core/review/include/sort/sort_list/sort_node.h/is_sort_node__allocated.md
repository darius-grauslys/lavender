is_sort_node__allocated — core/include/sort/sort_list/sort_node.h

Returns whether the given Sort_Node is marked as allocated.

Pre-conditions:
1. p_sort_node must be a non-null pointer to a valid, accessible Sort_Node object.

Post-conditions:
1. Returns the value of the is_allocated bitfield of the Sort_Node (true if allocated, false otherwise).

Correctness Verdict: Correct

Semantic Alignment:
The function correctly reads and returns the is_allocated bitfield member of the Sort_Node struct. This is a simple accessor; the implementation matches the semantic intent exactly.

Implementation Correctness:
Type compatibility — p_sort_node is Sort_Node *, and is_allocated is a bool :1 bitfield within Sort_Node. The return type is bool, which matches the bitfield type exactly. No implicit conversions or truncation.
No undefined behavior — no pointer arithmetic, no null dereference (null checking is the caller's responsibility for this low-level accessor), no type punning, no out-of-bounds access.
No validation is needed — this is a low-level inline accessor. The caller is responsible for ensuring p_sort_node is valid.

Side Effects:
No side effects — the function only reads the is_allocated field and returns its value.
