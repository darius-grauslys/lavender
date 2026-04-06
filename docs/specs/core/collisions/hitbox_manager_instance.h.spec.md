# 1 Specification: core/include/collisions/hitbox_manager_instance.h

## 1.1 Overview

Provides initialization and validation for the `Hitbox_Manager_Instance`
struct — a slot in the `Hitbox_Context`'s manager instance pool. Each
instance holds an opaque pointer to a concrete hitbox manager (e.g.
`Hitbox_AABB_Manager`) along with its type discriminator and UUID.

This is a thin wrapper focused on lifecycle management of individual
manager instance slots.

See `module_topology__collision.mmd` for the type hierarchy.

## 1.2 Dependencies

- `defines.h` (for `Hitbox_Manager_Instance`, `Hitbox_Manager_Type`,
  `Identifier__u32`)
- `defines_weak.h` (forward declarations)
- `serialization/identifiers.h` (for `is_identifier_u32__invalid`)

## 1.3 Types

### 1.3.1 Hitbox_Manager_Instance (struct)

Defined in `defines.h`:

    typedef struct Hitbox_Manager_Instance_t {
        Serialization_Header _serialization_header;
        void *pVM_hitbox_manager;
        Hitbox_Manager_Type type_of__hitbox_manager;
    } Hitbox_Manager_Instance;

| Field | Type | Description |
|-------|------|-------------|
| `_serialization_header` | `Serialization_Header` | UUID and struct size. UUID is `IDENTIFIER__UNKNOWN__u32` when deallocated. |
| `pVM_hitbox_manager` | `void*` | Opaque pointer to the concrete hitbox manager. NULL when deallocated. |
| `type_of__hitbox_manager` | `Hitbox_Manager_Type` | Discriminator for the concrete manager type. |

## 1.4 Functions

### 1.4.1 Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_hitbox_manager_instance_as__deallocated` | `(Hitbox_Manager_Instance*) -> void` | Sets the instance to the deallocated state: UUID set to `IDENTIFIER__UNKNOWN__u32`, `pVM_hitbox_manager` set to NULL. |
| `initialize_hitbox_manager_instance_as__allocated` | `(Hitbox_Manager_Instance*, void* pM_hitbox_manager, Identifier__u32 uuid, Hitbox_Manager_Type type) -> void` | Sets the instance to the allocated state with the given opaque manager pointer, UUID, and type. |

### 1.4.2 Validation (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_p_hitbox_manager_instance__valid` | `(Hitbox_Manager_Instance*) -> bool` | `bool` | Returns true if: (1) the pointer is non-null, (2) the UUID is not `IDENTIFIER__UNKNOWN__u32`, and (3) `pVM_hitbox_manager` is non-null. |

## 1.5 Agentic Workflow

### 1.5.1 Instance Slot Lifecycle

    [Uninitialized]
        |
        initialize_hitbox_manager_instance_as__deallocated(p_instance)
        |
    [Deallocated]
        |
        is_p_hitbox_manager_instance__valid(p_instance) -> false
        |
        initialize_hitbox_manager_instance_as__allocated(
            p_instance, p_concrete_manager, uuid, type)
        |
    [Allocated]
        |
        is_p_hitbox_manager_instance__valid(p_instance) -> true
        |
        initialize_hitbox_manager_instance_as__deallocated(p_instance)
        |
    [Deallocated]

### 1.5.2 Usage by Hitbox_Context

The `Hitbox_Context` manages an array of `Hitbox_Manager_Instance` slots.
When allocating a new hitbox manager:

    1. Find a deallocated slot (is_p_hitbox_manager_instance__valid == false).
    2. Invoke the registered allocator callback to create the concrete manager.
    3. Call initialize_hitbox_manager_instance_as__allocated with the result.

When releasing:

    1. Find the slot by UUID.
    2. Invoke the registered deallocator callback.
    3. Call initialize_hitbox_manager_instance_as__deallocated.

### 1.5.3 Preconditions

- `initialize_hitbox_manager_instance_as__deallocated`:
  `p_hitbox_manager_instance` must be non-null.
- `initialize_hitbox_manager_instance_as__allocated`:
  `p_hitbox_manager_instance` must be non-null. `pM_hitbox_manager` should
  be non-null for a valid instance.
- `is_p_hitbox_manager_instance__valid`: Handles null
  `p_hitbox_manager_instance` gracefully (returns false).

### 1.5.4 Postconditions

- After `initialize_hitbox_manager_instance_as__deallocated`:
  `is_p_hitbox_manager_instance__valid` returns false.
- After `initialize_hitbox_manager_instance_as__allocated` (with valid args):
  `is_p_hitbox_manager_instance__valid` returns true.

### 1.5.5 Error Handling

- `is_p_hitbox_manager_instance__valid` returns false for null pointers
  without error. This is by design for safe iteration over the instance pool.
