# Specification: core/include/collisions/collision_node.h

## Overview

Provides initialization, entry management, collision polling, and iteration
for the `Collision_Node` struct — a spatial bucket in the chunk-aligned
collision partitioning system. Each `Collision_Node` corresponds to one
loaded chunk (`Global_Space`) and maintains a linked list of
`Collision_Node_Entry` records referencing the hitboxes that currently
occupy that chunk's spatial region.

See `system_overview__collision_node.md` for the full architectural context.

## Dependencies

- `defines.h` (for `Collision_Node`, `Collision_Node_Entry`,
  `Collision_Node_Pool`, `Identifier__u64`, `Identifier__u32`,
  `Chunk_Vector__3i32`, `Quantity__u32`, `Hitbox_AABB`,
  `Hitbox_AABB_Manager`, `Vector__3i32F4`,
  `f_Hitbox_AABB_Collision_Handler`, `Entity`, `Entity_Manager`)
- `defines_weak.h` (forward declarations)
- `serialization/serialization_header.h` (for
  `is_serialized_struct__deallocated__uuid_64`)

## Types

### Collision_Node (struct)

Defined in `defines.h`:

    typedef struct Collision_Node_t {
        Serialization_Header__UUID_64 _serialization_header;
        Collision_Node_Entry *p_linked_list__collision_node_entries__tail;
    } Collision_Node;

| Field | Type | Description |
|-------|------|-------------|
| `_serialization_header` | `Serialization_Header__UUID_64` | 64-bit UUID derived from chunk coordinates. Used for O(1) lookup via hashing. |
| `p_linked_list__collision_node_entries__tail` | `Collision_Node_Entry*` | Tail of the singly-linked list of entries. NULL if empty. |

### Collision_Node_Entry (struct)

Defined in `defines.h`:

    typedef struct Collision_Node_Entry_t {
        Identifier__u32 uuid_of__hitbox__u32;
        struct Collision_Node_Entry_t *p_previous_entry;
    } Collision_Node_Entry;

| Field | Type | Description |
|-------|------|-------------|
| `uuid_of__hitbox__u32` | `Identifier__u32` | UUID of the hitbox occupying this entry's chunk. Resolved via `Hitbox_AABB_Manager`. |
| `p_previous_entry` | `Collision_Node_Entry*` | Link toward the head of the list. NULL at the head. |

## Functions

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_collision_node` | `(Collision_Node*, Identifier__u64 uuid__u64) -> void` | Initializes the node with the given 64-bit UUID and an empty entry list. |

### Entry Management

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `add_entry_to__collision_node` | `(Collision_Node_Pool*, Collision_Node*, Chunk_Vector__3i32, Identifier__u32 uuid_u32_of__entry) -> bool` | `bool` | Allocates a `Collision_Node_Entry` from the pool, sets its hitbox UUID, and appends it to the node's linked list tail. Returns false if the entry pool is exhausted. |
| `remove_entry_from__collision_node` | `(Collision_Node_Pool*, Collision_Node*, Identifier__u32 uuid__u32) -> void` | `void` | Finds the entry with the given UUID in the linked list, unlinks it, and returns it to the pool. |

### Queries

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_quantity_of__entries_in__collision_node` | `(const Collision_Node*) -> Quantity__u32` | `Quantity__u32` | Traverses the linked list and returns the count of entries. |
| `get_p_hitbox_aabb_at__vector_3i32F4_from__collision_node` | `(Hitbox_AABB_Manager*, Collision_Node*, Vector__3i32F4) -> Hitbox_AABB*` | `Hitbox_AABB*` | Iterates entries, resolves each to a `Hitbox_AABB`, and returns the first whose bounding box contains the given position. Returns NULL if none found. |

### Collision Polling

| Function | Signature | Description |
|----------|-----------|-------------|
| `poll_for__collisions_within_this__collision_node` | `(Game*, World*, Collision_Node*, f_Hitbox_AABB_Collision_Handler, Hitbox_AABB*) -> void` | Iterates all entries in the node. For each entry, resolves the hitbox UUID to a `Hitbox_AABB*` via the `Hitbox_AABB_Manager`. Tests collision between the subject hitbox and each candidate. Invokes the collision handler callback for each detected collision. |

### Entity Iteration

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `iterate_entities_in__collision_node_entry` | `(Entity_Manager*, Collision_Node_Entry**, Entity**) -> Entity*` | `Entity*` | Advances the entry pointer to the next entry in the linked list, resolves the entry's UUID to an `Entity*` via the `Entity_Manager`, and writes it to the entity output pointer. Returns the entity pointer, or NULL when the list is exhausted. |

### Linked List Iteration (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `iterate_collision_node__entry` | `(Collision_Node_Entry**) -> Collision_Node_Entry*` | `Collision_Node_Entry*` | Advances the entry pointer to `p_previous_entry` and returns the new current entry. Returns NULL at the head of the list. |

### Allocation Query (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_collision_node__allocated` | `(Collision_Node*) -> bool` | `bool` | Returns true if the node's 64-bit UUID is not the deallocated sentinel. Delegates to `is_serialized_struct__deallocated__uuid_64`. |

## Agentic Workflow

### Collision Node Lifecycle

    [Deallocated]
        |
        allocate_collision_node_from__collision_node_pool (collision_node_pool.h)
        initialize_collision_node(p_node, uuid_from_chunk_coords)
        |
    [Allocated, Empty]
        |
        add_entry_to__collision_node (hitbox enters chunk)
        |
    [Allocated, Has Entries]
        |
        poll_for__collisions_within_this__collision_node (each frame)
        |
        remove_entry_from__collision_node (hitbox leaves chunk)
        |
    [Allocated, Empty or Has Entries]
        |
        release_collision_node_from__collision_node_pool (chunk unload)
        |
    [Deallocated]

### Entry Migration Pattern

When a hitbox moves from one chunk to another:

    // 1. Remove from old chunk's node
    remove_entry_from__collision_node(
        &collision_node_pool,
        p_collision_node__old,
        hitbox_uuid__u32);

    // 2. Add to new chunk's node
    add_entry_to__collision_node(
        &collision_node_pool,
        p_collision_node__new,
        new_chunk_vector__3i32,
        hitbox_uuid__u32);

### Entity Iteration Pattern

    Collision_Node_Entry *p_entry =
        p_collision_node->p_linked_list__collision_node_entries__tail;
    Entity *p_entity = NULL;

    while (iterate_entities_in__collision_node_entry(
            p_entity_manager,
            &p_entry,
            &p_entity)) {
        // Process p_entity
    }

### Preconditions

- `initialize_collision_node`: `p_collision_node` must be non-null.
- `add_entry_to__collision_node`: The `Collision_Node_Pool` must have
  available entries. The node must be allocated.
- `remove_entry_from__collision_node`: The entry with the given UUID must
  exist in the node's linked list.
- `poll_for__collisions_within_this__collision_node`: The node must be
  allocated. The subject hitbox must be non-null.

### Postconditions

- After `add_entry_to__collision_node` (success):
  `get_quantity_of__entries_in__collision_node` increases by 1.
- After `remove_entry_from__collision_node`:
  `get_quantity_of__entries_in__collision_node` decreases by 1.
  The removed entry is returned to the pool.
- After `initialize_collision_node`:
  `is_collision_node__allocated` returns true.
  `get_quantity_of__entries_in__collision_node` returns 0.

### Error Handling

- `add_entry_to__collision_node` returns false if the entry pool is
  exhausted.
- `remove_entry_from__collision_node` may call `debug_error` if the UUID
  is not found in the linked list (debug builds).
