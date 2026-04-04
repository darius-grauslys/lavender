# Specification: core/include/collisions/collision_node_pool.h

## Overview

Provides pool management for `Collision_Node` and `Collision_Node_Entry`
instances. The `Collision_Node_Pool` is the top-level owner of all spatial
partitioning data and lives within the `World` struct. It manages both the
fixed-size array of collision nodes (one per loadable chunk) and the
fixed-size array of collision node entries (one per possible hitbox).

See `system_overview__collision_node.md` for the full architectural context.

## Dependencies

- `defines.h` (for `Collision_Node_Pool`, `Collision_Node`,
  `Collision_Node_Entry`, `Identifier__u64`, `QUANTITY_OF__GLOBAL_SPACE`,
  `MAX_QUANTITY_OF__HITBOX_AABB`)
- `defines_weak.h` (forward declarations)
- `platform_defines.h` (for `QUANTITY_OF__GLOBAL_SPACE`)
- `serialization/hashing.h` (for `dehash_identitier_u64_in__contigious_array`)

## Types

### Collision_Node_Pool (struct)

Defined in `defines.h`:

    typedef struct Collision_Node_Pool_t {
        Collision_Node collision_nodes[QUANTITY_OF__GLOBAL_SPACE];
        Collision_Node_Entry collision_node_entries[MAX_QUANTITY_OF__HITBOX_AABB];
    } Collision_Node_Pool;

| Field | Type | Description |
|-------|------|-------------|
| `collision_nodes` | `Collision_Node[QUANTITY_OF__GLOBAL_SPACE]` | Pool of collision nodes. Each slot corresponds to one loadable chunk. |
| `collision_node_entries` | `Collision_Node_Entry[MAX_QUANTITY_OF__HITBOX_AABB]` | Pool of collision node entries. Each slot corresponds to one possible hitbox. |

### Limits

| Macro | Default | Description |
|-------|---------|-------------|
| `QUANTITY_OF__GLOBAL_SPACE` | Platform-defined | Number of simultaneously loaded chunks. Determines collision node pool size. |
| `MAX_QUANTITY_OF__HITBOX_AABB` | 256 | Maximum number of AABB hitboxes. Determines collision node entry pool size. |

## Functions

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_collision_node_pool` | `(Collision_Node_Pool*) -> void` | Initializes all collision node slots with deallocated sentinel UUIDs and all entry slots as available. |

### Node Allocation

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `allocate_collision_node_from__collision_node_pool` | `(Collision_Node_Pool*, Identifier__u64 uuid__u64) -> Collision_Node*` | `Collision_Node*` | Allocates a collision node slot using the 64-bit UUID (derived from chunk coordinates) as a hash key. Returns a pointer to the allocated node, or NULL on failure. |
| `release_collision_node_from__collision_node_pool` | `(Collision_Node_Pool*, Collision_Node*) -> void` | `void` | Marks the given collision node slot as deallocated. All entries should have been removed prior to this call. |

### Entry Allocation

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `allocate_collision_node_entry_from__collision_node_pool` | `(Collision_Node_Pool*) -> Collision_Node_Entry*` | `Collision_Node_Entry*` | Allocates an available `Collision_Node_Entry` from the entry pool. Returns NULL if the pool is exhausted. |
| `release_collision_node_entry_from__collision_node_pool` | `(Collision_Node_Pool*, Collision_Node_Entry*) -> void` | `void` | Returns the given entry to the pool, marking it as available. |

### Lookup (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_p_collision_node_by__uuid_64_from__collision_node_pool` | `(Collision_Node_Pool*, Identifier__u64 uuid__u64) -> Collision_Node*` | `Collision_Node*` | Performs O(1) lookup of a collision node by its 64-bit UUID using `dehash_identitier_u64_in__contigious_array`. Returns a pointer to the node, or NULL if not found. |

## Agentic Workflow

### Pool Lifecycle

    initialize_collision_node_pool(&world.collision_node_pool)
        -> All node slots: UUID set to deallocated sentinel.
        -> All entry slots: marked as available.

    // --- Runtime ---

    // Chunk load:
    Collision_Node *p_node =
        allocate_collision_node_from__collision_node_pool(
            &pool, uuid_from_chunk_coords);

    // Hitbox enters chunk:
    Collision_Node_Entry *p_entry =
        allocate_collision_node_entry_from__collision_node_pool(&pool);
    // (entry is linked into node's list by collision_node.h functions)

    // Hitbox leaves chunk:
    // (entry is unlinked from node's list by collision_node.h functions)
    release_collision_node_entry_from__collision_node_pool(&pool, p_entry);

    // Chunk unload:
    release_collision_node_from__collision_node_pool(&pool, p_node);

### Hashing Strategy

The `get_p_collision_node_by__uuid_64_from__collision_node_pool` function
uses `dehash_identitier_u64_in__contigious_array` to map a 64-bit UUID
(derived from chunk coordinates) to an index in the contiguous
`collision_nodes` array. This provides O(1) spatial lookup.

The UUID derivation from chunk coordinates is performed externally (typically
via chunk vector hashing utilities). The pool itself does not compute UUIDs.

### Relationship to Collision_Node

The pool is responsible for **allocation and deallocation** of nodes and
entries. The `Collision_Node` (see `collision_node.h.spec.md`) is responsible
for **linking entries into its list** and **polling for collisions**. The
typical call sequence is:

    // Pool allocates the entry:
    Collision_Node_Entry *p_entry =
        allocate_collision_node_entry_from__collision_node_pool(&pool);

    // Node links the entry:
    add_entry_to__collision_node(&pool, p_node, chunk_vec, uuid);
    // (internally calls allocate_collision_node_entry_from__collision_node_pool)

Note: `add_entry_to__collision_node` in `collision_node.h` internally calls
the pool's entry allocator, so the caller typically does not need to call
`allocate_collision_node_entry_from__collision_node_pool` directly.

### Preconditions

- `initialize_collision_node_pool`: `p_collision_node_pool` must be non-null.
- `allocate_collision_node_from__collision_node_pool`: The UUID must not
  already be allocated in the pool.
- `release_collision_node_from__collision_node_pool`: The node must be
  allocated. All entries should have been removed from the node's linked
  list prior to release.
- `release_collision_node_entry_from__collision_node_pool`: The entry must
  have been previously allocated and unlinked from any node's list.

### Postconditions

- After `initialize_collision_node_pool`: All nodes report
  `is_collision_node__allocated` as false.
- After `allocate_collision_node_from__collision_node_pool` (success):
  The returned node's UUID matches the requested UUID.
  `is_collision_node__allocated` returns true for the node.
- After `release_collision_node_from__collision_node_pool`:
  `is_collision_node__allocated` returns false for the node.

### Error Handling

- `allocate_collision_node_from__collision_node_pool` returns NULL if the
  hash slot is already occupied or the pool is full.
- `allocate_collision_node_entry_from__collision_node_pool` returns NULL if
  the entry pool is exhausted.
- Debug builds may call `debug_error` or `debug_abort` on invalid operations.
