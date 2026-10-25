# set_sort_node_as__deallocated

**File of origin:** `core/include/sort/sort_list/sort_node.h`

## Semantic
Sets a `Sort_Node`'s allocation flag to `false`, marking the node as deallocated (i.e., available for reuse in the sort node pool).

## Pre-conditions
1. `p_sort_node` must be a non-null pointer to a valid `Sort_Node` struct instance.

## Post-conditions
1. `p_sort_node->is_allocated` is set to `false`.
2. All other fields of `p_sort_node` (e.g., `p_node_data`, `heuristic_value`, `index_for__next_node`) remain unchanged.

## Correctness Verdict
Correct

## Semantic Alignment
The implementation fully fulfills the semantic intent. The function name `set_sort_node_as__deallocated` clearly conveys that the node's allocation status is being set to "deallocated." The body sets `p_sort_node->is_allocated = false`, which is exactly the intended behavior. This is a simple setter consistent with the companion function `set_sort_node_as__allocated` (which sets `is_allocated = true`).

## Implementation Correctness
- **Type compatibility:** `is_allocated` is declared as `bool is_allocated :1` (a 1-bit bitfield of type `bool`). The literal `false` is of type `bool`. Types match exactly with no implicit conversion or truncation.
- **Undefined behavior:** No undefined behavior is introduced. The function dereferences `p_sort_node` to assign to a struct member; null-checking is the caller's responsibility (consistent with the other `set_sort_node_*` functions in this header).
- **Validation:** No validation is performed, which is appropriate for this function's role as a lightweight `static inline` setter. Validation is the caller's responsibility, consistent with the pattern used across all sibling functions (`set_sort_node_as__allocated`, `set_sort_node__p_node_data`, `is_sort_node__allocated`).

## Side Effects
- Mutates `p_sort_node->is_allocated` to `false`.
- No other fields are modified.
- No external side effects (no I/O, no memory allocation/deallocation).

## Lavender-Specific Semantics
This function is a **setter**, not an initialization function. It does not perform Lavender-style initialization (cleaning a struct to its initial conditions for pool reuse). However, it is used in conjunction with initialization functions in practice:

- In `initialize_sort_list_manager` (sort_list_manager.c), `set_sort_node_as__deallocated` is called after `initialize_sort_node_as__empty` to mark pool nodes as available.
- In `release_sort_list_in__sort_list_manager`, it is used to mark a sort list as deallocated after its nodes are released.

The function itself only toggles the `is_allocated` flag; it does not reset or clear the struct's data fields. Full cleanup of a node for pool reuse is performed by `initialize_sort_node_as__empty` (which resets `heuristic_value` and `index_for__next_node`), while this function solely updates the allocation status bit.
