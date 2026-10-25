# get_next_p_sort_node_from__sort_list

**File of origin:** `core/source/sort/sort_list/sort_list.c`

## Semantic

Returns a pointer to the `Sort_Node` that follows `p_sort_node` in the sort list's logical linked-list ordering, as determined by the `index_for__next_node` field of `p_sort_node`. Returns `nullptr` if there is no next node (i.e., the index is out of bounds or the target node is not allocated).

## Pre-conditions

1. `p_sort_list` must be non-null. This is validated in debug builds (`#ifndef NDEBUG`).
2. `p_sort_node` must be non-null. This is validated in debug builds (`#ifndef NDEBUG`).
3. `p_sort_node` should be a valid pointer to a `Sort_Node` within `p_sort_list->p_node_list` (i.e., the caller is responsible for ensuring `p_sort_node` belongs to `p_sort_list`). This is not validated by the function.

## Post-conditions

1. If `p_sort_node->index_for__next_node` is a valid index (less than `get_length_of__sort_list(p_sort_list)`) and the node at that index is allocated (`is_allocated == true`), returns a pointer to that `Sort_Node`.
2. If `p_sort_node->index_for__next_node` is out of bounds (e.g., `INDEX__UNKNOWN__SORT_NODE` which is `0x7FFF`, far exceeding any valid list size of up to 512), returns `nullptr`.
3. If the node at `index_for__next_node` exists but is not allocated, returns `nullptr`.
4. No state of `p_sort_list` or `p_sort_node` is mutated.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation fulfills the documented semantic intent. The function's docstring states: "Returns a pointer to a Sort_Node that is determined by index_for__next_node" and "Returns nullptr if there is no next node." The implementation delegates to `get_p_sort_node_by__index_from__sort_list`, which:
- Bounds-checks the index against the list length.
- Checks the allocation status of the target node.
- Returns `nullptr` if either check fails.

The sentinel value `INDEX__UNKNOWN__SORT_NODE` (defined as `INDEX__UNKNOWN__u16 >> 1` = `0x7FFF`) is used by `initialize_sort_node_as__empty` to mark a node as having no next node. Since `0x7FFF` always exceeds any valid list length (maximum 512), `get_p_sort_node_by__index_from__sort_list` will always return `nullptr` for this sentinel, correctly signaling "no next node."

## Implementation Correctness

- **Type compatibility:** `index_for__next_node` is a 15-bit bitfield of type `Index__u16` (which is `uint16_t`). `get_p_sort_node_by__index_from__sort_list` accepts `Index__u16`. The types are compatible with no implicit conversion or truncation issues.
- **Undefined behavior:** No null dereference occurs — both `p_sort_list` and `p_sort_node` are checked in debug builds. No out-of-bounds array access occurs — `get_p_sort_node_by__index_from__sort_list` performs bounds checking. No type punning or pointer arithmetic issues.
- **Validation:** Null-pointer validation is performed in debug builds only, consistent with the codebase's pattern (e.g., `get_p_sort_node_by__index_from__sort_list`, `get_index_of__sort_node_in__sort_list`, etc.). In release builds, the function relies on the caller to provide valid pointers, which is the established convention in this codebase.

## Side Effects

No side effects. The function is pure: it reads `p_sort_node->index_for__next_node` and delegates to `get_p_sort_node_by__index_from__sort_list`, which only performs read-only access to `p_sort_list` and its node array. No state is mutated.
