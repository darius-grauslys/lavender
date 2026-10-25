# set_sort_list__sort_heuristic

**File of origin:** `core/include/sort/sort_list/sort_list.h` (lines 171-182)

## Semantic

Sets the sort heuristic function pointer (`f_sort_heuristic`) on a `Sort_List` struct, replacing whatever heuristic was previously stored.

## Pre-conditions

1. `p_sort_list` must be non-null. This is asserted via `debug_abort` in debug builds (`#ifndef NDEBUG`); in release builds the null check is elided (consistent with the rest of the inline setters in this header).
2. `f_sort_heuristic` should be a valid `f_Sort_Heuristic` function pointer (or `NULL` if the caller intends to clear the heuristic). No validation is performed on this parameter, which is acceptable for a simple setter consistent with the codebase pattern.

## Post-conditions

1. `p_sort_list->f_sort_heuristic` is set to the value of the `f_sort_heuristic` parameter.
2. No other fields of `Sort_List` are modified.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation faithfully fulfills its intent: it assigns the provided `f_Sort_Heuristic` function pointer to the `f_sort_heuristic` field of the `Sort_List` struct. The struct field is declared as `f_Sort_Heuristic f_sort_heuristic;` (see `defines.h`, line 1454), and the parameter type is `f_Sort_Heuristic` (see `defines.h`, line 1397), so the assignment is type-correct. The parameter name `f_sort_heuristic` shadows the struct member name, but since the member is accessed through `p_sort_list->f_sort_heuristic`, there is no ambiguity or conflict.

This is a setter, not an initialization/reset function, so the Lavender "initialization ≠ RAII" semantics do not apply here.

## Implementation Correctness

- **Type compatibility:** The parameter `f_sort_heuristic` is of type `f_Sort_Heuristic`, and the target field `p_sort_list->f_sort_heuristic` is also of type `f_Sort_Heuristic`. Types match exactly with no implicit conversions or truncation.
- **Undefined behavior:** No undefined behavior. The null-pointer dereference is guarded in debug builds. The assignment itself is a simple pointer-sized write to a valid struct field.
- **Validation:** The null check on `p_sort_list` is appropriate for debug builds and follows the established convention used by every other inline setter/accessor in this header (e.g., `set_sort_list_as__allocated`, `set_sort_list_as__deallocated`, `is_sort_list__allocated`, `get_p_node_list_from__sort_list`). No validation on `f_sort_heuristic` (including null) is consistent with the codebase's setter pattern.

## Side Effects

Mutates `p_sort_list->f_sort_heuristic` by overwriting it with the provided function pointer value. No other state is touched.
