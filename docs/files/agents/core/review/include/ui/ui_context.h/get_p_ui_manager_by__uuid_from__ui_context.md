# get_p_ui_manager_by__uuid_from__ui_context

**File of origin:** `core/source/ui/ui_context.c`

## Semantic

Looks up and returns a pointer to a `UI_Manager` within the `UI_Context`'s fixed-size `ui_managers` array by matching the given UUID against the `Serialization_Header` embedded at the start of each `UI_Manager` struct. Returns `NULL` if no matching manager is found or if the UUID is invalid.

## Pre-conditions

1. `p_ui_context` must be non-null. The function dereferences `p_ui_context` to access the `ui_managers` field; no null-check is performed (consistent with the codebase pattern for direct `UI_Context` field accessors such as `allocate_p_ui_manager_from__ui_context`).
2. `uuid_of__ui_manager__u32` may be any `Identifier__u32` value, including `IDENTIFIER__UNKNOWN__u32`. The dehash callee handles invalid identifiers gracefully by returning `NULL`.
3. The `ui_managers` array within `p_ui_context` must have been initialized via `initialize_ui_context` (which calls `initialize_serialization_header__contiguous_array`), so that each `UI_Manager`'s `Serialization_Header` has a valid `size_of__struct` field. This is required because `poll_for__uuid_collision` reads `p_serialization_headers->size_of__struct` to compute element strides.

## Post-conditions

1. Returns a valid `UI_Manager*` whose `Serialization_Header.uuid` matches `uuid_of__ui_manager__u32`, if such a manager exists in the array.
2. Returns `NULL` (0) if `uuid_of__ui_manager__u32` is `IDENTIFIER__UNKNOWN__u32` (invalid identifier).
3. Returns `NULL` (0) if no `UI_Manager` in the array has a matching UUID (i.e., the identifier is not present or all collision probes failed).

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation fulfills its semantic intent. The function is a thin lookup wrapper that delegates to `dehash_identitier_u32_in__contigious_array`, which performs hash-based collision resolution over the contiguous `ui_managers` array. The `UI_Manager` struct has `Serialization_Header _serialization_header` as its **first** member (confirmed in `defines.h`), so casting the `ui_managers` array (of type `UI_Manager[]`) to `Serialization_Header*` is a valid C type-punning pattern that allows the serialization subsystem to traverse the array using `size_of__struct` as the stride. The return value (a `Serialization_Header*`) is cast back to `UI_Manager*`, which is safe because the pointer points to the beginning of a `UI_Manager` struct (whose first member is the `Serialization_Header`).

## Implementation Correctness

- **Type compatibility:** The cast from `UI_Manager*` (via array decay of `p_ui_context->ui_managers`) to `Serialization_Header*` is valid because `Serialization_Header` is the first member of `UI_Manager`. The reverse cast from `Serialization_Header*` to `UI_Manager*` is likewise valid. No implicit truncation or conversion occurs. `MAX_QUANTITY_OF__UI_MANAGERS` (value 8, from `defines.h`) is passed as `Quantity__u32`, matching the callee's expected type.
- **Undefined behavior:** No null dereference occurs *within this function's own logic* beyond the implicit dereference of `p_ui_context->ui_managers`. The callee `dehash_identitier_u32_in__contigious_array` checks for invalid identifiers and out-of-bounds indices before any array access, preventing out-of-bounds reads. No type punning beyond the valid first-member cast. No pointer arithmetic is performed directly in this function.
- **Validation:** No null-check on `p_ui_context` is present. This is consistent with the codebase pattern — sibling functions like `allocate_p_ui_manager_from__ui_context` also omit explicit null checks on `p_ui_context`. The dehash callee validates the identifier and handles "not found" cases, which is the appropriate level of validation for this lookup function.

## Side Effects

No side effects. This is a pure lookup function that reads from the `ui_managers` array and returns a pointer. It does not modify `p_ui_context`, the `ui_managers` array, or any `UI_Manager` within it.
