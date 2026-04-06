# 1. Specification: core/include/serialization/serialized_field.h

## 1.1 Overview

Provides a generic "soft pointer" mechanism for referencing pooled structs by
UUID. A `Serialized_Field` stores both a UUID and a data pointer, enabling
deferred linking: the UUID can be set at serialization time, and the pointer
resolved later against a contiguous array. This is the engine's approach to
serializable references between pooled objects.

## 1.2 Dependencies

- `defines.h` (for `Serialized_Field`, `Serialization_Header`,
  `Identifier__u32`, `IDENTIFIER__UNKNOWN__u32`)
- `defines_weak.h` (forward declarations)
- `serialization/serialization_header.h` (for `is_identifier_u32_matching__serialization_header`)

## 1.3 Types

### 1.3.1 Serialized_Field

    typedef struct Serialized_Field_t {
        union {
            struct {
                Serialization_Header _serialization_header;
            };
            struct {
                Identifier__u32 identifier_for__serialized_field;
                Quantity__u32   :32;
            };
        };
        union {
            void *p_serialized_field__data;
            Serialization_Header *p_serialized_field__serialization_header;
            Entity *p_serialized_field__entity;
            Inventory *p_serialized_field__inventory;
            Item_Stack *p_serialized_field__item_stack;
            Chunk *p_serialized_field__chunk;
        };
    } Serialized_Field;

| Field | Type | Description |
|-------|------|-------------|
| `identifier_for__serialized_field` | `Identifier__u32` | The UUID of the target struct this field references. Overlaps with `_serialization_header.uuid`. |
| `p_serialized_field__data` | `void*` | Opaque pointer to the referenced struct. |
| `p_serialized_field__serialization_header` | `Serialization_Header*` | Typed access to the referenced struct's header. |
| `p_serialized_field__entity` | `Entity*` | Typed access when referencing an Entity. |
| `p_serialized_field__inventory` | `Inventory*` | Typed access when referencing an Inventory. |
| `p_serialized_field__item_stack` | `Item_Stack*` | Typed access when referencing an Item_Stack. |
| `p_serialized_field__chunk` | `Chunk*` | Typed access when referencing a Chunk. |

### 1.3.2 Type Aliases

    typedef struct Serialized_Field_t Serialized_Item_Stack_Ptr;
    typedef struct Serialized_Field_t Serialized_Inventory_Ptr;
    typedef struct Serialized_Field_t Serialized_Entity_Ptr;
    typedef struct Serialized_Field_t Serialized_Chunk_Ptr;

These aliases provide semantic clarity when a `Serialized_Field` is used to
reference a specific type.

## 1.4 Functions

### 1.4.1 Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_serialized_field` | `(Serialized_Field*, void* data, Identifier__u32 uuid) -> void` | Sets both the data pointer and the UUID. |
| `initialize_serialized_field_as__unassigned` | `(Serialized_Field*) -> void` | Sets data to null and UUID to `IDENTIFIER__UNKNOWN__u32`. (static inline) |
| `initialize_serialized_field_as__unlinked` | `(Serialized_Field*, Identifier__u32 uuid) -> void` | Sets UUID but leaves data pointer null. Used when the UUID is known but the target has not been resolved yet. (static inline) |

### 1.4.2 Linking

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `link_serialized_field_against__contiguous_array` | `(Serialized_Field*, Serialization_Header*, Quantity__u32 quantity) -> bool` | `bool` | Iterates a contiguous array of structs, linking the field's data pointer to the first struct whose UUID matches the field's `identifier_for__serialized_field`. Returns true on success. |
| `point_serialized_field_to__this_serialized_struct` | `(Serialized_Field*, void* struct) -> void` | `void` | Directly sets the data pointer to the given struct. The struct's `Serialization_Header.uuid` must match the field's UUID. |

### 1.4.3 Validation (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_serialized_field_matching__serialization_header` | `(Serialized_Field*, Serialization_Header*) -> bool` | `bool` | Returns true if the field's UUID matches the header's UUID. Debug-aborts on null. |
| `is_p_serialized_field__linked` | `(Serialized_Field*) -> bool` | `bool` | Returns true if: (1) data pointer is non-null, (2) the pointed-to struct has a valid UUID, and (3) the UUIDs match. |

### 1.4.4 Typed Getters (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_p_inventory_from__serialized_field` | `(Serialized_Field*) -> Inventory*` | `Inventory*` | Returns the data pointer cast to `Inventory*`. |
| `get_p_entity_from__serialized_field` | `(Serialized_Field*) -> Entity*` | `Entity*` | Returns the data pointer cast to `Entity*`. |
| `get_p_chunk_from__serialized_field` | `(Serialized_Field*) -> Chunk*` | `Chunk*` | Returns the data pointer cast to `Chunk*`. |

## 1.5 Agentic Workflow

### 1.5.1 Serialization Pattern

1. **Before save**: The `Serialized_Field` holds both a UUID and a live
   pointer. Only the UUID needs to be serialized.
2. **After load**: The `Serialized_Field` is initialized as "unlinked"
   (UUID set, pointer null).
3. **Resolution**: Call `link_serialized_field_against__contiguous_array`
   to resolve the UUID back to a live pointer.

### 1.5.2 Common Usage

    // Create an unlinked reference
    initialize_serialized_field_as__unlinked(
        &my_field, target_uuid);

    // Later, resolve against a pool
    bool linked = link_serialized_field_against__contiguous_array(
        &my_field,
        (Serialization_Header*)entity_pool,
        quantity_of__entities);

    // Check before use
    if (is_p_serialized_field__linked(&my_field)) {
        Entity *p_entity = get_p_entity_from__serialized_field(&my_field);
    }

### 1.5.3 Preconditions

- `link_serialized_field_against__contiguous_array` requires that the
  contiguous array elements have `Serialization_Header` as their first field.
- The field's `identifier_for__serialized_field` must be set before linking.

### 1.5.4 Postconditions

- After successful `link_serialized_field_against__contiguous_array`:
  `is_p_serialized_field__linked` returns true.
- After `initialize_serialized_field_as__unassigned`:
  `is_p_serialized_field__linked` returns false.

### 1.5.5 Error Handling

- `link_serialized_field_against__contiguous_array` returns false if no
  matching UUID is found.
- `is_serialized_field_matching__serialization_header` calls `debug_abort`
  on null arguments in debug builds.
