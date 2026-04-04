# Specification: core/include/serialization/hashing.h

## Overview

Provides hash-based allocation, deallocation, and lookup for contiguous arrays
of structs identified by `Serialization_Header` or
`Serialization_Header__UUID_64`. This is the core mechanism by which the engine
maps UUIDs to array indices for O(1) average-case access to pooled resources.

The hashing strategy is simple modular hashing (`uuid % array_length`) with
linear probing for collision resolution.

## Dependencies

- `defines.h` (for `Serialization_Header`, `Serialization_Header__UUID_64`,
  identifier types, `IDENTIFIER__UNKNOWN__u32`, `IDENTIFIER__UNKNOWN__u64`)
- `defines_weak.h` (forward declarations)
- `numerics.h` (numeric utilities)
- `serialization/identifiers.h` (UUID generation and validation)
- `serialization/serialization_header.h` (header initialization, `ALLOCATE_P`,
  `DEALLOCATE_P`, `IS_DEALLOCATED_P`)

## Functions

### Collision Resolution

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `poll_for__uuid_collision` | `(Serialization_Header*, Quantity__u32 length, Identifier__u32, Index__u32 initial_index) -> Index__u32` | `Index__u32` | Starting from `initial_index`, linearly probes the array for a slot matching the UUID or a free slot. Returns `IDENTIFIER__UNKNOWN__u32` if the array is completely full. |
| `poll_for__uuid_collision__uuid_64` | `(Serialization_Header__UUID_64*, Quantity__u32 length, Identifier__u64, Index__u32 initial_index) -> Index__u32` | `Index__u32` | 64-bit variant. |

### UUID Availability

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_next_available__uuid_in__contiguous_array` | `(Serialization_Header*, Quantity__u32 length, Identifier__u32 uuid) -> Identifier__u32` | `Identifier__u32` | Returns a UUID that can be placed in the array without collision. May return the input UUID unchanged if no collision exists, or `IDENTIFIER__UNKNOWN__u32` if the array is full. |
| `get_next_available__uuid_in__contiguous_array__uuid_64` | `(Serialization_Header__UUID_64*, Quantity__u32 length, Identifier__u64 uuid) -> Identifier__u64` | `Identifier__u64` | 64-bit variant. |

### Dehashing (Lookup)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `dehash_identitier_u32_in__contigious_array` | `(Serialization_Header*, Quantity__u32 length, Identifier__u32) -> Serialization_Header*` | `Serialization_Header*` or `NULL` | Looks up a struct by UUID. Returns null if not found. |
| `dehash_identitier_u64_in__contigious_array` | `(Serialization_Header__UUID_64*, Quantity__u32 length, Identifier__u64) -> Serialization_Header__UUID_64*` | `Serialization_Header__UUID_64*` or `NULL` | 64-bit variant. |

### Allocation

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_next_available__allocation_in__contiguous_array` | `(Serialization_Header*, Quantity__u32 length, Identifier__u32) -> Serialization_Header*` | `Serialization_Header*` or `NULL` | Finds a free slot for the given UUID (handling collisions). Does NOT set the UUID. |
| `get_next_available__allocation_in__contiguous_array__u64` | `(Serialization_Header__UUID_64*, Quantity__u32 length, Identifier__u64) -> Serialization_Header__UUID_64*` | `Serialization_Header__UUID_64*` or `NULL` | 64-bit variant. |

### Random Allocation (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_next_available__random_uuid_in__contiguous_array` | `(Serialization_Header*, Quantity__u32 length, Repeatable_Psuedo_Random*) -> Identifier__u32` | `Identifier__u32` | Generates a random UUID and resolves it to an available slot. |
| `get_next_available__random_branded_uuid_in__contiguous_array` | `(Serialization_Header*, Quantity__u32 length, Repeatable_Psuedo_Random*, Identifier__u32 branding) -> Identifier__u32` | `Identifier__u32` | Generates a branded random UUID and resolves it. |
| `get_next_available__random_uuid_in__contiguous_array__uuid_64` | `(Serialization_Header__UUID_64*, Quantity__u32 length, Repeatable_Psuedo_Random*) -> Identifier__u64` | `Identifier__u64` | 64-bit variant. |
| `get_next_available__random_branded_uuid_in__contiguous_array__uuid_64` | `(Serialization_Header__UUID_64*, Quantity__u32 length, Repeatable_Psuedo_Random*, Identifier__u64 branding) -> Identifier__u64` | `Identifier__u64` | 64-bit branded variant. |

### Combined Allocation + Initialization (static inline)

