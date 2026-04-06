# 1 Specification: core/include/collisions/collision_resolver_aabb.h

## 1.1 Overview

Provides the top-level collision resolution loop for AABB hitboxes, including
both entity-entity and entity-tile collision detection and response. This is
the primary entry point for per-frame collision processing.

The resolver integrates the spatial partitioning system (`Collision_Node`)
with the hitbox management system (`Hitbox_AABB_Manager`) and the tile
system (`Local_Space_Manager`) to perform efficient, narrowed collision
checks.

See `system_overview__collision_node.md` for the spatial partitioning
context and `module_topology__collision.mmd` for the type relationships.

## 1.2 Dependencies

- `defines.h` (for `Game`, `World`, `Hitbox_AABB`, `Hitbox_AABB_Manager`,
  `Tile`, `Signed_Index__i32`, `f_Hitbox_AABB_Collision_Handler`,
  `f_Hitbox_AABB_Tile_Touch_Handler`, `Local_Space_Manager`)

## 1.3 Types

### 1.3.1 Callback Signatures

Defined in `defines.h`:

    typedef void (*f_Hitbox_AABB_Collision_Handler)(
            Game *p_game,
            World *p_world,
            Hitbox_AABB *p_hitbox_aabb__colliding,
            Hitbox_AABB *p_hitbox_aabb__collided);

    typedef void (*f_Hitbox_AABB_Tile_Touch_Handler)(
            Game *p_game,
            World *p_world,
            Hitbox_AABB *p_hitbox_aabb,
            Tile *p_tile,
            Signed_Index__i32 x__i32,
            Signed_Index__i32 y__i32);

| Callback | Description |
|----------|-------------|
| `f_Hitbox_AABB_Collision_Handler` | Invoked when two AABB hitboxes are detected as colliding. `p_hitbox_aabb__colliding` is the subject; `p_hitbox_aabb__collided` is the candidate. |
| `f_Hitbox_AABB_Tile_Touch_Handler` | Invoked when an AABB hitbox overlaps a tile. `x__i32` and `y__i32` are the tile's world-space coordinates. |

## 1.4 Functions

### 1.4.1 Default Handlers

| Function | Signature | Description |
|----------|-----------|-------------|
| `f_hitbox_aabb_collision_handler__default` | `(Game*, World*, Hitbox_AABB* colliding, Hitbox_AABB* collided) -> void` | Default entity-entity collision response. Performs displacement resolution based on overlap direction and the `COLLISION_DELTA_THRESHOLD`. |
| `f_hitbox_aabb_tile_touch_handler__default` | `(Game*, World*, Hitbox_AABB*, Tile*, Signed_Index__i32 x, Signed_Index__i32 y) -> void` | Default entity-tile collision response. Checks tile logic flags (unpassable, stair height) and applies position correction. |

### 1.4.2 Collision Polling

| Function | Signature | Description |
|----------|-----------|-------------|
| `poll_collision_resolver_aabb` | `(Game*, Hitbox_AABB_Manager*, f_Hitbox_AABB_Collision_Handler, f_Hitbox_AABB_Tile_Touch_Handler) -> void` | Main per-frame collision resolution loop. Iterates all active hitboxes in the manager. For each hitbox: (1) determines the chunk it occupies, (2) retrieves the chunk's `Collision_Node`, (3) polls entity-entity collisions via the node, (4) polls entity-tile collisions via the `Local_Space_Manager`. |
| `poll_hitbox_aabb_for__tile_collision` | `(Game*, Local_Space_Manager*, Hitbox_AABB*, f_Hitbox_AABB_Tile_Touch_Handler) -> void` | Checks a single hitbox against all tiles it overlaps. Iterates the tile grid cells covered by the hitbox's bounding box and invokes the tile touch handler for each occupied tile. |

## 1.5 Agentic Workflow

### 1.5.1 Per-Frame Collision Resolution

The collision resolver is invoked once per game tick:

    poll_collision_resolver_aabb(
        p_game,
        p_hitbox_aabb_manager,
        world->f_hitbox_aabb_collision_handler,
        world->f_hitbox_aabb_tile_touch_handler);

### 1.5.2 Resolution Algorithm

    For each active Hitbox_AABB in Hitbox_AABB_Manager:
        1. Compute chunk coordinates from hitbox position.
        2. Look up the Global_Space for those coordinates.
        3. Get the Global_Space's Collision_Node.
        4. Call poll_for__collisions_within_this__collision_node(...)
           -> For each Collision_Node_Entry in the node:
              -> Resolve entry UUID to Hitbox_AABB*.
              -> Test is_hitbox_aabb__colliding(subject, candidate).
              -> If colliding, invoke f_hitbox_aabb_collision_handler.
        5. Call poll_hitbox_aabb_for__tile_collision(...)
           -> For each tile cell overlapped by the hitbox:
              -> Look up the Tile from Local_Space_Manager.
              -> Invoke f_hitbox_aabb_tile_touch_handler.

### 1.5.3 Two-Phase Design

| Phase | System | Purpose |
|-------|--------|---------|
| Entity-Entity | `Collision_Node` spatial partitioning | Narrows candidates to same-chunk hitboxes. O(n) per node where n is entries in that node. |
| Entity-Tile | `Local_Space_Manager` tile grid | Checks tiles covered by hitbox bounding box. O(w*h) where w,h are hitbox dimensions in tiles. |

### 1.5.4 Integration with Movement

The collision resolver runs **after** `poll_hitbox_manager_for__movement`
(which applies velocity to position). The typical per-tick sequence is:

    1. poll_hitbox_manager_for__movement(...)   // physics step
    2. poll_collision_resolver_aabb(...)         // collision detection + response

### 1.5.5 Custom Handlers

The `World` struct stores the active collision and tile touch handlers:

    world->f_hitbox_aabb_collision_handler = my_custom_collision_handler;
    world->f_hitbox_aabb_tile_touch_handler = my_custom_tile_handler;

Pass `f_hitbox_aabb_collision_handler__default` and
`f_hitbox_aabb_tile_touch_handler__default` for standard behavior.

### 1.5.6 Preconditions

- `poll_collision_resolver_aabb`: `p_game` and `p_hitbox_aabb_manager` must
  be non-null. The callback function pointers must be non-null.
- `poll_hitbox_aabb_for__tile_collision`: `p_hitbox_aabb` must be non-null
  and active. `p_local_space_manager` must be initialized.

### 1.5.7 Postconditions

- After `poll_collision_resolver_aabb`: All active hitboxes have been checked
  for entity-entity and entity-tile collisions. Collision response has been
  applied via the provided handlers.

### 1.5.8 Error Handling

- If a `Collision_Node` cannot be found for a hitbox's chunk (e.g. chunk not
  loaded), the entity-entity phase is skipped for that hitbox.
- Debug builds may call `debug_error` on null pointers or invalid states.
