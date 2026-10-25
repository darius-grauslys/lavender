# m_sort__heap_sort__sort_list

**File of origin:** `core/source/sort/sort_list/heap_sort.c`

## Semantic
Performs one step of the heap sort extraction phase: if the heap is heapified and not yet fully sorted, it swaps the root (max element) with the element at the current heap-sort index, decrements the heap-sort index boundary, and sifts down the root to restore the heap property. Returns `true` when sorting is complete, `false` otherwise.

## Pre-conditions
1. `p_sort_list` must be non-null.
2. `p_sort_list` must have been initialized via `initialize_sort_list_as__heap_sort` (or `initialize_sort_list_as__heap`), which sets up the heap structure and assigns `m_sort__heap_sort__sort_list` as the sort function pointer.
3. The sort list must have an even length (enforced by the initializer in debug builds).
4. The `f_sort_heuristic` function pointer must be set on `p_sort_list` for comparisons during sifting.

## Post-conditions
1. If the heap is not yet heapified (`is_heap__heapifed` returns false), the function should trigger heapification. **BUG: it recursively calls itself instead of `m_sort__heapify__sort_list`, causing infinite recursion / stack overflow.**
2. If the heap is already heapified and `is_heap_sort__sorted` returns true (heap-sort index <= 1), the function returns `true` without modifying state.
3. Otherwise, `index_of__heap_sort` is decremented by one, the root node is swapped with the node at the current `index_of__heap_sort` position, and `sift_down_in__heap` is called on the root to restore the heap property within the reduced heap boundary.
4. The function returns `false` to indicate sorting is incomplete.

## Correctness Verdict
**Incorrect**

## Semantic Alignment
The implementation does not fulfill the semantic intent. On line 286, when `is_heap__heapifed(p_sort_list)` returns false, the function calls itself recursively (`m_sort__heap_sort__sort_list(p_sort_list)`) instead of calling `m_sort__heapify__sort_list(p_sort_list)`. Since the state is not modified by the recursive call (it will again find the heap is not heapified and recurse again), this results in unbounded recursion and a stack overflow. The correct call should be `m_sort__heapify__sort_list(p_sort_list)`, which is the function responsible for performing sift-down operations to build the heap from an un-heapified state.

## Implementation Correctness
- **Type compatibility:** All parameter types match their expected types. No implicit conversions or truncation.
- **Undefined behavior:** The recursive self-call on line 286 (when the heap is not heapified) is the primary defect. It causes infinite recursion with no base case, leading to stack overflow. No other undefined behavior is present in the rest of the function.
- **Validation:** No explicit null check on `p_sort_list` is performed within this function, but this is consistent with the codebase pattern where validation is handled in debug builds by the initializer functions. The function relies on the caller to ensure proper initialization.
- **Off-by-one:** The heap sort logic itself (swap root with node at `index_of__heap_sort`, decrement, sift down) is correct for the extraction phase. The `is_heap_sort__sorted` check (`index_of__heap_sort <= 1`) is also correct.

## Side Effects
- Mutates `p_sort_list->sort_data.index_of__heap_sort` by decrementing it.
- Swaps the root sort node with the node at the current heap-sort index (via `swap_sort_nodes_in__heap`), which also updates `index_for__next_node` on the swapped nodes.
- Calls `sift_down_in__heap` on the root, which may perform additional swaps to restore the heap property.
- The recursive self-call (line 286) is an unintended side effect that causes infinite recursion.
