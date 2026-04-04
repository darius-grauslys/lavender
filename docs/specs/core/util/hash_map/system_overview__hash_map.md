# System Overview: UUID Mapped Pool (Hash Map) Utilities

## Purpose

The hash map module provides a generic, macro-based UUID-mapped pool
data structure. A `UUID_MAPPED__POOL` is a fixed-size pool of
serializable elements that supports allocation, deallocation, and O(1)
UUID-based lookup (dehashing). This is the engine's primary mechanism
for managing pools of UUID-identified resources — entities, inventories,
game actions, graphics windows, UI elements, and other objects that must
be locatable by their unique identifier.

## Architecture

### Data Structure

    UUID_MAPPED__POOL(My_Pool, My_Element, 64)

    Produces:
    +--------------------------------------------------+
    | My_Pool                                          |
    | +----------------------------------------------+ |
    | | Serialization_Pool _serialization_pool        | |
    | |   +-- quantity_of__pool_elements: 64          | |
    | |   +-- size_of__element: sizeof(My_Element)    | |
    | |   +-- p_headers: &_values[0]                  | |
    | +----------------------------------------------+ |
    | | My_Element _values[0]                         | |
    | |   +-- Serialization_Header                    | |
    | |   |     +-- size_of__struct                   | |
    | |   |     +-- uuid                              | |
    | |   +-- (element-specific fields)               | |
    | +----------------------------------------------+ |
    | | My_Element _values[1]                         | |
    | |   +-- ...                                     | |
    | +----------------------------------------------+ |
    | | ...                                           | |
    | +----------------------------------------------+ |
    | | My_Element _values[63]                        | |
    | |   +-- ...                                     | |
    | +----------------------------------------------+ |
    +--------------------------------------------------+

### Element Requirement

Every element type used with `UUID_MAPPED__POOL` **must** begin with a
`Serialization_Header` as its first field:

    typedef struct My_Element_t {
        Serialization_Header _serialization_header;
        // ... other fields ...
    } My_Element;

The `Serialization_Header` contains:

| Field | Type | Purpose |
|-------|------|---------|
| `size_of__struct` | `Quantity__u32` | Size of the element struct in bytes |
| `uuid` | `Identifier__u32` | Unique identifier assigned on allocation |

The `uuid` field is used for allocation tracking (allocated vs. free)
and for dehashing (UUID-to-index lookup).

### Relationship to Serialization_Pool

`UUID_MAPPED__POOL` is a typed wrapper around the engine's
`Serialization_Pool`. The generated functions delegate to:

| Generated Function | Delegates To |
|-------------------|-------------|
| `initialize_<name>` | `initialize_serialization_pool` |
| `allocate_<type_value>_from__<name>` | `allocate_from__serialization_pool` |
| `release_<type_value>_from__<name>` | `release_from__serialization_pool` |
| `dehash_p_<type_value>_from__<name>` | `DEHASH` macro (from `serialization/hashing.h`) |

The generated functions cast between `Serialization_Header*` and
`type_value*`, providing type safety at the API boundary.

### UUID Dehashing

The `DEHASH` macro uses the UUID and pool metadata to compute an index
into the `_values` array:

1. The UUID is hashed to produce a candidate index.
2. If the element at that index has a matching UUID, it is returned
   (O(1) best case).
3. On hash collision, a linear probe or similar resolution is used
   (O(N) worst case).

This is the same dehashing mechanism used by `Collision_Node_Pool` for
64-bit UUID lookups into contiguous arrays.

## Lifecycle

### 1. Instantiation

**Header file**:

    #include "util/hash_map/hash_map.h"

    UUID_MAPPED__POOL(My_Pool, My_Element, 64)
    DECLARE_API__UUID_MAPPED__POOL(My_Pool, My_Element, 64)

Unlike `ENUM_MAP`, all generated functions are `static inline`, so
there is no separate `DEFINE_API` macro needed in a source file.

### 2. Initialization

    My_Pool my_pool;
    initialize_My_Pool(&my_pool);

After initialization:
- `_serialization_pool.quantity_of__pool_elements` is set to the pool
  length.
