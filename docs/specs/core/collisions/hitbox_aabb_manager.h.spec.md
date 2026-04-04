# Specification: core/include/collisions/core/aabb/hitbox_aabb_manager.h

## Overview

Provides pool management, allocation, deallocation, UUID-based lookup, and
physics integration for `Hitbox_AABB` instances. The `Hitbox_AABB_Manager`
is the concrete manager for AABB hitboxes and conforms to the
`Hitbox_Manager_Intrinsic` interface via a union cast, allowing it to be
used through the `Hitbox_Context` abstraction layer.

This manager also provides the factory and opaque-access callbacks required
by the `Hitbox_Context` registration system.

See `module_topology__collision.mmd` for the type hierarchy.

## Dependencies

- `defines.h` (for `Hitbox_AABB_Manager`, `Hitbox_AABB`,
  `Hitbox_Manager_Type`, `Hitbox_Flags__u8`, `Identifier__u32`,
  `Quantity__u32`, `Index__u32`, `Entity`, `Game`, `Vector__3i32`,
  `Vector__3i32F4`, `Vector__3i16F8`)
- `defines_weak.h` (forward declarations)
- `serialization/hashing.h` (for UUID-based lookup)

## Types

### Hitbox_AABB_Manager (struct)

Defined in `defines.h`:

    typedef struct Hitbox_AABB_Manager_t {
        union {
            Hitbox_Manager_Intrinsic _intrinsic;
            struct {
                Quantity__u32 quantity_of__hitboxes;
                Hitbox_AABB *pM_pool_of__hitboxes;
            };
        };
        Hitbox_AABB **pM_ptr_array_of__hitbox_records;
        Index__u32 index_of__next_hitbox_aabb_in__records;
    } Hitbox_AABB_Manager;

| Field | Type | Description |
|-------|------|-------------|
| `quantity_of__hitboxes` | `Quantity__u32` | Maximum number of hitboxes in the pool. |
| `pM_pool_of__hitboxes` | `Hitbox_AABB*` | Pointer to the contiguous array of `Hitbox_AABB` instances. Dynamically allocated by the factory. |
| `pM_ptr_array_of__hitbox_records` | `Hitbox_AABB**` | Pointer array for active hitbox tracking. Dynamically allocated by the factory. |
| `index_of__next_hitbox_aabb_in__records` | `Index__u32` | Tracks the next available slot in the pointer array for allocation. |

### Hitbox_Manager_Intrinsic (struct)

Defined in `defines.h`:

    typedef struct Hitbox_Manager_Intrinsic_t {
        Quantity__u32 quantity_of__hitboxes;
        Serialization_Header *p_array_of__hitboxes;
    } Hitbox_Manager_Intrinsic;

The `Hitbox_AABB_Manager` can be safely cast to `Hitbox_Manager_Intrinsic*`
via the union. This is the interface contract that all hitbox managers must
satisfy for use with CORE.

## Functions

### Hitbox_Context Registration Callbacks

These functions are registered with `Hitbox_Context` via
`register_hitbox_manager` and are invoked through the invocation table.

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `f_hitbox_manager__allocator_AABB` | `(Hitbox_Manager_Type, Quantity__u32 quantity) -> void*` | `void*` | Factory function. Allocates a `Hitbox_AABB_Manager` and its backing pools (`pM_pool_of__hitboxes`, `pM_ptr_array_of__hitbox_records`) using `malloc`. Returns the manager as an opaque pointer. |
| `f_hitbox_manager__deallocator_AABB` | `(void* pM_hitbox_manager, Hitbox_Manager_Type) -> void` | `void` | Frees the backing pools and the manager itself using `free`. |
| `f_hitbox_manager__opaque_property_access_of__hitbox_AABB` | `(void* pV_hitbox, void* pV_dims, void* pV_pos, void* pV_vel, void* pV_acc, Hitbox_Flags__u8*, bool is_set) -> bool` | `bool` | Opaque property accessor. Reads or writes hitbox properties through void pointers. Used by `Hitbox_Context.opaque_access_to__hitbox`. |

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_hitbox_aabb_manager` | `(Hitbox_AABB_Manager*, void* pM_pool, void** pM_ptr_array, Quantity__u32 quantity) -> void` | Initializes the manager with pre-allocated pool and pointer array. Sets all hitboxes to unallocated state. |

### Allocation

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `allocate_hitbox_aabb_from__hitbox_aabb_manager` | `(Hitbox_AABB_Manager*, Identifier__u32 uuid) -> Hitbox_AABB*` | `Hitbox_AABB*` | Allocates a hitbox from the pool with the given UUID. Returns NULL if the pool is exhausted. |
| `release_hitbox_aabb_from__hitbox_aabb_manager` | `(Game*, Hitbox_AABB_Manager*, Hitbox_AABB*) -> void` | `void` | Returns the hitbox to the pool. Marks it as deallocated. |

### Lookup

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager` | `(Hitbox_AABB_Manager*, Identifier__u32 uuid) -> Hitbox_AABB*` | `Hitbox_AABB*` | Looks up a hitbox by its 32-bit UUID. Returns NULL if not found. |

