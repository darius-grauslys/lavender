# m_process__game_action__hitbox

**File of origin:** `core/source/game_action/core/hitbox/game_action__hitbox.c`

## Semantic

Processes a game action that updates the position, velocity, and acceleration of a hitbox. The function retrieves the target hitbox via its UUID from the hitbox context, captures the old position, applies the new position/velocity/acceleration, and then triggers a collision node update based on the position delta.

## Pre-conditions

1. `p_this_process` must be non-null and contain a valid `p_process_data` pointer that can be cast to `Game_Action*`.
2. `p_game` must be non-null and have an allocated world (`pM_world` must be non-null).
3. The world's UUID (via `GET_UUID_P(get_p_world_from__game(p_game))`) must correspond to a registered hitbox manager in the game's `Hitbox_Context`.
4. The hitbox target UUID (`get_uuid_of__target_from__ga_collisions(p_game_action)`) must correspond to a valid, allocated hitbox within the hitbox manager.
5. The `Game_Action` payload must be properly initialized with valid position, velocity, acceleration, and hitbox kind fields (as set by `initialize_game_action_for__hitbox`).
6. The collision node pool in the world must be initialized and ready to accept updates.

## Post-conditions

1. If `pV_hitbox` is null (hitbox not found), the process is marked as failed via `fail_process(p_this_process)` and the function returns early without modifying any state.
2. If the hitbox kind is `Hitbox_Kind__Opaque` (or any unrecognized/default case), the old position is retrieved via `opaque_access_to__hitbox` with `OPAQUE_HITBOX_ACCESS__GET`, and then the new position, velocity, and acceleration are set via a second `opaque_access_to__hitbox` call with `OPAQUE_HITBOX_ACCESS__SET`.
3. If the hitbox kind is `Hitbox_Kind__AABB`, the old position is captured from the `Hitbox_AABB` struct, then position, velocity, and acceleration are directly set on the `Hitbox_AABB` using `set_hitbox_aabb__position_with__3i32F4`, `set_velocity_to__hitbox_aabb`, and `set_acceleration_to__hitbox_aabb`.
4. After the hitbox is updated, `poll_for_collision_node_update` is called with the old and new positions and the target UUID, which updates the collision node entries to reflect the hitbox's new position in the collision grid.
5. The process is marked as complete via `complete_process(p_this_process)`.
6. The hitbox is marked as dirty by the setter functions (e.g., `set_hitbox_aabb_as__dirty`).

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation correctly fulfills the semantic intent of updating a hitbox's transform (position, velocity, acceleration) and notifying the collision system of the change. The function:

- Correctly retrieves the hitbox via the hitbox context using the world UUID (as the hitbox manager identifier) and the target entity UUID.
- Properly captures the old position before mutation, which is needed for the collision node update to track which grid cells the hitbox has moved between.
- Correctly dispatches on `Hitbox_Kind` to handle both opaque (generic) hitboxes and AABB-specific hitboxes.
- For opaque hitboxes, uses the opaque accessor pattern (GET then SET) which is the correct approach for hitbox types not directly known to core.
- For AABB hitboxes, directly accesses the `Hitbox_AABB` struct fields, which is appropriate since the AABB layout is known.
- Calls `poll_for_collision_node_update` with both old and new positions, enabling the collision system to remove the hitbox from old grid cells and add it to new ones.
- Properly handles the null hitbox case by failing the process.

The `#warning TODO(tech-debt)` comment indicates that the opaque and AABB cases should ideally be separated into their own game actions, but this is a design/architecture concern, not a correctness issue.

## Implementation Correctness

- **Type compatibility:** All type conversions are correct. `GET_UUID_P(get_p_world_from__game(p_game))` returns `Identifier__u32` which matches the expected parameter type for `uuid_of__hitbox_manager__u32`. The `Vector__3i32F4` and `Vector__3i16F8` types are correctly extracted from the game action payload and passed to the appropriate setters.
- **Null pointer safety:** The function checks `pV_hitbox` for null before proceeding. The `opaque_access_to__hitbox` and `set_*_to__hitbox_aabb` functions have their own null checks in debug builds.
- **No undefined behavior:** No broken pointer arithmetic, no out-of-bounds access. The cast of `pV_hitbox` to `Hitbox_AABB*` in the AABB case is safe because `pV_hitbox` was already retrieved from the hitbox context for the same target UUID, and the AABB hitbox type is the concrete type used by the AABB hitbox manager.
- **Switch statement coverage:** The `Hitbox_Kind__Opaque` case is the default, meaning any unrecognized hitbox kind will be treated as opaque. This is a reasonable defensive default.
- **Variable initialization:** `position_OLD_of__hitbox__3i32F4` is declared but not initialized before the switch. In the `Hitbox_Kind__Opaque` case, it is populated by the GET call before the SET call. In the `Hitbox_Kind__AABB` case, it is assigned from `get_position_3i32F4_of__hitbox_aabb`. In both cases, it is properly initialized before use in `poll_for_collision_node_update`. However, if a new `Hitbox_Kind` enum value were added without a corresponding case, `position_OLD_of__hitbox__3i32F4` would be used uninitialized, which would be undefined behavior. This is a minor latent risk but not currently a bug given the existing enum values.

## Side Effects

- **Mutates the target hitbox:** Updates position, velocity, and acceleration of the hitbox identified by the target UUID.
- **Mutates the process:** Sets the process status to either `Process_Status_Kind__Fail` (if hitbox not found) or `Process_Status_Kind__Complete` (on success).
- **Mutates the collision system:** Calls `poll_for_collision_node_update` which may add or remove entries in collision node linked lists, potentially re-linking collision node entries to reflect the hitbox's new position in the spatial grid.
- **No side effects beyond these.** The function does not modify the `Game_Action` payload itself, nor does it allocate or deallocate any resources.
