# release_p_ui_manager_from__ui_context

**File of origin:** `core/source/ui/ui_context.c`

## Semantic

Releases (deallocates) a `UI_Manager` identified by UUID from the `UI_Context`'s contiguous pool of UI managers. This involves releasing all child `UI_Element`s, freeing the UI manager's dynamically allocated member arrays, and marking the `UI_Manager` struct itself as deallocated (Lavender-style pool cleanup, not RAII).

## Pre-conditions

1. `p_game` must be non-null. (Validated only in debug builds via `#ifndef NDEBUG`.)
2. `uuid_of__ui_manager__u32` must be a valid (non-`IDENTIFIER__UNKNOWN__u32`) UUID identifying a previously allocated `UI_Manager` in the `UI_Context`'s `ui_managers` array.
3. The `UI_Manager` with the given UUID must be paired with a `Graphics_Window` that shares the same UUID. If no such `Graphics_Window` is found, the function aborts (see Post-condition 5).

## Post-conditions

1. If `p_game` is null (debug builds only), the function logs an error and returns early without performing any work.
2. If no `UI_Manager` with the given UUID is found in the `UI_Context`'s pool, the function logs an error and returns early without performing any work.
3. All `UI_Element`s owned by the `UI_Manager` are released via `release_all__ui_elements_from__ui_manager`, which iteratively calls `release__ui_element_from__ui_manager` until the manager is empty.
4. The `UI_Manager`'s dynamically allocated member arrays (`pM_ptr_array_of__ui_elements` and `pM_ui_element_pool`) are freed via `release_ui_manager__members`, and the `UI_Manager` struct (excluding its `Serialization_Header`) is zeroed via `initialize_ui_manager`. The `pM_ui_element_pool` and `pM_ptr_array_of__ui_elements` pointers are set to 0 (dangling-pointer-safe).
5. If the `UI_Manager` is not paired with a `Graphics_Window` sharing the same UUID, the function calls `debug_abort` (halting execution in debug builds) because a memory leak may be occurring. In non-debug builds, `debug_abort` behavior depends on the platform implementation.
6. The `UI_Manager` struct's `Serialization_Header.uuid` is set to `IDENTIFIER__UNKNOWN__u32` via `DEALLOCATE_P`, marking the struct as deallocated so it can be reclaimed from the pool by a subsequent `allocate_p_ui_manager_from__ui_context` call.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation fulfills the semantic intent. The function properly performs a multi-step teardown of a `UI_Manager`:

- **Lavender-style deallocation (not RAII):** The function does not call `free()` on the `UI_Manager` struct itself. Instead, `DEALLOCATE_P` resets the `Serialization_Header.uuid` to `IDENTIFIER__UNKNOWN__u32`, marking the struct as deallocated within the contiguous pool. This is consistent with Lavender's convention where "initialization"/"deallocation" means cleaning up to a default state for pool reuse, not freeing the struct's memory. The `UI_Context.ui_managers` array is a fixed-size contiguous array allocated as part of `UI_Context` (which is itself part of `Gfx_Context` inside `Game`), so the `UI_Manager` structs are not individually heap-allocated.

- **Correct ordering of teardown:** UI elements are released first (while the graphics window and UI manager members are still valid), then the UI manager's dynamically allocated member arrays are freed, then the struct itself is marked as deallocated. This ordering is correct because `release_all__ui_elements_from__ui_manager` requires `p_game`, `p_graphics_window`, and `p_ui_manager` to all be valid.

- **Member release consistency:** `release_ui_manager__members` frees `pM_ptr_array_of__ui_elements` and `pM_ui_element_pool` (both heap-allocated in `allocate_ui_manager__members`), then calls `initialize_ui_manager` which memsets the struct body (after the `Serialization_Header`) to 0. This prevents dangling pointers and resets the struct to a clean state before `DEALLOCATE_P` marks the header as deallocated.

- **UUID pairing invariant:** The function enforces the invariant that a `UI_Manager` and its paired `Graphics_Window` share the same UUID. If this invariant is violated, `debug_abort` is called to surface the inconsistency. This is a deliberate design decision, not a bug.

## Implementation Correctness

- **Type compatibility:** All parameter types match their target field/function types exactly. `p_game` is `Game*`, `uuid_of__ui_manager__u32` is `Identifier__u32`, and the returned `UI_Manager*` and `Graphics_Window*` pointers are correctly cast from `Serialization_Header*` to their respective types. No implicit conversions or truncation occur.

- **Undefined behavior:** No broken pointer arithmetic, no null dereference, no type punning, and no out-of-bounds access. The `p_game` null check is performed (debug builds). The `p_ui_manager` null check guards against dereferencing a failed lookup. The `p_graphics_window` null check guards against using an invalid window pointer. The `DEALLOCATE_P` macro correctly accesses the `Serialization_Header` portion of the `UI_Manager` struct (which is the first member, `Serialization_Header _serialization_header`).

- **Validation:** Validation is appropriate for the function's role. The `p_game` null check is debug-only, consistent with the codebase's pattern (callers are expected to provide valid pointers in release). The UUID lookup failures are handled gracefully (log + early return for missing UI manager; abort for missing graphics window due to the memory-leak risk). The function does not validate that `uuid_of__ui_manager__u32` is not `IDENTIFIER__UNKNOWN__u32`, but this is acceptable because `dehash_identitier_u32_in__contigious_array` already handles invalid UUIDs by returning null, and the function's null check on `p_ui_manager` covers this case.

## Side Effects

1. All `UI_Element`s in the `UI_Manager`'s pool are released (their dispose handlers are invoked, their serialization headers are marked as deallocated, and their entries in the pointer array are removed).
2. The `UI_Manager`'s dynamically allocated `pM_ui_element_pool` and `pM_ptr_array_of__ui_elements` arrays are freed via `free()`.
3. The `UI_Manager` struct's body (excluding `Serialization_Header`) is zeroed via `memset` in `initialize_ui_manager`.
4. The `UI_Manager`'s `Serialization_Header.uuid` is set to `IDENTIFIER__UNKNOWN__u32`, marking the struct as deallocated for pool reuse.
5. Debug logging may occur (via `debug_error` / `debug_abort`) depending on runtime conditions.
6. The `Graphics_Window` and `Game` objects are read but not modified.
