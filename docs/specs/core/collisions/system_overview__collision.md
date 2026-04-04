# System Overview: Collision System

## Purpose

The collision system provides hitbox management, chunk-aligned spatial
partitioning, and collision detection/resolution for the engine. It is
split across two owners — `Hitbox_Context` (owned by `Game`) for hitbox
type registration and allocation, and `Collision_Node_Pool` (owned by
`World`) for spatial indexing — enabling efficient narrowing of collision
candidates to only those hitboxes sharing the same chunk.

## Architecture

### Ownership Split

    Game
    ├── Hitbox_Context                    (hitbox type system + manager pool)
    │   ├── Hitbox_Manager_Instance[0..MAX]
    │   │   └── void *pVM_hitbox_manager  (opaque pointer to concrete manager)
    │   ├── Hitbox_Manager_Instance__Invocation_Table[per Hitbox_Manager_Type]
    │   │   ├── f_hitbox_manager__allocator
    │   │   ├── f_hitbox_manager__deallocator
    │   │   └── f_hitbox_manager__get_properties_of__hitbox
    │   └── Hitbox_Manager_Registration_Record[per Hitbox_Manager_Type]
    │       ├── size/quantity of dimension components
    │       ├── size/quantity of position/velocity components
    │       └── size/quantity of acceleration components
    │
    └── World* (pM_world)
        ├── Collision_Node_Pool           (spatial partitioning)
        │   ├── Collision_Node[QUANTITY_OF__GLOBAL_SPACE]
        │   │   └── Collision_Node_Entry* (linked list of hitbox refs)
        │   └── Collision_Node_Entry[MAX_QUANTITY_OF__HITBOX_AABB]
        │
        ├── Global_Space_Manager
        │   └── Global_Space[]
        │       ├── Chunk_Vector__3i32
        │       └── Collision_Node*       (→ node in pool)
        │
        ├── Entity_Manager
        │   └── Entity[]                  (UUID matches Collision_Node_Entry.uuid)
        │
        ├── f_Hitbox_AABB_Collision_Handler   (entity-entity callback)
        └── f_Hitbox_AABB_Tile_Touch_Handler  (entity-tile callback)

### Why Two Owners?

The `Hitbox_Context` lives in `Game` because hitbox type registration
and the manager pool are global concerns that persist across world
loads/unloads. The `Collision_Node_Pool` lives in `World` because
spatial partitioning is tied to the currently loaded set of chunks —
when the world is deallocated, all spatial indexing is invalidated.

## Hitbox Type System

### Registration

The `Hitbox_Context` supports multiple hitbox manager types through a
registration pattern. Each `Hitbox_Manager_Type` (an enum) has:

1. A **Registration Record** describing the component layout (dimension
   sizes, position/velocity sizes, acceleration sizes, fractional
   precision).
2. An **Invocation Table** with function pointers for allocation,
   deallocation, and opaque property access.

Registration is performed at initialization:

    register_hitbox_manager(
        &hitbox_context,
        Hitbox_Manager_Type__AABB,
        registration_record,
        invocation_table);

### Manager Instances

`Hitbox_Manager_Instance` is a slot in the `Hitbox_Context` pool. Each
instance holds:

- A `Serialization_Header` for UUID-based lookup.
- An opaque `void *pVM_hitbox_manager` pointing to the concrete manager
  (e.g. `Hitbox_AABB_Manager`).
- A `Hitbox_Manager_Type` discriminator.

The opaque pointer pattern allows the `Hitbox_Context` to manage
different hitbox types uniformly without knowing their concrete layouts.

### Hitbox_AABB_Manager (Concrete Manager)

The default concrete manager for axis-aligned bounding boxes:

    Hitbox_AABB_Manager
    ├── Hitbox_AABB *pM_pool_of__hitboxes     (pool array)
    ├── Hitbox_AABB **pM_ptr_array_of__hitbox_records  (sorted pointers)
    ├── Quantity__u32 quantity_of__hitboxes
    └── Index__u32 index_of__next_hitbox_aabb_in__records

Each `Hitbox_AABB` contains:

| Field | Type | Description |
|-------|------|-------------|
| `_serialization_header` | `Serialization_Header` | UUID for pool lookup. |
| `position__3i32F4` | `Vector__3i32F4` | Current position (fixed-point). |
| `velocity__3i32F4` | `Vector__3i32F4` | Current velocity (fixed-point). |
| `acceleration__3i16F8` | `Vector__3i16F8` | Acceleration (compact fixed-point). |
| `width__quantity_u32` | `Quantity__u32` | Hitbox width. |
| `height__quantity_u32` | `Quantity__u32` | Hitbox height. |
| `hitbox_aabb_flags__u8` | `Hitbox_Flags__u8` | Active/dirty flags. |

