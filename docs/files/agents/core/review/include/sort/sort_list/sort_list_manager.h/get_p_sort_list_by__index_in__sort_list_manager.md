# get_p_sort_list_by__index_in__sort_list_manager

**File of origin:** `core/include/sort/sort_list/sort_list_manager.h`

---

## Semantic

Returns a pointer to a `Sort_List` element from the `sort_lists` fixed-size array within a `Sort_List_Manager`, selected by the given index.

---

## Pre-conditions

1. `p_sort_list_manager` must be non-null. Dereferencing a null pointer would result in undefined behavior.
2. `index_of__sort_list` must be in the range `[0, SORT_LIST__MAXIMUM_QUANTITY_OF)` (i.e., 0 to 63, since `SORT_LIST__MAXIMUM_QUANTITY_OF` is defined as 64). An out-of-range index causes out-of-bounds array access.
3. The `Sort_List_Manager` must be in a valid state (typically initialized via `initialize_sort_list_manager(...)`). While the function does not strictly require initialization to return a pointer, the caller is expected to have initialized the manager.

---

## Post-conditions

1. Returns a valid, non-null pointer to the `Sort_List` at position `index_of__sort_list` within `p_sort_list_manager->sort_lists`.
2. The returned pointer is stable as long as the `Sort_List_Manager` is not moved or destroyed.
3. The function does not modify any state of the `Sort_List_Manager` or the referenced `Sort_List`.

---

## Correctness Verdict

**Correct**

---

## Semantic Alignment

The implementation faithfully fulfills the semantic intent. It performs a direct array indexing operation on `p_sort_list_manager->sort_lists[index_of__sort_list]` and returns the address of the resulting element. The return type `Sort_List *` matches the element type of the `sort_lists` array. There is no semantic drift.

---

## Implementation Correctness

- **Type compatibility:** The parameter `index_of__sort_list` is of type `Index__u8` (i.e., `uint8_t`), which is an unsigned 8-bit integer. The `sort_lists` array is indexed with this value. Since `SORT_LIST__MAXIMUM_QUANTITY_OF` is 64 (which fits within the 0–255 range of `uint8_t`), the index type is sufficient to address all valid array elements. No implicit conversion or truncation occurs. ✓
- **Undefined behavior:** No null dereference occurs within the function body itself (the null check is the caller's responsibility for this inline accessor). No out-of-bounds access occurs if the caller respects the index bounds (0–63). No type punning or broken pointer arithmetic is present. ✓
- **Validation:** No bounds checking is performed inside the function. This is appropriate for a `static inline` accessor function — validation is the caller's responsibility. This is consistent with the similar `get_p_sort_node_by__index_in__sort_list_manager` function, which also performs no validation. The primary caller, `get_next_available__p_sort_list_in__sort_list_manager`, ensures the index is bounded by `SORT_LIST__MAXIMUM_QUANTITY_OF`. ✓

---

## Side Effects

No side effects. The function is a pure accessor: it reads the `sort_lists` array from the `Sort_List_Manager` and returns a pointer to the requested element. It does not modify any state.
