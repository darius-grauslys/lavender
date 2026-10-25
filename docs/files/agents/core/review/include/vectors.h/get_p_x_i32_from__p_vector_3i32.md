# get_p_x_i32_from__p_vector_3i32

**File of origin:** `core/include/vectors.h` (lines 458–462)

## Semantic

Returns a mutable pointer to the `x__i32` (x-component) field of a `Vector__3i32` struct, allowing the caller to read or write that component in place.

## Pre-conditions

1. `p_vector__3i32` must be a valid, non-null pointer to an initialized `Vector__3i32` object. Passing `NULL` results in undefined behavior (the function performs no null check).
2. The pointed-to `Vector__3i32` must not be concurrently modified by another thread without external synchronization (no internal locking is performed).

## Post-conditions

1. On return, the function yields a non-null `Signed_Index__i32 *` that points directly to the `x__i32` member of the struct referenced by `p_vector__3i32`.
2. The returned pointer remains valid as long as the original `Vector__3i32` object is alive and not moved/reallocated; any modification through the returned pointer mutates the x-component of that same struct.
3. No other fields of the struct are affected by this function.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation faithfully fulfills its intent: it returns `&p_vector__3i32->x__i32`, which is exactly a pointer to the x-component of the input vector. The field accessed (`x__i32`) is the correct member of `Vector__3i32` (defined in `defines_weak.h` as `Signed_Index__i32 x__i32, y__i32, z__i32;`). There is no semantic drift — the function does precisely what its name and signature promise.

## Implementation Correctness

- **Type compatibility:** The return type `Signed_Index__i32 *` matches the field type `Signed_Index__i32` exactly. No implicit conversions or truncation occur.
- **Undefined behavior:** The function itself performs no dereference of the pointer; it only computes the address of a struct member via `->`. If the caller passes a valid pointer, no UB is introduced. If the caller passes `NULL`, UB occurs at the call site, but this is consistent with all sibling accessor functions in this file (e.g., `get_p_y_i32_from__p_vector_3i32`, `get_p_z_i32_from__p_vector_3i32`) and is the caller's responsibility.
- **Validation:** No null-check is performed. This is appropriate for a lightweight `static inline` accessor — validation is the caller's responsibility, and adding checks here would be inconsistent with the surrounding code and would defeat the purpose of an inline accessor.

## Side Effects

No side effects. The function does not modify any state; it is a pure accessor that returns a pointer to an existing struct member. Any mutation that occurs through the returned pointer is performed by the caller, not by this function.