### Hitbox_Manager_Intrinsic

All concrete hitbox managers share a common leading layout
(`Hitbox_Manager_Intrinsic`) via union cast, enabling the `Hitbox_Context`
to access basic properties (quantity, serialization header array) without
knowing the concrete type:

    Hitbox_Manager_Intrinsic
    ├── Quantity__u32 quantity_of__hitboxes
    └── Serialization_Header *p_array_of__hitboxes

### Opaque Access

The `Hitbox_Context` provides opaque access to hitbox properties through
the invocation table:

    opaque_access_to__hitbox(
        &hitbox_context,
        hitbox_manager_type,
        hitbox_uuid,
        &hitbox_properties);

This resolves the hitbox through the correct manager and fills a
properties struct without the caller needing to know the concrete type.

## Spatial Partitioning

### Collision Nodes

The `Collision_Node_Pool` provides chunk-aligned spatial buckets. Each
loaded chunk (`Global_Space`) is associated with exactly one
`Collision_Node`. Each node maintains a singly-linked list of
`Collision_Node_Entry` records, each referencing a hitbox by UUID.

    +-------------+-------------+-------------+
    | Chunk(0,1)  | Chunk(1,1)  | Chunk(2,1)  |
    | Node: CN_A  | Node: CN_B  | Node: CN_C  |
    | Entries: 0  | Entries: 2  | Entries: 1  |
    +-------------+-------------+-------------+
    | Chunk(0,0)  | Chunk(1,0)  | Chunk(2,0)  |
    | Node: CN_D  | Node: CN_E  | Node: CN_F  |
    | Entries: 1  | Entries: 3  | Entries: 0  |
    +-------------+-------------+-------------+

Nodes use 64-bit UUIDs derived from chunk coordinates for O(1) lookup
via hashing.

### Linked List Structure

Each `Collision_Node` maintains entries linked from tail to head:

    Collision_Node
      └── p_linked_list__collision_node_entries__tail
          └── Entry_C (uuid: 0x003)
              └── p_previous_entry
                  └── Entry_B (uuid: 0x007)
                      └── p_previous_entry
                          └── Entry_A (uuid: 0x001)
                              └── p_previous_entry = NULL (head)

New entries are appended at the tail. Removal unlinks the entry and
returns it to the pool.

### Entry Migration

When a hitbox moves to a different chunk, its `Collision_Node_Entry`
must be migrated:

    remove_entry_from__collision_node(pool, old_node, hitbox_uuid)
    add_entry_to__collision_node(pool, new_node, chunk_vector, hitbox_uuid)

## Collision Detection Flow

### Per-Frame Resolution

The collision resolver drives the full detection loop each frame:

    For each active Hitbox_AABB in Hitbox_AABB_Manager:
        1. Determine which Global_Space the hitbox occupies
           (from chunk coordinates derived from hitbox position).
        2. Get the Global_Space's Collision_Node.
        3. Entity-entity collisions:
           poll_for__collisions_within_this__collision_node(...)
             → Iterate all entries in the node.
             → Resolve each entry's UUID to a Hitbox_AABB.
             → Call is_hitbox_aabb__colliding(subject, candidate).
             → If colliding, invoke f_hitbox_aabb_collision_handler.
        4. Entity-tile collisions:
           poll_hitbox_aabb_for__tile_collision(...)
             → Check tiles via Local_Space_Manager.
             → If touching, invoke f_hitbox_aabb_tile_touch_handler.

### Physics Integration

The `Hitbox_AABB_Manager` handles physics integration separately from
collision detection:

    poll_hitbox_manager_for__movement(...)
         → For each active hitbox:
              velocity += acceleration
              position += velocity

This runs before collision detection each frame.

## Lifecycle

### Initialization

    initialize_hitbox_context(&game.hitbox_context)
         → Clear all manager instance slots.
         → Clear all invocation tables and registration records.

    register_hitbox_manager(&hitbox_context, type, record, table)
         → Register each supported hitbox type.

    initialize_collision_node_pool(&world.collision_node_pool)
         → All node slots: UUID-64 set to deallocated sentinel.
         → All entry slots: marked as available.