These functions find a free slot AND set the UUID in one call:

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `allocate_serialization_header_with__this_uuid` | `(Serialization_Header*, Quantity__u32 length, Identifier__u32 uuid) -> Serialization_Header*` | `Serialization_Header*` or `NULL` | Finds a slot for the given UUID and calls `ALLOCATE_P`. |
| `allocate_serialization_header` | `(Serialization_Header*, Quantity__u32 length, Repeatable_Psuedo_Random*) -> Serialization_Header*` | `Serialization_Header*` | Generates a random UUID, finds a slot, and allocates. |
| `allocate_serialization_header_with__uuid_branding` | `(Serialization_Header*, Quantity__u32 length, Repeatable_Psuedo_Random*, Identifier__u32 branding) -> Serialization_Header*` | `Serialization_Header*` | Generates a branded random UUID, finds a slot, and allocates. |
| `allocate_serialization_header_with__this_uuid__u64` | `(Serialization_Header__UUID_64*, Quantity__u32 length, Identifier__u64 uuid) -> Serialization_Header__UUID_64*` | `Serialization_Header__UUID_64*` or `NULL` | 64-bit variant. |
| `allocate_serialization_header__u64` | `(Serialization_Header__UUID_64*, Quantity__u32 length, Repeatable_Psuedo_Random*) -> Serialization_Header__UUID_64*` | `Serialization_Header__UUID_64*` | 64-bit random variant. |
| `allocate_serialization_header_with__uuid_branding__u64` | `(Serialization_Header__UUID_64*, Quantity__u32 length, Repeatable_Psuedo_Random*, Identifier__u64 branding) -> Serialization_Header__UUID_64*` | `Serialization_Header__UUID_64*` | 64-bit branded variant. |

### Random Allocation with OUT Parameter

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_next_available__random_allocation_in__contiguous_array` | `(Serialization_Header*, Quantity__u32 length, Repeatable_Psuedo_Random*, Identifier__u32 *p_OUT_uuid) -> Serialization_Header*` | `Serialization_Header*` | If `*p_OUT_uuid` is not `IDENTIFIER__UNKNOWN__u32`, it is treated as a branding mask. The resolved UUID is written to `*p_OUT_uuid`. |
| `get_next_available__random_allocation_in__contiguous_array__uuid_64` | `(Serialization_Header__UUID_64*, Quantity__u32 length, Repeatable_Psuedo_Random*, Identifier__u64 *p_OUT_uuid) -> Serialization_Header__UUID_64*` | `Serialization_Header__UUID_64*` | 64-bit variant. |

### Existence Check (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `has_uuid_in__contiguous_array` | `(Serialization_Header*, Quantity__u32 length, Identifier__u32) -> bool` | `bool` | Returns true if the UUID exists in the array. |
| `has_uuid_in__contiguous_array__uuid_64` | `(Serialization_Header__UUID_64*, Quantity__u32 length, Identifier__u64) -> bool` | `bool` | 64-bit variant. |

### Index Computation (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `bound_uuid_to__contiguous_array` | `(Identifier__u32, Quantity__u32 length) -> Identifier__u32` | `Identifier__u32` | Computes `uuid % length`. The initial hash index. |
| `bound_uuid_to__contiguous_array__uuid_64` | `(Identifier__u64, Quantity__u32 length) -> Identifier__u32` | `Identifier__u32` | 64-bit variant. |

## Hashing Strategy

### Algorithm

1. **Initial index**: `uuid % array_length`
2. **Collision resolution**: Linear probing. If the slot at the initial index
   is occupied by a different UUID, advance to the next slot (wrapping around).
3. **Termination**: Stop when a matching UUID or a deallocated slot is found,
   or when the entire array has been probed.

### Implications

- **O(1) average case** for lookup and allocation when the array is not
  heavily loaded.
- **O(n) worst case** when the array is nearly full.
- Arrays should be sized to avoid high load factors. In practice, pool sizes
  are fixed at compile time and matched to expected usage.

## Agentic Workflow

### Common Patterns

**Allocate a struct in a pool:**

    Serialization_Header *p_header =
        allocate_serialization_header_with__uuid_branding(
            pool_headers,
            pool_length,
            &randomizer,
            GET_UUID_BRANDING(Lavender_Type__Entity, 0));

**Look up a struct by UUID:**

    Serialization_Header *p_header =
        dehash_identitier_u32_in__contigious_array(
            pool_headers,
            pool_length,
            target_uuid);

**Check existence:**

    if (has_uuid_in__contiguous_array(pool, length, uuid)) { ... }

### Preconditions

- The contiguous array must be initialized with
  `initialize_serialization_header__contiguous_array` before any hashing
  operations.
- `size_of__struct` must be correctly set in every header for pointer
  arithmetic to work.
- UUIDs passed to allocation functions must not be `IDENTIFIER__UNKNOWN__u32`
  (or `__u64`), as this is the sentinel for deallocated slots.

### Postconditions

- After `allocate_serialization_header*`: the returned header has its UUID
  set and `is_serialized_struct__deallocated` returns false.
- After `dehash_identitier_u32_in__contigious_array`: returns null if not
  found, otherwise a pointer to the matching header.

### Error Handling

- Allocation functions return `NULL` when the array is full.
- `dehash` functions return `NULL` when the UUID is not found.
- `poll_for__uuid_collision` returns `IDENTIFIER__UNKNOWN__u32` when the
  array is completely full.
