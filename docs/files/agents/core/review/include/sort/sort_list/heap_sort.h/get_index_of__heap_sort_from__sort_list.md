# Function Review: get_index_of__heap_sort_from__sort_list

**File of origin:** `core/include/sort/sort_list/heap_sort.h`

## Semantic

Retrieves the current heap sort index from a `Sort_List`'s embedded `Sort_Data`, indicating the progress of the heap sort algorithm. This is a simple accessor that delegates to `get_index_of__heap_sort_from__sort_data`.

## Pre-conditions

1. `p_sort_list` must be non-null. The function dereferences `p_sort_list->sort_data` without a null check; passing null would result in undefined behavior.
2. `p_sort_list` must point to a valid, properly initialized `Sort_List` structure.

## Post-conditions

1. Returns the value of the `index_of__heap_sort` field (of type `Index__u16`) from the `Sort_Data` union embedded in `p_sort_list->sort_data`.
2. The function does not modify `p_sort_list` or any of its members. It is a read-only accessor.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation correctly retrieves the `index_of__heap_sort` field by delegating to `get_index_of__heap_sort_from__sort_data`, passing the address of `p_sort_list->sort_data`. This is consistent with the codebase's pattern of providing accessor functions at both the `Sort_Data` and `Sort_List` abstraction levels. The return type (`Index__u16`) matches the type of the `index_of__heap_sort` field in `Sort_Data`.

## Implementation Correctness

- **Type compatibility:** The return type `Index__u16` matches the type of `p_sort_data->index_of__heap_sort` exactly. No implicit conversions or truncation occur.
- **Undefined behavior:** No pointer arithmetic, type punning, or out-of-bounds access. The only concern is the lack of a null check on `p_sort_list`, but this is consistent with the rest of the codebase — other inline accessors (e.g., `is_sort_data__heapifed`, `is_heap__heapifed`) also do not perform null checks. Null validation is the caller's responsibility.
- **Validation:** As a simple pure accessor, no validation is appropriate within this function. The precondition that `p_sort_list` is valid is the caller's responsibility, consistent with the codebase pattern.

## Side Effects

No side effects. This is a pure read accessor function.
