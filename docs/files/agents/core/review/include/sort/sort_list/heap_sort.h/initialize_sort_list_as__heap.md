# initialize_sort_list_as__heap

**File of origin:** `core/source/sort/sort_list/heap_sort.c`

## Semantic

Initializes a `Sort_List` to function as a binary heap for heap sort. This is Lavender-style initialization (resetting to default/initial state), not RAII. It sets up the `index_for__next_node` field on each `Sort_Node` to point to its left child in a binary heap, configures the sort function to the heapify phase, and sets the heapification and heap-sort indices to their starting positions.

## Pre-conditions

1. `p_sort_list` must not be null.
2. `p_sort_list->p_node_list` must point to a valid, contiguous array of `Sort_Node` elements.
3. `p_sort_list->f_sort_heuristic` must be set (non-null) if sorting will be performed.
4. All `Sort_Node` elements in `p_node_list` must be allocated (i.e., `is_allocated` must be set to true for each node) so that `get_p_sort_node_by__index_from__sort_list` returns non-null pointers.

## Post-conditions

1. Each `Sort_Node` in the list has its `index_for__next_node` field set to the index of its left child (`(index << 1) + 1`), or `INDEX__UNKNOWN__SORT_NODE` if the left child index is out of bounds.
2. `p_sort_list->m_sort` is set to `m_sort__heapify__sort_list`, indicating the sort list is in the heapify phase.
3. `p_sort_list->sort_data.index_of__heapification` is set to the parent index of the last node, which is the standard starting point for bottom-up heapify.
4. `p_sort_list->sort_data.index_of__heap_sort` is set to `get_length_of__sort_list(p_sort_list)`, the starting point for the heap sort extraction phase.

## Correctness Verdict

**Incorrect**

## Semantic Alignment

The function's intent is to initialize a `Sort_List` as a binary heap. The core logic is correct: it iterates over all nodes, sets each node's `index_for__next_node` to its left child index (or `INDEX__UNKNOWN__SORT_NODE` if out of bounds), sets the sort function to the heapify phase, and initializes the heapification and heap-sort indices.

However, the function contains a **debug-only check that rejects odd-length sort lists**:

```c
if (get_length_of__sort_list(p_sort_list) & 0b1) {
    debug_abort("initialize_sort_list_as__heap_sort, p_sort_list has odd length.");
    return;
}
```

This is a **bug**. Heap sort works correctly with any number of elements, including odd lengths. The `update_heap_sort_node__index_for__next_node` function properly handles out-of-bounds child indices by clamping to `INDEX__UNKNOWN__SORT_NODE`, and `request_resorting_of__heap` correctly computes the heapify starting index `(length - 2) >> 1` for any length. There is no algorithmic requirement for the list length to be even. This check unnecessarily restricts the function to even-length lists, causing it to abort on valid inputs in debug builds.

## Implementation Correctness

1. **Odd length check (bug):** The `& 0b1` check rejects odd-length lists. This is incorrect — heap sort does not require an even number of elements. The check should be removed entirely.

2. **Null pointer dereference risk:** The function calls `get_p_sort_node_by__index_from__sort_list` to obtain each node pointer, then passes it directly to `update_heap_sort_node__index_for__next_node` without checking for null. `get_p_sort_node_by__index_from__sort_list` returns null if `is_sort_node__allocated` returns false. If any node is not marked as allocated, `update_heap_sort_node__index_for__next_node` will dereference a null pointer (both in the pointer arithmetic `p_sort_node - p_sort_list->p_node_list` and in the field assignment `p_sort_node->index_for__next_node = ...`). A debug assertion checking `p_sort_node != null` should be added before the call.

3. **Debug message mismatch:** The debug abort message says "initialize_sort_list_as__heap_sort" but the function is named "initialize_sort_list_as__heap". This is a minor cosmetic issue in the debug message.

4. **Type compatibility:** The `index_for__next_node` field is a 15-bit bitfield. The computation `(index_of__sort_node << 1) + 1` fits within 15 bits for all practical sort list sizes (max 511 nodes, yielding a maximum left-child index of 1023). No truncation occurs.

5. **Pointer arithmetic:** The computation `p_sort_node - p_sort_list->p_node_list` correctly determines the node's index within the contiguous array, assuming `p_sort_node` points to an element within `p_node_list`.

## Side Effects

- Mutates `index_for__next_node` on every `Sort_Node` in the list.
- Sets `p_sort_list->m_sort` to `m_sort__heapify__sort_list`.
- Sets `p_sort_list->sort_data.index_of__heapification` to the parent index of the last node.
- Sets `p_sort_list->sort_data.index_of__heap_sort` to the length of the sort list.
- No allocation or deallocation occurs.
