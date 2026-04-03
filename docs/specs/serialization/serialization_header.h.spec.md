# Specification: core/include/serialization/serialization_header.h

## Overview

Provides initialization, allocation, deallocation, and identity-checking
utilities for `Serialization_Header` and `Serialization_Header__UUID_64`.
These headers are embedded as the **first field** of nearly every pooled
struct in the engine, enabling UUID-based identification and allocation
tracking across contiguous arrays.

## Dependencies

- `defines.h` (for `Serialization_Header`, `Serialization_Header__UUID_64`,
  `Identifier__u32`, `Identifier__u64`, `Quantity__u32`)
- `defines_weak.h` (forward declarations)

## Types

### Serialization_Header

    typedef struct Serialization_Header_t {
        Quantity__u32       size_of__struct;
        Identifier__u32     uuid;
    } Serialization_Header;

| Field | Type | Description |
|-------|------|-------------|
| `size_of__struct` | `Quantity__u32` | Byte size of the owning struct. Used for pointer arithmetic in contiguous arrays. |
| `uuid` | `Identifier__u32` | 32-bit UUID. `IDENTIFIER__UNKNOWN__u32` means deallocated. |

### Serialization_Header__UUID_64

    typedef struct Serialization_Header__UUID_64_t {
        Quantity__u32       size_of__struct;
        Identifier__u64     uuid;
    } Serialization_Header__UUID_64;

| Field | Type | Description |
|-------|------|-------------|
| `size_of__struct` | `Quantity__u32` | Byte size of the owning struct. |
| `uuid` | `Identifier__u64` | 64-bit UUID. `IDENTIFIER__UNKNOWN__u64` means deallocated. |

### UUID Branding

UUIDs can be "branded" with a type tag and index to encode metadata:

    Bits [31..26]: Lavender_Type (6 bits)
    Bits [25..20]: Index (6 bits)
    Bits [19..0]:  Random / unique portion

Macros:

| Macro | Description |
|-------|-------------|
| `GET_UUID_BRANDING(type, index)` | Constructs a branding mask from a `Lavender_Type` and index. |
| `BRAND_UUID(uuid, branding)` | Applies branding to a 32-bit UUID, preserving the lower bits. |
| `BRAND_UUID__64(uuid, branding)` | Applies branding to a 64-bit UUID, preserving the lower bits. |

### Convenience Macros

| Macro | Description |
|-------|-------------|
| `GET_UUID(header)` | Extracts UUID from a struct (by value). |
| `GET_UUID_P(p_header)` | Extracts UUID from a struct (by pointer). |
| `GET_UUID__u64(header)` | Extracts 64-bit UUID from a struct (by value). |
| `GET_UUID_P__u64(p_header)` | Extracts 64-bit UUID from a struct (by pointer). |
| `IS_DEALLOCATED(header)` | Returns true if the struct is deallocated (by value). |
| `IS_DEALLOCATED_P(p_header)` | Returns true if null or deallocated (by pointer). |
| `IS_DEALLOCATED__u64(header)` | 64-bit variant (by value). |
| `IS_DEALLOCATED_P__u64(p_header)` | 64-bit variant (by pointer). |
| `ALLOCATE_P(p_header, uuid)` | Initializes the header with the given UUID, preserving `size_of__struct`. |
| `ALLOCATE_P__u64(p_header, uuid)` | 64-bit variant. |
| `DEALLOCATE_P(p_header)` | Sets UUID to `IDENTIFIER__UNKNOWN__u32`, preserving `size_of__struct`. |
| `DEALLOCATE_P__u64(p_header)` | 64-bit variant. |

## Functions

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_serialization_header` | `(Serialization_Header*, Identifier__u32 uuid, Quantity__u32 size) -> void` | Sets UUID and struct size. |
| `initialize_serialization_header__uuid_64` | `(Serialization_Header__UUID_64*, Identifier__u64 uuid, Quantity__u32 size) -> void` | 64-bit variant. |
| `initialize_serialization_header_for__deallocated_struct` | `(Serialization_Header*, Quantity__u32 size) -> void` | Sets UUID to `IDENTIFIER__UNKNOWN__u32`. (static inline) |
| `initialize_serialization_header_for__deallocated_struct__uuid_64` | `(Serialization_Header__UUID_64*, Quantity__u32 size) -> void` | 64-bit variant. (static inline) |

### Contiguous Array Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_serialization_header__contiguous_array` | `(Serialization_Header*, Quantity__u32 length, Quantity__u32 size) -> void` | Initializes all headers in a contiguous array as deallocated. |
| `initialize_serialization_header__contiguous_array__uuid_64` | `(Serialization_Header__UUID_64*, Quantity__u32 length, Quantity__u32 size) -> void` | 64-bit variant. |