### Physics Integration

| Function | Signature | Description |
|----------|-----------|-------------|
| `poll_hitbox_manager_for__movement` | `(Game*, Hitbox_AABB_Manager*) -> void` | Iterates all active hitboxes. For each: applies acceleration to velocity, applies velocity to position, and marks the hitbox as dirty if it moved. |

### Convenience Accessors (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_p_hitbox_aabb_by__entity_from__hitbox_aabb_manager` | `(Hitbox_AABB_Manager*, Entity*) -> Hitbox_AABB*` | `Hitbox_AABB*` | Looks up a hitbox using the entity's UUID. Delegates to `get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager`. |
| `get_p_hitbox_aabb_by__index_from__hitbox_aabb_manager` | `(Hitbox_AABB_Manager*, Index__u32) -> Hitbox_AABB*` | `Hitbox_AABB*` | Returns the hitbox at the given index in the pointer array. Debug builds check bounds and call `debug_error` on overflow. |

## Agentic Workflow

### Manager Lifecycle

    [Uninitialized]
        |
        f_hitbox_manager__allocator_AABB(type, quantity)
            -> malloc pool, ptr_array, manager
            -> initialize_hitbox_aabb_manager(...)
        |
    [Initialized, Empty Pool]
        |
        allocate_hitbox_aabb_from__hitbox_aabb_manager(mgr, uuid)
        |
    [Has Allocated Hitboxes]
        |
        poll_hitbox_manager_for__movement(game, mgr)  // each tick
        |
        release_hitbox_aabb_from__hitbox_aabb_manager(game, mgr, hitbox)
        |
    [Pool Partially/Fully Free]
        |
        f_hitbox_manager__deallocator_AABB(mgr, type)
            -> free pool, ptr_array, manager
        |
    [Deallocated]

### Integration with Hitbox_Context

The `Hitbox_AABB_Manager` is not used directly by most game code. Instead,
it is accessed through the `Hitbox_Context` abstraction:

    // Registration (once, during initialization):
    register_hitbox_manager(
        p_hitbox_context,
        f_hitbox_manager__allocator_AABB,
        f_hitbox_manager__deallocator_AABB,
        f_hitbox_manager__opaque_property_access_of__hitbox_AABB,
        Hitbox_Manager_Type__AABB,
        ...);

    // Allocation (via Hitbox_Context):
    Hitbox_Manager_Instance *p_instance =
        allocate_hitbox_manager_from__hitbox_context(
            p_hitbox_context, uuid, Hitbox_Manager_Type__AABB, quantity);

    // The instance's pVM_hitbox_manager points to the Hitbox_AABB_Manager.

### Physics Tick Sequence

    1. poll_hitbox_manager_for__movement(p_game, p_hitbox_aabb_manager)
       -> For each active hitbox:
          -> velocity += acceleration (with precision conversion)
          -> position += velocity
          -> mark dirty if moved

    2. poll_collision_resolver_aabb(...)
       -> Uses dirty flags to optimize checks

### Preconditions

- `initialize_hitbox_aabb_manager`: All pointer arguments must be non-null.
  `quantity` must be > 0.
- `allocate_hitbox_aabb_from__hitbox_aabb_manager`: The pool must have
  available slots.
- `release_hitbox_aabb_from__hitbox_aabb_manager`: The hitbox must have been
  previously allocated from this manager.
- `get_p_hitbox_aabb_by__index_from__hitbox_aabb_manager`: `index_of__hitbox`
  must be less than `quantity_of__hitboxes`.

### Postconditions

- After `allocate_hitbox_aabb_from__hitbox_aabb_manager` (success): The
  returned hitbox has the requested UUID and is marked as allocated.
- After `release_hitbox_aabb_from__hitbox_aabb_manager`: The hitbox slot is
  available for reuse.
- After `poll_hitbox_manager_for__movement`: All active hitboxes have updated
  positions reflecting their velocity and acceleration.

### Error Handling

- `allocate_hitbox_aabb_from__hitbox_aabb_manager` returns NULL on pool
  exhaustion.
- `get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager` returns NULL
  if the UUID is not found.
- `get_p_hitbox_aabb_by__index_from__hitbox_aabb_manager` calls
  `debug_error` and returns 0 on out-of-bounds access in debug builds.
