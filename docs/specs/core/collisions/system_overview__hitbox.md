# System Overview: Hitbox Management

## Purpose

The hitbox management system provides a type-erased, pooled allocation scheme
for collision primitives. It allows multiple hitbox manager types (e.g. AABB,
future AAABBB) to coexist under a single `Hitbox_Context`, each with its own
pool of hitboxes, while exposing a uniform opaque access interface for
cross-type operations.

## Architecture

### Data Hierarchy

    Game
    +-- Hitbox_Context
        +-- Hitbox_Manager_Instance[0..MAX_QUANTITY_OF__HITBOX_MANAGERS-1]  (8 slots)
        |   +-- Serialization_Header  (UUID identifies this instance)
        |   +-- Hitbox_Manager_Type   (enum tag: AABB, AAABBB, etc.)
        |   +-- void *pVM_hitbox_manager  (opaque pointer to concrete manager)
        |       +-- e.g. Hitbox_AABB_Manager
        |           +-- Hitbox_AABB[0..pool_size-1]  (contiguous pool)
        |           |   +-- Serialization_Header  (UUID identifies this hitbox)
        |           |   +-- Vector__3i32F4 position
        |           |   +-- Vector__3i32F4 velocity
        |           |   +-- Vector__3i16F8 acceleration
        |           |   +-- Quantity__u32 width, height
        |           |   +-- Hitbox_Flags__u8 (active, dirty)
        |           +-- Hitbox_AABB*[] ptr_array_of__hitbox_records  (active tracking)
        |
        +-- Hitbox_Manager_Instance__Invocation_Table[Hitbox_Manager_Type__Unknown]
        |   +-- f_Hitbox_Manager__Allocator
        |   +-- f_Hitbox_Manager__Deallocator
        |   +-- f_Hitbox_Manager__Opaque_Property_Access_Of__Hitbox
        |
        +-- Hitbox_Manager_Registration_Record[Hitbox_Manager_Type__Unknown]
            +-- component sizes (dimensions, pos/vel, acceleration)
            +-- component quantities
            +-- fractional precision metadata

### Key Types

| Type | Role |
|------|------|
| `Hitbox_Context` | Top-level owner. Lives in `Game`. Holds all manager instance slots, invocation tables, and registration records. |
| `Hitbox_Manager_Instance` | A slot representing one allocated manager. Contains a UUID, a type tag, and an opaque pointer to the concrete manager. |
| `Hitbox_Manager_Instance__Invocation_Table` | Function pointer table for a registered manager type. Indexed by `Hitbox_Manager_Type`. |
| `Hitbox_Manager_Registration_Record` | Metadata describing the component layout of a registered manager type. Indexed by `Hitbox_Manager_Type`. |
| `Hitbox_Manager_Intrinsic` | Interface contract. Any concrete manager's opaque pointer must be safely castable to this struct. |
| `Hitbox_AABB_Manager` | Concrete manager for AABB hitboxes. Implements `Hitbox_Manager_Intrinsic` via union. |
| `Hitbox_AABB` | The AABB collision primitive. Contains position, velocity, acceleration, dimensions, and flags. |
| `Hitbox_Flags__u8` | Bitmask for hitbox state (active, dirty). |
| `Hitbox_Manager_Type` | Enum discriminating manager types: `AABB`, `AAABBB`, `Unknown`. |

### Limits

| Macro | Default | Description |
|-------|---------|-------------|
| `MAX_QUANTITY_OF__HITBOX_MANAGERS` | 8 | Maximum concurrent manager instances in `Hitbox_Context`. |
| `MAX_QUANTITY_OF__HITBOX` | 256 | Collective hitbox limit across all manager pools. |
| `MAX_QUANTITY_OF__HITBOX_AABB` | 256 | Maximum AABB hitboxes per manager. |

## Lifecycle

### 1. Initialization

    initialize_hitbox_context(&game.hitbox_context)
        -> All Hitbox_Manager_Instance slots marked as deallocated.
        -> Invocation tables and registration records zeroed.

    register_hitbox_managers(&game.hitbox_context)
        -> Calls register_hitbox_manager(...) for each built-in type.
        -> For AABB: registers f_hitbox_manager__allocator_AABB,
           f_hitbox_manager__deallocator_AABB,
           f_hitbox_manager__opaque_property_access_of__hitbox_AABB.
        -> Populates Hitbox_Manager_Registration_Record with component metadata.

### 2. Manager Allocation

    Hitbox_Manager_Instance *p_instance =
        allocate_hitbox_manager_from__hitbox_context(
            &hitbox_context,
            uuid,
            Hitbox_Manager_Type__AABB,
            pool_size);

        -> Finds a free Hitbox_Manager_Instance slot.
        -> Invokes f_hitbox_manager__allocator_AABB(type, pool_size).
        -> Stores the returned opaque pointer in pVM_hitbox_manager.
        -> Sets the UUID and type tag.

