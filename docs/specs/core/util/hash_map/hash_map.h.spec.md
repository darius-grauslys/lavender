# 1 Specification: core/include/util/hash_map/hash_map.h

## 1.1 Overview

Provides a generic, macro-based UUID-mapped pool data structure.
A `UUID_MAPPED__POOL` is a fixed-size pool of serializable elements
that supports allocation, deallocation, and O(1) UUID-based lookup
(dehashing) via the engine's `Serialization_Pool` and hashing utilities.

This is the engine's primary mechanism for managing pools of
UUID-identified resources (entities, inventories, game actions, etc.)
where elements must be locatable by their UUID.

The entire API is generated via preprocessor macros, producing
type-safe structs and functions for each instantiation.

## 1.2 Dependencies

- `defines.h` (for `Serialization_Pool`, `Serialization_Header`,
  `Identifier__u32`)
- `serialization/hashing.h` (for `DEHASH` macro,
  `initialize_serialization_pool`, `allocate_from__serialization_pool`,
  `release_from__serialization_pool`)

## 1.3 Types

### 1.3.1 UUID_MAPPED__POOL (macro — struct definition)

    #define UUID_MAPPED__POOL(name, type_value, length_of__pool) \
        typedef struct name##_t { \
            Serialization_Pool _serialization_pool; \
            type_value _values[length_of__pool]; \
        } name;

Defines a struct named `name` containing a `Serialization_Pool` header
followed by a fixed-size array of `type_value` elements. The
`Serialization_Pool` manages allocation state and enables UUID-based
dehashing into the `_values` array.

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | identifier | The name of the generated struct typedef. |
| `type_value` | type name | The element type. **Must** have a `Serialization_Header _serialization_header` as its first field. |
| `length_of__pool` | integer constant | Maximum number of elements in the pool. |

**Example instantiation**:

    UUID_MAPPED__POOL(My_Pool, My_Element, 64)

Produces:

    typedef struct My_Pool_t {
        Serialization_Pool _serialization_pool;
        My_Element _values[64];
    } My_Pool;

### 1.3.2 Serialization_Pool (struct, from defines.h)

    typedef struct Serialization_Pool_t {
        Quantity__u32 quantity_of__pool_elements;
        Quantity__u32 size_of__element;
        Serialization_Header *p_headers;
    } Serialization_Pool;

| Field | Type | Description |
|-------|------|-------------|
| `quantity_of__pool_elements` | `Quantity__u32` | Number of elements in the pool. |
| `size_of__element` | `Quantity__u32` | Size in bytes of each element. |
| `p_headers` | `Serialization_Header*` | Pointer to the first element's serialization header (i.e. `&_values[0]`). |

### 1.3.3 Element Requirement

Every `type_value` used with `UUID_MAPPED__POOL` **must** begin with a
`Serialization_Header`:

    typedef struct My_Element_t {
        Serialization_Header _serialization_header;
        // ... other fields ...
    } My_Element;

The `Serialization_Header` contains:

    typedef struct Serialization_Header_t {
        Quantity__u32 size_of__struct;
        Identifier__u32 uuid;
    } Serialization_Header;

The `uuid` field is used for allocation tracking and dehashing.

### 1.3.4 Generated Functions

#### 1.3.4.1 DECLARE_API__UUID_MAPPED__POOL (macro)

    #define DECLARE_API__UUID_MAPPED__POOL(name, type_value, length_of__pool)

Declares the following static inline functions:

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `initialize_<name>` | `(<name>*) -> void` | `void` | Initializes the serialization pool header. Sets `quantity_of__pool_elements` and `size_of__element`. |
| `allocate_<type_value>_from__<name>` | `(<name>*) -> type_value*` | `type_value*` | Allocates and returns the next available element from the pool. Returns null if the pool is full. |
| `release_<type_value>_from__<name>` | `(<name>*, type_value*) -> void` | `void` | Releases an element back to the pool. |
| `dehash_p_<type_value>_from__<name>` | `(<name>*, Identifier__u32 uuid) -> type_value*` | `type_value*` | Looks up an element by UUID using the `DEHASH` macro. O(1) if the UUID maps directly to the correct slot; O(N) worst case on collision. |

## 1.4 Agentic Workflow

### 1.4.1 When to Use

