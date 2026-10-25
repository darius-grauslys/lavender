is_collision_node__allocated — core/include/collisions/collision_node.h, lines 55-60

## Semantic

Queries whether a `Collision_Node` is currently in an allocated (live) state by checking that its serialization header's UUID does not equal the deallocated sentinel `IDENTIFIER__UNKNOWN__u64`. Returns the logical inverse of "is this struct deallocated."

## Pre-conditions

1. `p_collision_node` is expected to be a non-null pointer to a valid `Collision_Node` object.
2. No other pre-conditions; the function does not inspect `p_linked_list__collision_node_entries__tail` or any other field.

## Post-conditions

1. Returns `true` if `p_collision_node->_serialization_header.uuid != IDENTIFIER__UNKNOWN__u64` (the node is allocated).
2. Returns `false` if `p_collision_node->_serialization_header.uuid == IDENTIFIER__UNKNOWN__u64` (the node is deallocated).
3. No mutation of the `Collision_Node` or any other state occurs.

## Correctness Verdict

Incorrect

## Semantic Alignment

The implementation fulfills the semantic intent: it correctly returns the negation of the deallocated status, delegating to `is_serialized_struct__deallocated__uuid_64`. The Lavender engine's allocation model determines "allocated" by checking whether the UUID is the `IDENTIFIER__UNKNOWN__u64` sentinel. The function correctly returns `true` for valid UUIDs and `false` for the sentinel.

## Implementation Correctness

**Null dereference — missing null guard on `p_collision_node`.** The function dereferences `p_collision_node` unconditionally via `&p_collision_node->_serialization_header` before any null check is possible. If `p_collision_node` is `NULL`, this is undefined behavior (null pointer dereference). Compare with the analogous `is_global_space__allocated` (core/include/world/global_space.h, lines 46-53), which guards with `p_global_space &&` before dereferencing. The codebase already has a null-safe pattern: callers that need null safety use the `IS_DEALLOCATED_P__u64` macro (which checks `!serialized_header` before calling `is_serialized_struct__deallocated__uuid_64`). The `is_collision_node__allocated` function should follow the same pattern by adding `p_collision_node &&` (or equivalent) before the dereference.

**Dead null check in callee.** The callee `is_serialized_struct__deallocated__uuid_64` (serialization_header.h, lines 173-179) contains `return !p_serialization_header || ...`. However, the argument passed is `&p_collision_node->_serialization_header` — the address-of a struct member, which is always non-null when `p_collision_node` is non-null. The `!p_serialization_header` check is therefore dead code in this call path: it can never be true when reached. The only protection against a null `p_collision_node` must reside in `is_collision_node__allocated` itself, which currently lacks it.

**Type compatibility — correct.** `p_collision_node->_serialization_header` is of type `Serialization_Header__UUID_64`, and `&p_collision_node->_serialization_header` yields `Serialization_Header__UUID_64 *`, which matches the parameter type of `is_serialized_struct__deallocated__uuid_64` exactly. No implicit conversions occur.

**No other UB.** No pointer arithmetic, no type punning, no out-of-bounds access. The only issue is the missing null guard described above.

**Validation scope.** Given that the sibling function `is_global_space__allocated` performs its own null check, `is_collision_node__allocated` should be equally defensive. The current absence of a guard is inconsistent with established patterns in the same codebase.

## Side Effects

No side effects. The function is a pure query: it reads `p_collision_node->_serialization_header.uuid` and returns a boolean. No state is mutated, no I/O occurs, no global state is touched.
