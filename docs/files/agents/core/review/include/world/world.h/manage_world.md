# manage_world

**File of origin:** `core/source/world/world.c`

## Semantic

`manage_world` orchestrates the per-frame update logic for the game world. It retrieves the world from the game context, resolves the world-specific hitbox AABB manager from the hitbox context, polls collision resolution and hitbox movement, updates all entities, and iterates over all connected clients to update local space scrolling based on each client's hitbox position.

## Pre-conditions

1. `p_game` must be non-null and point to a valid, initialized `Game` structure.
2. The world must be initialized and accessible via `get_p_world_from__game(p_game)`.
3. The hitbox context must be initialized and accessible via `get_p_hitbox_context_from__game(p_game)`.
4. The hitbox context must contain a valid `Hitbox_AABB_Manager` entry for the world's UUID (retrieved via `get_pV_hitbox_manager_from__hitbox_context`).
5. The world must have valid function pointers set for `f_hitbox_aabb_collision_handler` and `f_hitbox_aabb_tile_touch_handler`.
6. The entity manager within the world must be initialized.
7. The global space manager within the world must be initialized.
8. For each client: the client pointer (if non-null) must have a valid local space manager accessible via `get_p_local_space_manager_from__client`.
9. The client's hitbox AABB (if found) must have a valid position retrievable via `get_position_3i32F4_of__hitbox_aabb`.

## Post-conditions

1. The world's hitbox AABB manager has been polled for collision resolution and movement updates.
2. All allocated and enabled entities in the world have had their update handlers invoked.
3. For each connected client with a valid hitbox, the local space manager has been polled for scrolling based on the client's hitbox position.
4. The world state is advanced by one frame tick.

## Correctness Verdict

Correct.

## Semantic Alignment

The implementation fulfills the semantic intent of managing the world's per-frame update cycle. It correctly:
- Retrieves the world from the game context.
- Obtains the world-specific hitbox AABB manager from the hitbox context.
- Polls collision resolution and hitbox movement.
- Delegates entity management to `manage_world__entities`.
- Iterates over all connected clients to update local space scrolling based on each client's hitbox position.

The `#warning` comment on line 113 indicates a known design TODO (using client hitbox for scrolling rather than camera), but this does not represent a correctness bug — it represents a planned improvement. The current implementation correctly uses the client's hitbox position for local space scrolling, which is actually the intended behavior noted in the TODO.

## Implementation Correctness

1. **Type compatibility:** All parameter types match their target field/function types. The cast of `get_pV_hitbox_manager_from__hitbox_context` return value to `Hitbox_AABB_Manager*` is consistent with the pattern used elsewhere in the codebase.
2. **Pointer safety:** The function checks `p_client` for null before use (line 125) and checks `p_hitbox_aabb` for null before use (line 131). The world pointer and hitbox manager are obtained from well-established accessor functions that are expected to return valid pointers given proper initialization.
3. **Loop bounds:** The client iteration loop correctly uses `get_quantity_of__clients_connect_to__game(p_game)` as the upper bound, and the entity iteration in `manage_world__entities` correctly checks `MAX_QUANTITY_OF__ENTITIES`.
4. **No undefined behavior:** No broken pointer arithmetic, no null dereferences, no type punning, no out-of-bounds access.
5. **Validation:** The function appropriately validates client and hitbox pointers within the loop. Null checks on the world and hitbox manager are delegated to the caller's responsibility (pre-condition).

## Side Effects

1. **Collision resolution polling:** Invokes `poll_collision_resolver_aabb`, which may resolve and clear pending collisions.
2. **Hitbox movement polling:** Invokes `poll_hitbox_manager_for__movement`, which updates hitbox positions.
3. **Entity updates:** Invokes `manage_world__entities`, which calls each entity's `m_entity_update_handler`, potentially modifying entity state, game state, or world state.
4. **Local space scrolling:** Invokes `poll_local_space_for__scrolling` for each client with a valid hitbox, which updates the local space manager's center position to follow the client's hitbox.