- `_serialization_pool.size_of__element` is set to `sizeof(type_value)`.
- `_serialization_pool.p_headers` points to `&_values[0]`.
- All elements are in the free state.

### 3. Allocation

    My_Element *p_element =
        allocate_My_Element_from__My_Pool(&my_pool);

    if (!p_element) {
        // Pool is exhausted — all slots are in use
    }

On successful allocation:
- The element's `_serialization_header` is initialized with a UUID and
  struct size.
- The element is marked as allocated in the pool's internal state.
- A pointer to the element is returned.

### 4. UUID Lookup (Dehashing)

    My_Element *p_found =
        dehash_p_My_Element_from__My_Pool(
                &my_pool,
                some_uuid);

    if (!p_found) {
        // UUID not found in pool
    }

### 5. Deallocation

    release_My_Element_from__My_Pool(&my_pool, p_element);

After release:
- The element's slot is available for future allocation.
- The element's UUID is no longer valid for dehashing.

### Element Lifecycle Diagram

    [Pool Initialized]
            |
    allocate_<type_value>_from__<name>
            |
            v
    [Element Allocated — UUID assigned]
            |
        (use element; look up by UUID via dehash)
            |
    release_<type_value>_from__<name>
            |
            v
    [Element Returned to Pool — slot reusable]

## Usage in the Engine

UUID-mapped pools are used for any system that manages a pool of
UUID-identified objects:

| Consumer | Element Type | Pool Size | Purpose |
|----------|-------------|-----------|---------|
| Collision Node Pool | `Collision_Node` | `QUANTITY_OF__GLOBAL_SPACE` | Spatial partitioning nodes per loaded chunk |
| Entity Manager | Entity | `MAX_QUANTITY_OF__ENTITIES` | Entity allocation and UUID lookup |
| Hitbox Context | `Hitbox_Manager_Instance` | `MAX_QUANTITY_OF__HITBOX_MANAGERS` | Hitbox manager instance pool |
| Graphics Window Manager | `Graphics_Window` | Platform-defined | Graphics window allocation |
| UI Manager | `UI_Element` | Platform-defined | UI element allocation |
| Game Action System | `Game_Action` | Platform-defined | Game action allocation and network sync |

## Comparison with Enum Map

| Aspect | Enum Map | UUID Mapped Pool |
|--------|----------|-----------------|
| Key type | Engine enum | `Identifier__u32` (UUID) |
| Key space | Dense, small (enum count) | Sparse, large (32-bit UUID space) |
| Lookup | O(1) array index | O(1) dehash (amortized) |
| Allocation | N/A (all slots always exist) | Explicit allocate/release |
| Element requirement | Any type | Must begin with `Serialization_Header` |
| Code generation | `DEFINE_API` in source file | All `static inline` |

Use `ENUM_MAP` when the key is an enum with a known, small set of
variants. Use `UUID_MAPPED__POOL` when elements are dynamically
allocated and identified by UUID.

## Error Handling

| Condition | Behavior |
|-----------|----------|
| Pool exhaustion on allocate | Returns null |
| Dehash with unknown UUID | May return null or incorrect element; caller must validate |
| Release of non-pool element | Undefined behavior |

Error handling for bounds checking and UUID validation is delegated to
the underlying `Serialization_Pool` and `DEHASH` implementations.

## Preconditions and Postconditions

### Preconditions

- `initialize_<name>`: pointer must be non-null.
- `allocate_<type_value>_from__<name>`: pool must be initialized.
- `release_<type_value>_from__<name>`: the element must have been
  previously allocated from this pool.
- `dehash_p_<type_value>_from__<name>`: the UUID should correspond to
  a currently allocated element.

### Postconditions

- After `initialize_<name>`: pool is ready for allocation; all elements
  are free.
- After `allocate_<type_value>_from__<name>`: the returned element has
  a valid `_serialization_header` with an assigned UUID.
- After `release_<type_value>_from__<name>`: the element's slot is
  available for future allocation.

## Memory Layout

    struct <name>_t {
        Serialization_Pool _serialization_pool;     // pool metadata
        <type_value> _values[<length_of__pool>];    // element array
    };

Total size: `sizeof(Serialization_Pool) + sizeof(type_value) × length_of__pool`.