### 3. Hitbox Allocation

    Hitbox_AABB *p_hitbox = (Hitbox_AABB*)
        allocate_pV_hitbox_from__hitbox_context(
            &hitbox_context,
            manager_uuid,
            hitbox_uuid);

        -> Resolves manager instance by UUID.
        -> Casts pVM_hitbox_manager to Hitbox_Manager_Intrinsic.
        -> Finds a free slot in the pool via UUID hashing.
        -> Returns opaque pointer (caller casts to Hitbox_AABB*).

### 4. Per-Frame Update

    poll_hitbox_manager_for__movement(p_game, p_hitbox_aabb_manager);
        -> For each active Hitbox_AABB:
            -> acceleration is added to velocity.
            -> velocity is added to position.
            -> Hitbox is marked dirty.

    poll_collision_resolver_aabb(
        p_game,
        p_hitbox_aabb_manager,
        f_collision_handler,
        f_tile_touch_handler);
        -> For each active Hitbox_AABB:
            -> Check entity-entity collisions via Collision_Node.
            -> Check entity-tile collisions via Local_Space_Manager.
            -> Invoke handlers for each detected collision.

### 5. Cleanup

    release_hitbox_aabb_from__hitbox_aabb_manager(p_game, p_manager, p_hitbox);
        -> Deinitializes the hitbox.
        -> Removes from pointer array.

    release_hitbox_manager_from__hitbox_context(&hitbox_context, manager_uuid);
        -> Invokes f_hitbox_manager__deallocator_AABB.
        -> Marks the Hitbox_Manager_Instance slot as deallocated.

## Opaque Property Access

The `opaque_access_to__hitbox` function provides type-erased get/set access
to any hitbox through the `Hitbox_Context`. This is useful for cross-type code
(e.g. game actions that operate on hitboxes without knowing their concrete type).

    opaque_access_to__hitbox(
        &hitbox_context,
        manager_uuid,
        hitbox_uuid,
        pV_OPTIONAL_dimensions,    // NULL to skip
        pV_OPTIONAL_position,      // NULL to skip
        pV_OPTIONAL_velocity,      // NULL to skip
        pV_OPTIONAL_acceleration,  // NULL to skip
        p_OPTIONAL_hitbox_flags,   // NULL to skip
        OPAQUE_HITBOX_ACCESS__SET  // or OPAQUE_HITBOX_ACCESS__GET
    );

**Performance warning**: This call is relatively expensive. It resolves the
manager instance, looks up the hitbox, and invokes the registered opaque access
callback. The callback assumes the hitbox is dirty after any call, even reads.
Prefer direct type-specific access when the hitbox type is known.

## Type Registration Contract

Any hitbox manager type registered with `Hitbox_Context` must satisfy:

1. The opaque pointer (`pVM_hitbox_manager`) must be safely castable to
   `Hitbox_Manager_Intrinsic`:

        typedef struct Hitbox_Manager_Intrinsic_t {
            Quantity__u32 quantity_of__hitboxes;
            Serialization_Header *p_array_of__hitboxes;
        } Hitbox_Manager_Intrinsic;

2. The allocator callback must return a pointer satisfying (1).

3. The opaque property access callback must correctly interpret the void
   pointers according to the `Hitbox_Manager_Registration_Record` metadata.

## Fixed-Point Conventions

| Component | Type | Fractional Bits | Description |
|-----------|------|-----------------|-------------|
| Position | `Vector__3i32F4` | 4 | Center of the hitbox in world-space. |
| Velocity | `Vector__3i32F4` | 4 | Per-tick displacement. |
| Acceleration | `Vector__3i16F8` | 8 | Per-tick velocity change. |
| Dimensions | `Quantity__u32` | 0 | Full width and height (integer). |

## Dirty Flag Semantics

The `HITBOX_FLAG__IS_DIRTY` bit indicates that the hitbox's state has changed
since the last time it was processed. The collision system uses this flag to
determine which hitboxes need re-evaluation.

- **Set by**: Any setter function (position, velocity, acceleration, dimensions).
- **Cleared by**: The collision resolver or movement poll after processing.
- **Checked by**: Collision resolver, rendering system, collision node updates.

Note: `apply_*_velocity` functions (which accumulate velocity) do **not** set
the dirty flag. The movement poll handles dirtying when it integrates velocity
into position.

## Relationship to Collision Nodes

Hitboxes are spatially indexed via `Collision_Node` entries (see
`system_overview__collision_node.md`). When a hitbox moves between chunks, its
`Collision_Node_Entry` must be removed from the old node and added to the new
node. This is managed externally (typically by the entity system or game action
handlers), not by the hitbox management system itself.

The `Collision_Node_Entry.uuid_of__hitbox__u32` field references the hitbox's
UUID, which is resolved to a `Hitbox_AABB*` via the `Hitbox_AABB_Manager`
during collision polling.