### Chunk Load

    allocate_collision_node_from__collision_node_pool(pool, uuid_from_chunk)
    initialize_collision_node(p_node, uuid_from_chunk)
    global_space.p_collision_node = p_node

### Hitbox Allocation

    allocate_hitbox_manager_from__hitbox_context(&hitbox_context, type)
         → Allocates a Hitbox_Manager_Instance slot.
         → Calls the type's allocator via invocation table.
         → Returns the opaque manager pointer.

    allocate_pV_hitbox_from__hitbox_context(&hitbox_context, manager_uuid)
         → Allocates a hitbox from the specified manager.
         → Returns opaque hitbox pointer.

### Hitbox Enters Chunk

    add_entry_to__collision_node(pool, p_node, chunk_vector, hitbox_uuid)
         → Allocates a Collision_Node_Entry from the pool.
         → Appends to the node's linked list tail.

### Hitbox Leaves Chunk

    remove_entry_from__collision_node(pool, p_node, hitbox_uuid)
         → Finds entry by UUID in linked list.
         → Unlinks and returns to pool.

### Chunk Unload

    release_collision_node_from__collision_node_pool(pool, p_node)
         → All entries should have been removed prior.
         → Node slot marked as deallocated.
         → global_space.p_collision_node = NULL

### Hitbox Deallocation

    release_hitbox_manager_from__hitbox_context(&hitbox_context, manager_uuid)
         → Calls the type's deallocator via invocation table.
         → Frees the Hitbox_Manager_Instance slot.

## Entity Iteration via Collision Nodes

The collision node system supports spatial entity queries:

    Collision_Node_Entry *p_entry =
        p_collision_node->p_linked_list__collision_node_entries__tail;
    Entity *p_entity = NULL;

    while (iterate_entities_in__collision_node_entry(
            p_entity_manager, &p_entry, &p_entity)) {
        // p_entity is valid for this iteration
    }

This resolves each entry's `uuid_of__hitbox__u32` to an `Entity` via
the `Entity_Manager`, enabling queries like "find all entities in this
chunk."

## Capacity Constraints

| Resource | Pool Size | Determined By |
|----------|-----------|---------------|
| `Collision_Node` | `QUANTITY_OF__GLOBAL_SPACE` | Number of simultaneously loaded chunks. |
| `Collision_Node_Entry` | `MAX_QUANTITY_OF__HITBOX_AABB` (256) | Maximum number of AABB hitboxes. |
| `Hitbox_Manager_Instance` | `MAX_QUANTITY_OF__HITBOX_MANAGERS` | Maximum concurrent hitbox managers. |
| `Hitbox_AABB` | `MAX_QUANTITY_OF__HITBOX_AABB` (256) | Per-manager hitbox pool. |

Each hitbox occupies exactly one `Collision_Node_Entry` at a time. If a
hitbox straddles a chunk boundary, it is assigned to the chunk containing
its center position. Cross-boundary collisions are handled by checking
adjacent collision nodes during resolution.

## Hitbox Kinds

The `Hitbox_Kind` enum defines supported hitbox shapes:

| Kind | Description |
|------|-------------|
| `Hitbox_Kind__Opaque` | Opaque/unknown hitbox (no collision). |
| `Hitbox_Kind__AABB` | Axis-aligned bounding box. |
| `Hitbox_Kind__Unknown` | Sentinel/invalid value. |

Additional kinds (AAABBB, Ball, Sphere) are reserved but not yet
implemented.

## Relationship Summary

| Concern | Managed By |
|---------|------------|
| Hitbox type registration | `Hitbox_Context` |
| Hitbox manager allocation/deallocation | `Hitbox_Context` |
| Hitbox allocation/deallocation | Concrete manager via `Hitbox_Context` invocation table |
| Hitbox property access (opaque) | `Hitbox_Context` invocation table |
| Spatial indexing by chunk | `Collision_Node_Pool` (in `World`) |
| Physics integration (velocity → position) | `Hitbox_AABB_Manager.poll_hitbox_manager_for__movement` |
| Collision detection and response | Collision resolver + `Collision_Node` iteration |
| Collision node entry migration | External (entity system / game action handlers) |

The `Collision_Node_Entry.uuid_of__hitbox__u32` is the bridge between
the spatial partitioning system and the hitbox management system: it
references a `Hitbox_AABB` by UUID, which is resolved through the
`Hitbox_AABB_Manager` during collision polling.
