# System Overview: Collision Node Spatial Partitioning

## Purpose

The collision node system provides chunk-aligned spatial partitioning for
hitbox collision detection. Each loaded chunk (`Global_Space`) is associated
with a `Collision_Node` that tracks which hitboxes currently occupy that
chunk's spatial region. This allows the collision resolver to efficiently
narrow down collision candidates to only those hitboxes sharing the same
chunk.

## Architecture

### Data Hierarchy

    World
    +-- Collision_Node_Pool
    |   +-- Collision_Node[0..QUANTITY_OF__GLOBAL_SPACE-1]  (node pool)
    |   |   +-- Serialization_Header__UUID_64  (derived from chunk coordinates)
    |   |   +-- Collision_Node_Entry *p_linked_list__collision_node_entries__tail
    |   |       +-- Collision_Node_Entry
    |   |           +-- Identifier__u32 uuid_of__hitbox__u32
    |   |           +-- Collision_Node_Entry *p_previous_entry  (towards head)
    |   |               +-- ... (linked list continues)
    |   |
    |   +-- Collision_Node_Entry[0..MAX_QUANTITY_OF__HITBOX_AABB-1]  (entry pool)
    |
    +-- Global_Space_Manager
    |   +-- Global_Space[0..QUANTITY_OF__GLOBAL_SPACE-1]
    |       +-- Chunk_Vector__3i32  (chunk coordinates)
    |       +-- Chunk *p_chunk
    |       +-- Collision_Node *p_collision_node  --> references node in pool
    |
    +-- Entity_Manager
        +-- Entity[0..MAX_QUANTITY_OF__ENTITIES-1]
            +-- (UUID matches Collision_Node_Entry.uuid_of__hitbox__u32)

### Key Types

| Type | Role |
|------|------|
| `Collision_Node_Pool` | Top-level owner. Lives in `World`. Holds both the node array and the entry array. |
| `Collision_Node` | A spatial bucket associated with one `Global_Space` (chunk). Identified by a 64-bit UUID derived from chunk coordinates. Contains a linked list of entries. |
| `Collision_Node_Entry` | A single record in a node's linked list. References a hitbox by its 32-bit UUID. |
| `Global_Space` | Represents a loaded chunk. Holds a pointer to its associated `Collision_Node`. |
| `Global_Space_Manager` | Manages the pool of `Global_Space` instances. Lives in `World`. |

### Limits

| Macro | Default | Description |
|-------|---------|-------------|
| `QUANTITY_OF__GLOBAL_SPACE` | Platform-defined | Number of simultaneously loaded chunks. Determines `Collision_Node` pool size. |
| `MAX_QUANTITY_OF__HITBOX_AABB` | 256 | Maximum number of hitboxes. Determines `Collision_Node_Entry` pool size. |

## Spatial Partitioning Strategy

### Chunk-Aligned Buckets

The world is divided into chunks of fixed size (`CHUNK__WIDTH` x `CHUNK__HEIGHT`
tiles). Each loaded chunk has exactly one `Global_Space`, and each
`Global_Space` has at most one associated `Collision_Node`.

A hitbox occupies the `Collision_Node` corresponding to the chunk that contains
the hitbox's center position. When the hitbox moves to a different chunk, its
entry must be migrated to the new chunk's `Collision_Node`.

    +-------------+-------------+-------------+
    | Chunk(0,1)  | Chunk(1,1)  | Chunk(2,1)  |
    |             |             |             |
    | Node: CN_A  | Node: CN_B  | Node: CN_C  |
    | Entries: 0  | Entries: 2  | Entries: 1  |
    +-------------+-------------+-------------+
    | Chunk(0,0)  | Chunk(1,0)  | Chunk(2,0)  |
    |             |             |             |
    | Node: CN_D  | Node: CN_E  | Node: CN_F  |
    | Entries: 1  | Entries: 3  | Entries: 0  |
    +-------------+-------------+-------------+

### UUID Derivation

`Collision_Node` instances use 64-bit UUIDs derived from chunk coordinates.
This allows O(1) lookup via hashing in the `Collision_Node_Pool`:

    get_p_collision_node_by__uuid_64_from__collision_node_pool(
        p_collision_node_pool,
        uuid_derived_from__chunk_coordinates);

The hashing function (`dehash_identitier_u64_in__contigious_array`) maps the
64-bit UUID to an index in the contiguous `collision_nodes` array.

### Linked List Structure

Each `Collision_Node` maintains a singly-linked list of `Collision_Node_Entry`
records, linked from tail to head via `p_previous_entry`:

    Collision_Node
      +-- p_linked_list__collision_node_entries__tail
          +-- Entry_C (uuid: 0x003)
              +-- p_previous_entry
                  +-- Entry_B (uuid: 0x007)
                      +-- p_previous_entry
                          +-- Entry_A (uuid: 0x001)
                              +-- p_previous_entry = NULL (head)

New entries are appended at the tail. Removal unlinks the entry from the chain
and returns it to the `Collision_Node_Pool`'s entry pool.

## Lifecycle

### 1. Initialization

    initialize_collision_node_pool(&world.collision_node_pool);
        -> All Collision_Node slots: UUID-64 set to deallocated sentinel.
        -> All Collision_Node_Entry slots: marked as available.

