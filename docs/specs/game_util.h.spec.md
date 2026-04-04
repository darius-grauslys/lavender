# Specification: core/include/game_util.h

## Overview

Provides convenience functions that combine entity, world, and tile
subsystem operations. These are thin wrappers that bridge the entity
system (getting the position/direction of an entity) with the world
system (looking up tiles at positions).

## Dependencies

- `defines.h`
- `world/tile_vectors.h` (for `vector_3i32F4_to__tile_vector`)
- `entity/entity_util.h` (for `get_vector_3i32F4_thats__infront_of_this__entity`)
- `game.h` (for `get_p_chunk_manager_from__game`)

## Types

None.

## Functions

### get_tile_vector_thats__infront_of_this__entity (static inline)

    static inline
    Tile_Vector__3i32 get_tile_vector_thats__infront_of_this__entity(
            Entity *p_entity);

Returns the tile-space vector of the tile directly in front of the
given entity, based on the entity's current position and facing direction.

| Parameter | Type | Description |
|-----------|------|-------------|
| `p_entity` | `Entity*` | The entity whose front tile is queried. |

**Return value**: `Tile_Vector__3i32` — the tile coordinates in front of
the entity.

### get_p_tile_thats__infront_of__this_entity (static inline)

    static inline
    Tile *get_p_tile_thats__infront_of__this_entity(
            Game *p_game,
            Entity *p_entity);

Returns a pointer to the `Tile` directly in front of the given entity
in the active world.

| Parameter | Type | Description |
|-----------|------|-------------|
| `p_game` | `Game*` | The game instance (for world/chunk access). |
| `p_entity` | `Entity*` | The entity whose front tile is queried. |

**Return value**: `Tile*` — pointer to the tile, or null if the tile is
not loaded.

## Agentic Workflow

### When to Use

Use these functions when:

- Implementing entity interaction logic (e.g. "use" action on the tile
  in front of the player).
- Checking tile properties ahead of an entity for pathfinding or AI.
- Placing or modifying tiles relative to an entity's facing direction.

### Composition

These functions compose three layers:

    Entity facing direction
         ↓
    get_vector_3i32F4_thats__infront_of_this__entity (entity_util.h)
         ↓
    vector_3i32F4_to__tile_vector (tile_vectors.h)
         ↓
    get_p_tile_from__chunk_manager_with__tile_vector_3i32 (chunk_manager.h)

### Usage Pattern

    Tile *p_tile = get_p_tile_thats__infront_of__this_entity(
            p_game, p_entity);
    if (p_tile && is_tile__interactable(p_tile)) {
        // interact with tile
    }

### Preconditions

- `p_entity` must be non-null and have valid position/direction data.
- `p_game` must have an allocated world with loaded chunks covering the
  entity's position.

### Postconditions

- `get_tile_vector_thats__infront_of_this__entity` always returns a
  valid `Tile_Vector__3i32` (though it may be out of loaded chunk range).
- `get_p_tile_thats__infront_of__this_entity` returns null if the tile
  is not in a loaded chunk.

### Error Handling

- No explicit error handling. Null entity or unloaded world results in
  undefined behavior or null return from chunk manager lookup.
