# initialize_sort_list_as__empty — core/source/sort/sort_list/sort_list.c

Resets a Sort_List struct to its initial (empty/deallocated) conditions by clearing key fields to default values.

## Pre-conditions
1. `p_sort_list` must be a non-null pointer to a writable `Sort_List` object.

## Post-conditions
1. `p_sort_list->p_node_list` is set to `0` (null).
2. `p_sort_list->f_sort_heuristic` is set to `0` (null function pointer).
3. `p_sort_list->size_of__p_node_list` is set to `0`.
4. `p_sort_list->is_allocated` is set to `false`.

## Correctness Verdict
Incorrect

## Semantic Alignment
This function is intended to perform Lavender-style initialization (pool cleanup / reset to default state), not RAII-style resource setup. The intent is to clear the `Sort_List` struct so it can be safely returned to a free pool or reused.

However, the implementation does **not** fully clear the struct. The `Sort_List` struct contains the following fields:

1. `Sort_Node *p_node_list` — set ✓
2. `f_Sort_Heuristic f_sort_heuristic` — set ✓
3. `m_Sort m_sort` — **NOT set** ✗
4. `struct Sort_List_t *p_sort_list__next` — **NOT set** ✗
5. `Quantity__u32 size_of__p_node_list :31` — set ✓
6. `bool is_allocated :1` — set ✓
7. `Sort_Data sort_data` — **NOT set** ✗

The fields `m_sort`, `p_sort_list__next`, and `sort_data` are left uninitialized (containing stale data from any prior use of the struct). This violates the semantic intent of "initialization as empty/reset" — a properly initialized empty list should have all fields in a known default state.

Notably, the sibling function `initialize_sort_list_as__allocated` **does** set `p_sort_list->p_sort_list__next = 0`, but `initialize_sort_list_as__empty` omits this assignment.

## Implementation Correctness
- **Type compatibility**: All assignments use compatible types (null pointer constants for pointers, `0` for function pointer, `0` for bitfield, `false` for bool). No implicit conversions or truncation.
- **Undefined behavior**: No pointer arithmetic, null dereference, type punning, or out-of-bounds access.
- **Validation**: The function performs no null check on `p_sort_list`, which is consistent with the pattern used in `initialize_sort_list_as__allocated` (which also lacks a null check). This is acceptable for a low-level struct initialization function where the caller is responsible for providing a valid pointer. However, the missing field initialization is a correctness defect.

## Side Effects
The function mutates the `Sort_List` struct pointed to by `p_sort_list`, clearing four of its seven fields to default values. The fields `m_sort`, `p_sort_list__next`, and `sort_data` are left with their prior (potentially stale) values, which constitutes an incomplete reset.
