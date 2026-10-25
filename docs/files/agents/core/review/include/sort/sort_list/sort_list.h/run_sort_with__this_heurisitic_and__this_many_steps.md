## Function Review: run_sort_with__this_heurisitic_and__this_many_steps

**File of origin:** `core/source/sort/sort_list/sort_list.c`

### Semantic
Temporarily swaps the sort heuristic on a `Sort_List`, invokes a bounded-step sort using the new heuristic, then restores the original heuristic. Returns whether the list is fully sorted after the given number of steps.

### Pre-conditions
1. `p_sort_list` must be non-null. (Checked in debug builds via `NDEBUG` guard; returns `true` and aborts if null.)
2. `p_sort_list->m_sort` must be non-null. (Checked in debug builds; returns `true` and aborts if null.)
3. `f_this_sort_heuristic` is expected to be a valid function pointer (or `NULL` if the sort implementation does not use it). No validation is performed — this is the caller's responsibility.
4. `quantity_of__steps` is forwarded directly to `run_sort_with__this_many_steps`; a value of 0 means no sort steps execute and the function returns `false`.
5. `p_sort_list->f_sort_heuristic` is assumed to hold a meaningful value that should be preserved across the call.

### Post-conditions
1. `p_sort_list->f_sort_heuristic` is restored to its original value (`f_previous_heuristic`) after the sort completes, regardless of the sort result.
2. The sort list's internal node ordering may be modified by the `m_sort` callback (via `run_sort_with__this_many_steps`), as that is the intended behavior of the sort operation.
3. Returns `true` if the list is fully sorted after at most `quantity_of__steps` iterations; returns `false` otherwise.

### Correctness Verdict
**Correct**

### Semantic Alignment
The implementation faithfully fulfills its semantic intent: it saves the existing heuristic, temporarily installs the caller-provided heuristic, delegates to `run_sort_with__this_many_steps` for the bounded sort, and restores the original heuristic before returning. The save/restore pattern is correctly ordered and no state leaks occur.

### Implementation Correctness
- **Type compatibility:** All types match exactly. `f_Sort_Heuristic` is `Signed_Quantity__i32 (*)(Sort_Node*, Sort_Node*)`, and `p_sort_list->f_sort_heuristic` is the same type. `Quantity__u32` matches the parameter type in `run_sort_with__this_many_steps`. No implicit conversions or truncation.
- **Undefined behavior:** No null pointer dereference, no out-of-bounds access, no type punning. The debug guards check `p_sort_list` and `p_sort_list->m_sort` before use.
- **Validation:** Debug-only null checks are appropriate for this function's role (matching the pattern used by `run_sort_with__this_many_steps` and `run_sort`). The function does not validate `f_this_sort_heuristic` for null, but this is consistent with the engine's convention where the caller is responsible for providing valid function pointers.
- **Minor issue:** The debug error messages incorrectly reference `"run_sort"` instead of `"run_sort_with__this_heurisitic_and__this_many_steps"`. This is a copy-paste artifact in the `debug_abort` string literals and does not affect runtime correctness, but should be corrected for diagnostic clarity.

### Side Effects
- Temporarily mutates `p_sort_list->f_sort_heuristic` (sets it to `f_this_sort_heuristic`), but restores the original value before returning.
- May mutate `p_sort_list` internal state (node ordering, `sort_data`) through the `m_sort` callback invoked by `run_sort_with__this_many_steps`.
- Returns a `bool` indicating whether the sort completed within the step budget.
