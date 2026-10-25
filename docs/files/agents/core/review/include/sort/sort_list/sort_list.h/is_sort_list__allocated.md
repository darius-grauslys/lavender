# Function Review: is_sort_list__allocated

## File of Origin
`core/include/sort/sort_list/sort_list.h`

## Semantic
A pure accessor function that queries whether a `Sort_List` has been marked as allocated by returning the value of its `is_allocated` bitfield.

## Pre-conditions
1. `p_sort_list` must be a non-null pointer to a valid `Sort_List` struct. In debug builds (`NDEBUG` not defined), a null `p_sort_list` triggers `debug_abort` and returns `false`. In release builds, passing null results in undefined behavior (dereferencing a null pointer).

## Post-conditions
1. Returns `true` if `p_sort_list->is_allocated` is set to `true`, indicating the sort list is marked as allocated.
2. Returns `false` if `p_sort_list->is_allocated` is set to `false`, indicating the sort list is marked as deallocated.
3. The function does not modify any state of the `Sort_List` struct or any other observable state.

## Correctness Verdict
**Correct**

## Semantic Alignment
The function fulfills its semantic intent: it is a simple query that returns the `is_allocated` field of the `Sort_List` struct. The `is_allocated` field is declared as `bool is_allocated :1` in the `Sort_List_t` struct (defined in `core/include/defines.h`, lines 1452–1461). The function's return type is `bool`, which matches the field type exactly — no implicit conversion, truncation, or type punning occurs. The implementation directly returns the field value, which is the correct behavior for an accessor.

## Implementation Correctness
- **Type compatibility**: The return type `bool` matches the field type `bool is_allocated :1`. The `bool` type is provided via `<stdbool.h>` (included transitively through `defines_weak.h`). No implicit conversions or truncation occur.
- **Undefined behavior**: In debug builds, a null `p_sort_list` is checked and aborts before dereference. In release builds, no null check is performed — this is consistent with the codebase's pattern where debug builds perform validation and release builds rely on caller responsibility. For example, `is_sort_node__allocated` in `sort_node.h` performs no null check at all, even in debug builds.
- **Validation**: The debug-only null check is appropriate for this type of accessor function and is consistent with the patterns used by other accessor functions in the same header (e.g., `get_length_of__sort_list`, `run_sort__once`, `set_sort_list_as__allocated`).
- **Return value on abort path**: In the debug null-check path, `return 0;` is used instead of `return false;`. While `0` is implicitly convertible to `false` in C, this is a minor style inconsistency, not a correctness issue. The `debug_abort` call is expected to terminate the program, so this return is effectively unreachable.

## Side Effects
No side effects. This is a pure read-only query function. It does not modify the `Sort_List` struct, does not call any mutating operations, and does not produce any observable side effects beyond returning a boolean value.
