# Function Review: run_sort

## 1. Header
- **Function name**: run_sort
- **File of origin**: core/source/sort/sort_list/sort_list.c, lines 169-182

## 2. Semantic
Repeatedly invokes the sort list's `m_sort` function pointer until it returns `true`, indicating the sort is complete. This drives the incremental sort algorithm to completion in a blocking loop.

## 3. Pre-conditions
1. `p_sort_list` must be non-null (checked in debug builds via `NDEBUG` guard).
2. `p_sort_list->m_sort` must be non-null (checked in debug builds).
3. The `Sort_List` must have been initialized with a valid `p_node_list` and `size_of__p_node_list` before calling this function, so that `m_sort` operates on valid data.
4. The `m_sort` function pointer must implement a terminating sort algorithm — i.e., it must eventually return `true` to signal completion. If it never returns `true`, this function will loop indefinitely.

## 4. Post-conditions
1. The sort list's nodes are fully sorted according to the sort heuristic associated with the `m_sort` function.
2. The function returns `void` (no return value).
3. The internal `Sort_Data` state (e.g., heapification indices for heapsort) is left in the state set by the final `m_sort` call.

## 5. Correctness Verdict
**Correct**

## 6. Semantic Alignment
The implementation aligns with the semantic intent. The `m_Sort` function pointer type is documented as: "Should be implemented to run just one step of the sort algorithm per invocation. Return true if fully sorted, otherwise false." The `run_sort` function correctly loops with `while (!p_sort_list->m_sort(p_sort_list)) {}`, which continues calling `m_sort` until it returns `true` (sorted). When `m_sort` returns `true`, `!true` evaluates to `false`, terminating the loop. This is consistent with the `run_sort_with__this_many_steps` function, which also treats a `true` return as "sorted" and breaks out of its loop.

## 7. Implementation Correctness
- **Type compatibility**: `p_sort_list->m_sort` is of type `m_Sort`, defined as `bool (*)(Sort_List *)`. The argument `p_sort_list` is of type `Sort_List *`, matching exactly. The return type `bool` is correctly negated with `!`. No implicit conversions or truncation.
- **Undefined behavior**: No null dereference in release builds is a concern (null checks are debug-only), but this is consistent with the codebase's established pattern. No pointer arithmetic, no type punning, no out-of-bounds access within this function itself. The loop body delegates all work to `m_sort`, which is responsible for its own bounds safety.
- **Validation**: Null checks for `p_sort_list` and `p_sort_list->m_sort` are present in debug builds (`NDEBUG` not defined), which is appropriate for this function's role as a high-level sort driver. In release builds, the caller is responsible for ensuring valid inputs, consistent with the rest of the codebase.

## 8. Side Effects
- **Mutates** the `Sort_List` and its associated `Sort_Node` array by repeatedly invoking `m_sort`, which performs sorting operations (e.g., swapping node data pointers or heuristic values) until the list is sorted.
- Does not allocate or free memory.
- Does not modify `p_sort_list->f_sort_heuristic` or `p_sort_list->is_allocated`.
- No I/O or other observable side effects beyond the sort state of the list.
