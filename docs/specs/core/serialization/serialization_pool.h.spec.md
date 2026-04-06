# 1. Specification: core/include/serialization/serialization_pool.h

## 1.1 Overview

Provides a thin wrapper around contiguous arrays of serialized structs,
abstracting pool initialization, allocation, deallocation, and UUID-based
lookup. `Serialization_Pool` stores the array metadata (element count, element
size, base pointer) and delegates to the hashing module for UUID operations.

## 1.2 Dependencies

- `defines.h` (for `Serialization_Pool`, `Serialization_Header`,
  `Identifier__u32`, `Quantity__u32`)
- `defines_weak.h` (forward declarations)
- `serialization/hashing.h` (for `dehash_identitier_u32_in__contigious_array`)

## 1.3 Types

### 1.3.1 Serialization_Pool

    typedef struct Serialization_Pool_t {
        Quantity__u32 quantity_of__pool_elements;
        Quantity__u32 size_of__element;
        Serialization_Header *p_headers;
    } Serialization_Pool;

| Field | Type | Description |
|-------|------|-------------|
| `quantity_of__pool_elements` | `Quantity__u32` | Number of elements in the pool. |
| `size_of__element` | `Quantity__u32` | Byte size of each element (must match `Serialization_Header.size_of__struct`). |
| `p_headers` | `Serialization_Header*` | Pointer to the base of the contiguous array. |

## 1.4 Functions

### 1.4.1 Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_serialization_pool` | `(Serialization_Pool*, Quantity__u32 quantity, Quantity__u32 element_size) -> void` | Sets the pool metadata. Does NOT allocate memory; the backing array must be provided externally. Initializes all headers in the array as deallocated. |

### 1.4.2 Allocation / Deallocation

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `allocate_from__serialization_pool` | `(Serialization_Pool*) -> Serialization_Header*` | `Serialization_Header*` or `NULL` | Finds the next available (deallocated) slot in the pool and returns it. Does NOT set the UUID; the caller must do so. |
| `release_from__serialization_pool` | `(Serialization_Pool*, Serialization_Header*) -> void` | `void` | Marks the given header as deallocated. |

### 1.4.3 Lookup (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `dehash_from__serialization_pool` | `(Serialization_Pool*, Identifier__u32 uuid) -> Serialization_Header*` | `Serialization_Header*` or `NULL` | Looks up a struct by UUID using `dehash_identitier_u32_in__contigious_array`. The length passed to the dehash function is `quantity_of__pool_elements * size_of__element`. |

### 1.4.4 Hash-Based Allocation (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `allocate_by_hash_in__serialization_pool` | `(Serialization_Pool*, Identifier__u32 uuid) -> void` | Finds the slot for the given UUID via dehashing and sets its UUID. This is a combined lookup + allocate for when the UUID is already known. |

## 1.5 Agentic Workflow

### 1.5.1 When to use this module

- Use `Serialization_Pool` when you need a simple, generic pool manager
  for a contiguous array of structs with `Serialization_Header` as their
  first field.
- For specialized pools (e.g. `Hitbox_AABB_Manager`, `Entity_Manager`),
  the managers typically implement their own pool logic directly rather
  than using `Serialization_Pool`.

### 1.5.2 Lifecycle

1. **Declare** the backing array and `Serialization_Pool` struct.
2. **Initialize** with `initialize_serialization_pool(...)`.
3. **Allocate** elements with `allocate_from__serialization_pool` or
   `allocate_by_hash_in__serialization_pool`.
4. **Lookup** elements with `dehash_from__serialization_pool`.
5. **Release** elements with `release_from__serialization_pool`.

### 1.5.3 Preconditions

- The backing array must be allocated externally and must be contiguous.
- `size_of__element` must exactly match the size of the structs in the array.
- `Serialization_Header` must be the first field of each struct.

### 1.5.4 Postconditions

- After `initialize_serialization_pool`: all elements are deallocated.
- After `allocate_from__serialization_pool`: the returned header is ready
  for UUID assignment.
- After `release_from__serialization_pool`: the element's UUID is
  `IDENTIFIER__UNKNOWN__u32`.

### 1.5.5 Error Handling

- `allocate_from__serialization_pool` returns `NULL` if the pool is full.
- `dehash_from__serialization_pool` returns `NULL` if the UUID is not found.
- `allocate_by_hash_in__serialization_pool` silently does nothing if the
  dehash returns null.
