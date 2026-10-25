set_sort_list_as__deallocated — core/include/sort/sort_list/sort_list.h

Sets the `is_allocated` flag of a Sort_List to false, marking it as deallocated.

Pre-conditions:
1. `p_sort_list` must be a non-null pointer to a writable Sort_List object.
2. In debug builds (when NDEBUG is not defined), a null `p_sort_list` will trigger a debug abort and the function will return early without modifying any state.

Post-conditions:
1. `p_sort_list->is_allocated` is set to `false`.
2. No other fields of the Sort_List struct are modified by this function.

Correctness Verdict: Correct

Semantic Alignment:
This function performs a simple flag assignment, consistent with its name and the companion function `set_sort_list_as__allocated` (which sets the same flag to `true`). It is a flag setter, not a full struct initialization. The function correctly sets the `is_allocated` bit-field to `false`, which semantically indicates the Sort_List is no longer in an allocated state. This aligns with the Lavender engine's pattern where "deallocated" means the flag is cleared so the list can be returned to a free pool or reused.

Implementation Correctness:
Type compatibility — `p_sort_list->is_allocated` is a 1-bit bit-field of type `bool`, and `false` is the correct boolean literal for this field. No implicit conversions or truncation.
Undefined behavior — No pointer arithmetic, no type punning, no out-of-bounds access. The null check in debug builds prevents null dereference. In release builds (NDEBUG defined), the null check is omitted for performance, which is consistent with the codebase pattern but relies on the caller to provide a valid pointer.
Validation — The null check is appropriate for debug builds. In release builds, validation is omitted, which is the established pattern in this codebase for inline functions. The caller is responsible for ensuring `p_sort_list` is valid.

Side Effects:
Mutates `p_sort_list->is_allocated` to `false`. No other struct fields are modified. No other memory or global state is affected.
