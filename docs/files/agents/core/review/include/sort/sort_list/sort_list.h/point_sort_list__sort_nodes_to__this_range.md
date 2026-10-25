# point_sort_list__sort_nodes_to__this_range

**File of origin:** `core/source/sort/sort_list/sort_list.c`

## Semantic

Points every `Sort_Node` in the sort list's internal node array to sequential offsets within a contiguous data range, so that node `i` references `p_node_data__range + (i * size_of__stride_in__bytes)`. The `index_for__next_node` linking field is not modified — only `p_node_data` is set.

## Pre-conditions

1. `p_sort_list` must be a non-null pointer to a valid, allocated `Sort_List` (i.e., `is_allocated == true` and `p_node_list` must point to a valid contiguous array of `Sort_Node` elements).
2. `p_node_data__range` must point to a contiguous block of memory large enough to hold `get_length_of__sort_list(p_sort_list)` elements each of `size_of__stride_in__bytes` bytes.
3. `size_of__stride_in__bytes` must be the correct stride between consecutive elements in `p_node_data__range`.
4. The `Sort_List` must have been initialized via `initialize_sort_list_as__allocated` (not `initialize_sort_list_as__empty`), so that `p_node_list` is non-null and `size_of__p_node_list` is set.

## Post-conditions

1. For every index `i` in `[0, min(SORT_NODE__MAXIMUM_QUANTITY_OF, get_length_of__sort_list(p_sort_list)))`, `p_sort_list->p_node_list[i].p_node_data` is set to `p_node_data__range + (i * size_of__stride_in__bytes)`.
2. No other fields of `Sort_List` or `Sort_Node` are modified.
3. `p_node_data__range` is not modified; the function only reads from it via pointer arithmetic.

## Correctness Verdict

**Incorrect**

## Semantic Alignment

The documentation states: "Will have the entire sort list point to the given range in sequential order of nodes, regardless of each node's index_for__next_node." The intent is to set `p_node_data` on **all** nodes in the sort list's node array.

However, the implementation calls `get_p_sort_node_by__index_from__sort_list`, which returns `0` (null) for any node whose `is_allocated` bit is false. After `initialize_sort_list_as__allocated` is called, `initialize_sort_node_as__empty` is invoked on each node, which does **not** set `is_allocated` to `true` (nor does it explicitly set it to `false`). In practice, nodes will have `is_allocated == false` after this initialization (from zero-initialized or stale memory), meaning `get_p_sort_node_by__index_from__sort_list` returns null for every node.

The function then dereferences this null pointer on the very first iteration:
```c
p_sort_node->p_node_data = p_node_data__range_as__p_uint8_t;
```
This is undefined behavior (null pointer dereference) and does not fulfill the documented semantic intent of pointing the "entire sort list" to the data range.

The correct implementation should use direct array access instead of `get_p_sort_node_by__index_from__sort_list`:
```c
p_sort_list->p_node_list[index_of__sort_node].p_node_data =
    p_node_data__range_as__p_uint8_t;
```

## Implementation Correctness

**Critical Bug — Null Pointer Dereference:**
`get_p_sort_node_by__index_from__sort_list` returns `0` when `is_sort_node__allocated(p_sort_node)` is false. The function does not check for this null return before dereferencing `p_sort_node`, causing undefined behavior. This will crash on the first unallocated node encountered.

**No null check for `p_sort_list`:**
The function does not validate that `p_sort_list` is non-null before calling `get_length_of__sort_list(p_sort_list)`. While `get_length_of__sort_list` has a debug-mode null check, in release builds (`NDEBUG` defined), passing a null `p_sort_list` would result in undefined behavior.

**Loop bound redundancy:**
The loop condition checks both `index_of__sort_node < SORT_NODE__MAXIMUM_QUANTITY_OF` (512) and `index_of__sort_node < get_length_of__sort_list(p_sort_list)`. The first check is redundant if `size_of__p_node_list` is always ≤ 512, but serves as a safety bound. This is not a bug, just a defensive measure.

**Type compatibility:** `Index__u16` is used for the loop counter, which is sufficient since both `SORT_NODE__MAXIMUM_QUANTITY_OF` (512) and `size_of__p_node_list` (31-bit field) are well within the range of `uint16_t`. No truncation or implicit conversion issues.

## Side Effects

1. Mutates `p_node_data` on every `Sort_Node` in `p_sort_list->p_node_list` (up to `min(SORT_NODE__MAXIMUM_QUANTITY_OF, size_of__p_node_list)` nodes).
2. Does not modify `p_sort_list` struct fields (size, heuristic, flags, etc.).
3. Does not modify `index_for__next_node` or `heuristic_value` on any node.
4. Does not allocate, deallocate, or free any memory.
