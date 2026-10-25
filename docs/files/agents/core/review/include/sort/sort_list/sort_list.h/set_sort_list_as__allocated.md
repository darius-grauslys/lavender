set_sort_list_as__allocated — core/include/sort/sort_list/sort_list.h

Sets the `is_allocated` bitfield flag of a `Sort_List` to `true`, marking the sort list as in-use within the pool system.

Pre-conditions:
1. `p_sort_list` must be a non-null pointer to a writable `Sort_List` object.
2. In debug builds (when `NDEBUG` is not defined), a null `p_sort_list` triggers `debug_abort` and the function returns early without dereferencing.
3. In release builds (when `NDEBUG` is defined), no null check is performed; passing null results in undefined behavior (consistent with the engine's convention for low-level setters like `set_sort_node_as__allocated`).

Post-conditions:
1. `p_sort_list->is_allocated` is set to `true`.
2. No other fields of the `Sort_List` struct are modified.

Correctness Verdict: Correct

Semantic Alignment:
The function's intent is to mark a `Sort_List` as allocated by setting its `is_allocated` flag to `true`. The implementation does exactly this — it assigns `true` to the `is_allocated` bitfield and nothing more. There is no semantic drift.

Lavender-Specific Semantics:
This function is NOT an initialization function in the Lavender sense. Its name contains "allocated" but not "init", "initialize", or "reset". In Lavender, the `is_allocated` flag indicates that a struct is in use within the pool system — it does NOT signify RAII-style resource acquisition (e.g., `malloc`). This function merely sets a flag; it performs no memory allocation or resource setup. The companion function `initialize_sort_list_as__allocated` (in `sort_list.c`) is the Lavender-style initialization that sets default values and clears nodes, whereas `set_sort_list_as__allocated` is a simple flag setter that can be called independently to mark a sort list as allocated after it has been initialized.

Implementation Correctness:
Type compatibility — `is_allocated` is declared as `bool is_allocated :1` (a 1-bit bitfield of type `bool`). Assigning `true` (a `bool` literal) to it is a direct, exact type match with no implicit conversion or truncation.
Undefined behavior — in debug builds, the null pointer is checked before dereference. In release builds, no null check occurs, but this is consistent with the engine's established pattern for low-level inline setters (e.g., `set_sort_node_as__allocated` performs no null check in any build). No pointer arithmetic, type punning, or out-of-bounds access is present.
Validation — the debug-mode null check is appropriate defensive programming for a public inline setter. The release-mode omission is by design and matches the codebase convention.

Side Effects:
Mutates `p_sort_list->is_allocated`, setting it to `true`. No other state is modified. No other functions are called (other than `debug_abort` in debug builds on null input).