### 2. Node Allocation (Chunk Load)

When a `Global_Space` is activated (chunk loaded):

    Collision_Node *p_node =
        allocate_collision_node_from__collision_node_pool(
            &collision_node_pool,
            uuid_from_chunk_coordinates);

    initialize_collision_node(p_node, uuid_from_chunk_coordinates);

    global_space.p_collision_node = p_node;

### 3. Entry Addition (Hitbox Enters Chunk)

When a hitbox's center position falls within a chunk:

    add_entry_to__collision_node(
        &collision_node_pool,
        p_collision_node,
        chunk_vector__3i32,
        hitbox_uuid__u32);

        -> Allocates a Collision_Node_Entry from the pool.
        -> Sets uuid_of__hitbox__u32 to the hitbox's UUID.
        -> Appends to the tail of the node's linked list.
        -> Returns false if the entry pool is exhausted.

### 4. Entry Removal (Hitbox Leaves Chunk)

When a hitbox moves to a different chunk:

    remove_entry_from__collision_node(
        &collision_node_pool,
        p_collision_node__old,
        hitbox_uuid__u32);

        -> Finds the entry by UUID in the linked list.
        -> Unlinks it from the chain.
        -> Returns the Collision_Node_Entry to the pool.

Then add the entry to the new chunk's node (step 3).

### 5. Collision Polling

During per-frame collision resolution:

    poll_for__collisions_within_this__collision_node(
        p_game,
        p_world,
        p_collision_node,
        f_hitbox_aabb_collision_handler,
        p_hitbox_aabb__subject);

        -> Iterates all Collision_Node_Entry records in the node.
        -> For each entry:
            -> Resolves uuid_of__hitbox__u32 to a Hitbox_AABB* via
               Hitbox_AABB_Manager.
            -> Calls is_hitbox_aabb__colliding(subject, candidate).
            -> If collision detected, invokes f_hitbox_aabb_collision_handler.

### 6. Node Deallocation (Chunk Unload)

When a `Global_Space` is deactivated:

    release_collision_node_from__collision_node_pool(
        &collision_node_pool,
        p_collision_node);

        -> All entries in the node's linked list should have been
           removed prior to this call.
        -> The node slot is marked as deallocated.
        -> global_space.p_collision_node = NULL.

## Integration with Collision Resolver

The `poll_collision_resolver_aabb` function (from `collision_resolver_aabb.h`)
drives the full collision detection loop:

    For each active Hitbox_AABB in Hitbox_AABB_Manager:
        1. Determine which Global_Space the hitbox occupies
           (from chunk coordinates derived from hitbox position).
        2. Get the Global_Space's Collision_Node.
        3. Call poll_for__collisions_within_this__collision_node(...)
           to check entity-entity collisions.
        4. Call poll_hitbox_aabb_for__tile_collision(...)
           to check entity-tile collisions via Local_Space_Manager.

This two-phase approach (spatial partitioning via `Collision_Node`, then
per-tile checks via `Local_Space_Manager`) keeps the collision system
efficient even with many active hitboxes.

## Entity Iteration

The collision node system also supports iterating entities within a spatial
region:

    Collision_Node_Entry *p_entry =
        p_collision_node->p_linked_list__collision_node_entries__tail;
    Entity *p_entity = NULL;

    while (iterate_entities_in__collision_node_entry(
            p_entity_manager,
            &p_entry,
            &p_entity)) {
        // p_entity is valid for this iteration
    }

This resolves each `Collision_Node_Entry.uuid_of__hitbox__u32` to an `Entity`
via the `Entity_Manager`, enabling spatial queries like "find all entities in
this chunk."

## Capacity Constraints

- Each hitbox can occupy **exactly one** `Collision_Node_Entry` at a time.
  The entry pool size (`MAX_QUANTITY_OF__HITBOX_AABB` = 256) matches the
  maximum number of AABB hitboxes.
- Each loaded chunk can have **at most one** `Collision_Node`. The node pool
  size (`QUANTITY_OF__GLOBAL_SPACE`) matches the number of simultaneously
  loaded chunks.
- If a hitbox straddles a chunk boundary, it is assigned to the chunk
  containing its **center position** only. Cross-boundary collisions are
  handled by checking adjacent collision nodes during the resolution phase.

## Relationship to Hitbox Management

The collision node system and the hitbox management system (see
`system_overview__hitbox.md`) are complementary but separate:

| Concern | Managed By |
|---------|------------|
| Hitbox allocation, pooling, and property access | `Hitbox_Context` -> `Hitbox_AABB_Manager` |
| Spatial indexing of hitboxes by chunk | `Collision_Node_Pool` -> `Collision_Node` |
| Physics integration (velocity -> position) | `Hitbox_AABB_Manager.poll_hitbox_manager_for__movement` |
| Collision detection and response | `collision_resolver_aabb.poll_collision_resolver_aabb` |
| Collision node entry migration on chunk transition | External (entity system / game action handlers) |

The `Collision_Node_Entry.uuid_of__hitbox__u32` is the bridge between the two
systems: it references a `Hitbox_AABB` by UUID, which is resolved through the
`Hitbox_AABB_Manager` during collision polling.
