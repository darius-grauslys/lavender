# is_sort_data__heapifed

**File of origin:** `core/include/sort/sort_list/heap_sort.h`

## Semantic

Checks whether the heapification process for a `Sort_Data` is complete by testing if `index_of__heapification` equals `INDEX__UNKNOWN__SORT_NODE`. Returns `true` when heapification is finished, `false` when it is still in progress.

## Pre-conditions

1. `p_sort_data` must be a non-null pointer to a valid, initialized `Sort_Data` struct.
2. `index_of__heapification` holds a valid heap-node index (a value in `[0, length_of__sort_list - 1]`) while heapification is in progress, or `INDEX__UNKNOWN__SORT_NODE` when heapification is complete.

## Post-conditions

1. Returns `true` if `p_sort_data->index_of__heapification == INDEX__UNKNOWN__SORT_NODE`, indicating that the heap is fully heapified.
2. Returns `false` otherwise, indicating that heapification is still in progress.
3. No state is mutated; the function is a read-only query.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation correctly fulfills its semantic intent. The `index_of__heapification` field is used as a cursor that walks from the last interior node down to the root during heapification. When it reaches `INDEX__UNKNOWN__SORT_NODE`, heapification is complete. This is confirmed by the implementation in `core/source/sort/sort_list/heap_sort.c`:

- `request_resorting_of__heap` sets `index_of__heapification` to a valid interior-node index (not `INDEX__UNKNOWN__SORT_NODE`), signaling heapification should begin.
- `m_sort__heapify__sort_list` sets `index_of__heapification = INDEX__UNKNOWN__SORT_NODE` when the root (index 0) has been processed, marking completion.
- `is_heap__heapifed` delegates to this function to gate the sort phase in `m_sort__heap_sort__sort_list`.

The comparison is a straightforward equality check between two `Index__u16` values, which is exactly the semantic contract.

## Implementation Correctness

- **Type compatibility:** `p_sort_data->index_of__heapification` is of type `Index__u16` (i.e., `uint16_t`), and `INDEX__UNKNOWN__SORT_NODE` is defined as `(INDEX__UNKNOWN__u16 >> 1)` where `INDEX__UNKNOWN__u16` is `(uint16_t)(-1)`, so the right-hand side is also `uint16_t`. The comparison is type-compatible with no implicit conversions or truncation.
- **Undefined behavior:** No pointer arithmetic, no out-of-bounds access, no type punning. The function dereferences `p_sort_data` directly; no null-check is performed, which is consistent with the other accessor inline functions in this header (e.g., `is_heap__heapifed`, `get_index_of__heap_sort_from__sort_data`). Null validation is the caller's responsibility, matching the established pattern.
- **Validation:** No validation is performed within this function. For a simple inline accessor/query, this is appropriate; the caller is expected to provide a valid `Sort_Data` pointer, consistent with the codebase conventions for inline helpers.

## Side Effects

No side effects. The function is a pure query — it reads `p_sort_data->index_of__heapification` and returns a `bool` without modifying any state.
