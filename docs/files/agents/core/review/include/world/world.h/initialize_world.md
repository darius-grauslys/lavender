# Function: `initialize_world`

**File of origin:** `core/source/world/world.c`

## Semantic

Resets a `World` struct to its default/initial conditions (Lavender-style initialization / pool cleanup). It delegates to sub-struct `initialize_*` functions, sets default name, spawn point, and handler function pointers.

## Pre-conditions

1. `p_game` must be a non-null pointer to a valid `Game` object. It is used as a seed source for the pseudo-random number generator (`(u32)(u64)p_game`) and to access the game's item manager for `register_core_items_into__item_manager`.
2. `p_world` must be a non-null pointer to a writable `World` object whose memory is allocated.
3. The `World` struct fields are assumed to be in an indeterminate state prior to the call; the function is responsible for setting all fields to safe defaults.

## Post-conditions

1. `p_world->_serialization_header` is initialized with identifier `0` and `sizeof(World)`.
2. `p_world->repeatable_pseudo_random` is seeded from the address of `p_game`.
3. `p_world->name` is set to `"default_world"` and `p_world->length_of__world_name` reflects its length.
4. `p_world->chunk_generator_table`, `entity_manager`, `collision_node_pool`, `chunk_pool`, `global_space_manager`, `inventory_manager`, `item_manager`, and `tile_logic_context` are all initialized to their respective default states.
5. Core items are registered into the item manager (via the game's world reference).
6. `p_world->f_hitbox_aabb_tile_touch_handler` is set to `f_hitbox_aabb_tile_touch_handler__default`.
7. `p_world->f_hitbox_aabb_collision_handler` is set to `f_hitbox_aabb_collision_handler__default`.
8. `p_world->spawn_point` is set to `VECTOR__3i32F4__OUT_OF_BOUNDS`.

**However, the following fields are NOT initialized and remain in an indeterminate state:**
- `p_world->region_manager` — `initialize_region_manager` exists but is never called.
- `p_world->structure_manager` — `initialize_structure_manager` exists but is never called.
- `p_world->camera` — `initialize_camera_as__inactive` exists but is never called.
- `p_world->f_tile_render_kernel` — `set_f_tile_render_kernel_of__world` exists but is never called; the function pointer is left uninitialized.
- `p_world->p_graphics_window_for__world` — left uninitialized; should be set to `0`/`NULL`.

## Correctness Verdict

**Incorrect**

The function fails to initialize five struct fields: `region_manager`, `structure_manager`, `camera`, `f_tile_render_kernel`, and `p_graphics_window_for__world`. Each of these has a dedicated initialization routine or setter available, but none are invoked. Leaving these fields uninitialized means the `World` struct is in a partially-valid state after the call, which can lead to undefined behavior if any code reads these fields before they are separately set.

## Semantic Alignment

This function performs Lavender-style initialization (pool cleanup / reset to defaults), not RAII resource acquisition. The intent is to clear the struct to safe initial conditions so it can be reused or returned to a pool.

The implementation does **not** fulfill its semantic intent. A Lavender-style initializer must reset **all** struct fields to known default values. The `World` struct has 20 fields (see `typedef struct World_t` in `core/include/defines.h`), and only 15 are initialized by this function. The five omitted fields (`region_manager`, `structure_manager`, `camera`, `f_tile_render_kernel`, `p_graphics_window_for__world`) are left in an indeterminate state.

Additionally, `register_core_items_into__item_manager` is called with `get_p_item_manager_from__game(p_game)` rather than `get_p_item_manager_from__world(p_world)`. The game-level accessor delegates to `get_p_item_manager_from__world(get_p_world_from__game(p_game))`, which retrieves the item manager from the game's stored world — not necessarily the `p_world` being initialized. If `p_game`'s world differs from `p_world`, core items are registered into the wrong item manager. The correct call should use `get_p_item_manager_from__world(p_world)`.

## Implementation Correctness

- **Type compatibility:** All initialization calls pass correctly-typed pointers. The cast `(u32)(u64)p_game` truncates a 64-bit pointer to 32 bits for use as a pseudo-random seed; this is intentional and not a type-safety issue.
- **Undefined behavior:** Reading any of the five uninitialized fields before they are separately set constitutes undefined behavior. The `strncpy` call is safe: `"default_world"` is 13 characters, `WORLD_NAME_MAX_SIZE_OF` is 32, so the destination is fully null-terminated and padded.
- **Validation:** No null-pointer validation is performed on `p_game` or `p_world`. This is consistent with the codebase pattern (other `initialize_*` functions also lack validation), so it is the caller's responsibility.

## Side Effects

- Mutates `p_world` in place: all initialized sub-managers, pools, and direct fields are reset to defaults.
- Calls `register_core_items_into__item_manager` on the item manager obtained from `p_game`'s world (see Semantic Alignment for the concern about which item manager is targeted).
- No I/O, no global state mutation, no memory allocation.