### Contiguous Array Access

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_p_serialization_header_from__contigious_array` | `(Serialization_Header*, Quantity__u32 length, Index__u32 index) -> Serialization_Header*` | `Serialization_Header*` | Index-based access into a contiguous array using `size_of__struct` for stride. |
| `get_p_serialization_header_from__contigious_array__uuid_64` | `(Serialization_Header__UUID_64*, Quantity__u32 length, Index__u32 index) -> Serialization_Header__UUID_64*` | `Serialization_Header__UUID_64*` | 64-bit variant. |
| `get_next_available_p_serialization_header` | `(Serialization_Header*, Quantity__u32 quantity) -> Serialization_Header*` | `Serialization_Header*` or `NULL` | Finds the first deallocated header in the array. |
| `get_next_available_p_serialization_header__uuid_64` | `(Serialization_Header__UUID_64*, Quantity__u32 quantity) -> Serialization_Header__UUID_64*` | `Serialization_Header__UUID_64*` or `NULL` | 64-bit variant. |

### Identity Checks (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_identifier_u32_matching__serialization_header` | `(Identifier__u32, Serialization_Header*) -> bool` | `bool` | Returns true if the UUID matches. Debug-aborts on null. |
| `is_identifier_u64_matching__serialization_header` | `(Identifier__u64, Serialization_Header__UUID_64*) -> bool` | `bool` | 64-bit variant. Debug-aborts on null. |
| `is_serialized_struct__deallocated` | `(Serialization_Header*) -> bool` | `bool` | Returns true if null or UUID is `IDENTIFIER__UNKNOWN__u32`. |
| `is_serialized_struct__deallocated__uuid_64` | `(Serialization_Header__UUID_64*) -> bool` | `bool` | 64-bit variant. |

## General Usage

`Serialization_Header` is the first field of most pooled structs in the engine.
Representative examples include:

- `Entity._serialization_header`
- `Hitbox_AABB._serialization_header`
- `Hitbox_Manager_Instance._serialization_header`
- `Sprite._serialization_header`
- `UI_Element._serialization_header`
- `Inventory._serialization_header`
- `Game_Action._serialiation_header`
- `Graphics_Window._serialization_header`
- `Process._serialization_header`

`Serialization_Header__UUID_64` is used for types requiring 64-bit identity,
such as:

- `Chunk._serialization_header`
- `Global_Space._serialization_header`
- `Collision_Node._serialization_header`

The `size_of__struct` field enables pointer arithmetic across contiguous arrays
of heterogeneous-sized structs (though in practice each pool is homogeneous).

## Agentic Workflow

### When to use this module

- When initializing any pooled struct, call `initialize_serialization_header`
  or use the `ALLOCATE_P` / `DEALLOCATE_P` macros.
- When checking if a struct is allocated, use `IS_DEALLOCATED_P` or
  `is_serialized_struct__deallocated`.
- When iterating contiguous arrays, use
  `get_p_serialization_header_from__contigious_array` for index-based access.
- When searching for a free slot, use
  `get_next_available_p_serialization_header`.

### Preconditions

- The `Serialization_Header` must be the **first field** of any struct that
  uses it. Pointer arithmetic and casting depend on this layout.
- `size_of__struct` must be set correctly before any contiguous array
  operations. It is typically set once during pool initialization and
  preserved across allocate/deallocate cycles.

### Postconditions

- After `ALLOCATE_P`: UUID is set, `is_serialized_struct__deallocated`
  returns false.
- After `DEALLOCATE_P`: UUID is `IDENTIFIER__UNKNOWN__u32`,
  `is_serialized_struct__deallocated` returns true.

### Error Handling

- `is_identifier_u32_matching__serialization_header` calls `debug_abort`
  on null pointer in debug builds.
- `is_serialized_struct__deallocated` safely returns true on null.
