set_sort_node_as__allocated — core/include/sort/sort_list/sort_node.h

Sets the is_allocated bit-field of a Sort_Node to true.

Pre-conditions:
1. p_sort_node must be a non-null pointer to a writable Sort_Node object.

Post-conditions:
1. p_sort_node->is_allocated is set to true.

Correctness Verdict: Correct

Semantic Alignment:
The function name semantically conveys "mark this sort node as allocated." The implementation sets the is_allocated bit-field to true, which is exactly the intended behavior. This is a state-flag setter, not a Lavender-style initialization (which would reset a struct to its default/clean state for pool reuse). The implementation is semantically aligned with the function name.

Implementation Correctness:
Type compatibility — the literal `true` is a bool, and `is_allocated` is a `bool :1` bit-field; the assignment is type-correct with no implicit conversions or truncation.
No undefined behavior — no pointer arithmetic, no null dereference (assuming pre-conditions hold), no type punning, no out-of-bounds access.
No validation is needed — this is a low-level static inline setter. The caller is responsible for ensuring p_sort_node is valid.

Side Effects:
Mutates p_sort_node->is_allocated to true. No other observable side effects.