Use `UUID_MAPPED__POOL` when:

- You need a fixed-size pool of elements that are identified by UUID.
- Elements must be locatable by UUID (e.g. for network synchronization,
  serialization references, cross-system lookups).
- Elements have a `Serialization_Header` as their first field.

Do **not** use `UUID_MAPPED__POOL` when:

- Elements are identified by enum key. Use `ENUM_MAP` instead.
- Elements do not need UUID-based lookup. Use a simple array or
  `Sort_List_Manager` instead.
- The pool needs to be dynamically sized. This is a fixed-size pool.

### 1.4.2 Instantiation Pattern

**In a header file**:

    #include "util/hash_map/hash_map.h"

    UUID_MAPPED__POOL(My_Pool, My_Element, 64)
    DECLARE_API__UUID_MAPPED__POOL(My_Pool, My_Element, 64)

Note: Unlike `ENUM_MAP`, all generated functions are `static inline`,
so there is no separate `DEFINE_API` macro needed in a source file.

### 1.4.3 Initialization

    My_Pool my_pool;
    initialize_My_Pool(&my_pool);

After initialization, the `Serialization_Pool` header is configured with
the element count and size. The pool's `p_headers` pointer is set to the
start of the `_values` array.

### 1.4.4 Allocation and Deallocation

    // Allocate
    My_Element *p_element =
        allocate_My_Element_from__My_Pool(&my_pool);
    if (!p_element) {
        // Pool is full
    }

    // Release
    release_My_Element_from__My_Pool(&my_pool, p_element);

### 1.4.5 UUID Lookup (Dehashing)

    My_Element *p_found =
        dehash_p_My_Element_from__My_Pool(
                &my_pool,
                some_uuid);

The `DEHASH` macro uses the UUID and pool metadata to compute an index
into the `_values` array. If the element at that index has a matching
UUID, it is returned directly (O(1)). Otherwise, a linear probe or
similar collision resolution is used.

**Important**: The dehash function accesses
`_values[0]._serialization_header.uuid` as a compile-time check to
ensure the element type has a `Serialization_Header`. This access is
a `(void)` expression and has no runtime effect.

### 1.4.6 Element Lifecycle

    [Pool Initialized]
            |
    allocate_<type_value>_from__<name>
            |
    [Element Allocated, UUID assigned]
            |
        (use element, look up by UUID via dehash)
            |
    release_<type_value>_from__<name>
            |
    [Element Returned to Pool]

### 1.4.7 Relationship to Serialization_Pool

`UUID_MAPPED__POOL` is a typed wrapper around `Serialization_Pool`. The
underlying allocation, deallocation, and dehashing are delegated to:

- `initialize_serialization_pool`
- `allocate_from__serialization_pool`
- `release_from__serialization_pool`
- `DEHASH` (macro from `serialization/hashing.h`)

The generated functions simply cast between `Serialization_Header*` and
`type_value*`.

### 1.4.8 Preconditions

- `initialize_<name>`: pointer must be non-null.
- `allocate_<type_value>_from__<name>`: pool must be initialized.
  Returns null if no free slots remain.
- `release_<type_value>_from__<name>`: the element pointer must have
  been previously allocated from this pool.
- `dehash_p_<type_value>_from__<name>`: the UUID must correspond to a
  currently allocated element. Behavior is undefined for UUIDs not
  present in the pool.

### 1.4.9 Postconditions

- After `initialize_<name>`: pool is ready for allocation. All elements
  are in the free state.
- After `allocate_<type_value>_from__<name>`: the returned element's
  `_serialization_header` is initialized with a UUID and struct size.
- After `release_<type_value>_from__<name>`: the element's slot is
  available for future allocation.

### 1.4.10 Error Handling

- `allocate_<type_value>_from__<name>` returns null on pool exhaustion.
  Callers must check for null.
- `dehash_p_<type_value>_from__<name>` may return null or an incorrect
  element if the UUID is not in the pool. Callers should validate the
  returned pointer.
- No debug-build-specific error handling is generated by these macros;
  error handling is delegated to the underlying `Serialization_Pool`
  functions.

### 1.4.11 Thread Safety

None. UUID-mapped pools are not thread-safe. In the cooperative
scheduling model, this is acceptable since only one process handler
runs at a time.
