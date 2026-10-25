# is_serialized_struct__deallocated

**File of origin:** `core/include/serialization/serialization_header.h`

## Semantic

Returns `true` if the given `Serialization_Header` pointer is NULL or if its `uuid` field equals `IDENTIFIER__UNKNOWN__u32`, indicating the struct has been deallocated (reset to its initial/pool-cleaned state). This is a non-mutating query function.

## Pre-conditions

1. `p_serialization_header` may be NULL; the function safely handles this case.
2. If `p_serialization_header` is non-NULL, it must point to a valid `Serialization_Header` struct in memory.

## Post-conditions

1. Returns `true` if `p_serialization_header` is NULL.
2. Returns `true` if `p_serialization_header` is non-NULL and its `uuid` field equals `IDENTIFIER__UNKNOWN__u32` (i.e., `(uint32_t)(-1)`).
3. Returns `false` if `p_serialization_header` is non-NULL and its `uuid` field is any value other than `IDENTIFIER__UNKNOWN__u32`.
4. The function does not modify any state; the `Serialization_Header` (if non-NULL) is read but not written.

## Correctness Verdict

**Correct**

## Semantic Alignment

The function correctly fulfills its semantic intent: it determines whether a serialized struct has been deallocated. In the Lavender engine, "deallocation" is implemented via Lavender-style initialization (not RAII), where a struct is reset to its initial conditions by setting its `uuid` to `IDENTIFIER__UNKNOWN__u32` via `initialize_serialization_header_for__deallocated_struct`. This function checks for exactly that sentinel state. The logic is straightforward and matches the intent.

## Implementation Correctness

- **Type compatibility:** The `uuid` field of `Serialization_Header` is of type `Identifier__u32` (a `typedef` for `uint32_t`), and `IDENTIFIER__UNKNOWN__u32` is defined as `(uint32_t)(-1)`. The comparison is between two `uint32_t` values — no implicit conversions or truncation occur.
- **Undefined behavior:** No null dereference occurs. The short-circuit evaluation of the `||` operator ensures `p_serialization_header->uuid` is only accessed when `p_serialization_header` is non-NULL.
- **Validation:** The NULL check is appropriate for this query function's role. Callers using the `IS_DEALLOCATED_P` macro rely on this NULL-safety, while direct callers of this function are also protected. No additional validation is needed.

## Side Effects

No side effects. This is a pure query function — it reads the `uuid` field of the `Serialization_Header` (if the pointer is non-NULL) and returns a boolean. No memory is modified, no I/O occurs, and no global state is touched.
