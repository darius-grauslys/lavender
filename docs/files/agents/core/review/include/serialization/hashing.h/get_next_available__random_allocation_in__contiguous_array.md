# get_next_available__random_allocation_in__contiguous_array

**File of origin:** `core/source/serialization/hashing.c`

## Semantic

Allocates the next available (deallocated) slot in a contiguous array of
`Serialization_Header` structs. If the caller-provided UUID is invalid
(`IDENTIFIER__UNKNOWN__u32` or zero), a random UUID is generated; otherwise the
provided UUID is treated as a branding mask and combined with a random UUID via
`BRAND_UUID`. The resolved UUID is written out via `p_OUT_uuid__u32`, and a
pointer to the corresponding `Serialization_Header` is returned.

## Pre-conditions

1. `p_serialization_headers` must be a non-null pointer to a contiguous array of
   `Serialization_Header` structs, properly initialized (each header's
   `size_of__struct` field must be valid).
2. `length_of__p_serialization_headers` must be greater than zero (used as a
   divisor in modulo operations within callees).
3. `p_randomizer` must be a non-null, properly seeded `Repeatable_Psuedo_Random`
   instance (used only when a random UUID is needed).
4. `p_OUT_uuid__u32` must be a non-null pointer to a writable `Identifier__u32`.
   The caller should initialize it to `IDENTIFIER__UNKNOWN__u32` (or zero) to
   signal "generate a random UUID"; any other value is treated as a branding
   mask.

## Post-conditions

1. `p_OUT_uuid__u32` is updated to contain the resolved UUID that was assigned
   to the allocated slot.
2. Returns a pointer to the `Serialization_Header` for the allocated slot, or
   null if the array is full (no available slots).
3. The returned `Serialization_Header` is not mutated by this function — the
   caller is expected to call `ALLOCATE_P` (or equivalent) to mark it as
   allocated with the resolved UUID.

## Correctness Verdict

Correct

## Semantic Alignment

The implementation correctly fulfills its semantic intent:

- When `*p_OUT_uuid__u32` is invalid (or zero), it delegates to
  `get_next_available__random_uuid_in__contiguous_array`, which generates a
  fully random UUID.
- When `*p_OUT_uuid__u32` is a valid branding mask, it delegates to
  `get_next_available__random_branded_uuid_in__contiguous_array`, which
  generates a random UUID and combines it with the branding mask via
  `BRAND_UUID`.
- The resolved UUID is written to `*p_OUT_uuid__u32` and then passed to
  `get_next_available__allocation_in__contiguous_array`, which finds an
  available slot using `poll_for__uuid_collision`.
- The return value correctly propagates the result (or null if the array is
  full).

The function does not itself allocate or initialize the serialization header —
it only finds the available slot and resolves the UUID. This matches the
documented contract where callers (`allocate_serialization_header`,
`allocate_serialization_header_with__uuid_branding`) are responsible for calling
`ALLOCATE_P` after receiving the pointer.

## Implementation Correctness

- **Type compatibility:** All parameter types match the declarations in
  `hashing.h`. `Identifier__u32` is `uint32_t`, `Quantity__u32` is `uint32_t`,
  and `Index__u32` is `uint32_t`. No implicit conversions or truncation.
- **No undefined behavior:** No pointer arithmetic is performed directly in this
  function — it delegates to `poll_for__uuid_collision` and
  `get_next_available__allocation_in__contiguous_array`, both of which handle
  array traversal safely. Null checks on `p_serialization_headers` and
  `p_OUT_uuid__u32` are the caller's responsibility (documented in the header
  comment).
- **Validation:** The function does not perform null checks on its parameters.
  This is consistent with the codebase pattern where validation is the caller's
  responsibility (the header documentation states "Be sure to allocate the
  type!"). The debug-mode checks are in the lower-level functions
  (`poll_for__uuid_collision`, `get_p_serialization_header_from__contigious_array`).

## Side Effects

- Writes the resolved UUID to `*p_OUT_uuid__u32` (output parameter mutation).
- Does not mutate `p_serialization_headers` or any `Serialization_Header` within
  the array — only reads from it to find an available slot.
- May advance the internal state of `p_randomizer` if a new random UUID is
  generated (via `get_random__uuid_u32`).
