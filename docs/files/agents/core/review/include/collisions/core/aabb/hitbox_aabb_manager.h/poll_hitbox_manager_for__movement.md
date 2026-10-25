poll_hitbox_manager_for__movement — core/source/collisions/core/aabb/hitbox_aabb_manager.c

Iterates over all hitboxes in the manager and, for each dirty+active hitbox, dispatches a game action that performs one semi-implicit Euler integration step (position += velocity, velocity += acceleration) with gravity reset as the ongoing acceleration.

Pre-conditions:
1. p_game must be a non-null pointer to a valid Game context (not validated — assumed valid by caller; only forwarded to dispatch_game_action__hitbox).
2. p_hitbox_aabb_manager must be a non-null pointer to a writable Hitbox_AABB_Manager object (validated in debug builds only; if null, the function logs a debug error and returns early).
3. The manager's quantity_of__hitboxes and pM_ptr_array_of__hitbox_records must be properly initialized and consistent (allocated via initialize_hitbox_aabb_manager).
4. The loop index iterates from 0 to quantity_of__hitboxes; get_p_hitbox_aabb_by__index_from__hitbox_aabb_manager performs its own debug bounds check against quantity_of__hitboxes.

Post-conditions:
1. For each dirty+active hitbox, a Game_Action of kind Game_Action_Kind__Hitbox is dispatched via dispatch_game_action__hitbox → dispatch_game_action_to__server (enqueued for asynchronous resolution).
2. The resolver (m_process__game_action__hitbox) will overwrite the hitbox's state with: position = old_position + old_velocity, velocity = old_velocity + old_acceleration (with i16F8→i32F4 conversion), acceleration = gravity (VECTOR__3i16F8__0_0_nGRAVITY_PER_TICK).
3. Hitboxes that are not dirty or not active are skipped (continue).
4. Upon encountering the first NULL slot in the pointer array (a deallocated hitbox), the loop breaks. This is safe because the pool uses a swap-and-pop allocation strategy (see release_hitbox_aabb_from__hitbox_aabb_manager), guaranteeing allocated hitboxes are always contiguous from index 0; all slots after the first NULL are also NULL.

Correctness Verdict: Correct

Semantic Alignment:
The function performs a standard semi-implicit (symplectic) Euler integration step:
- New position = position + velocity (Euler position update).
- New velocity = velocity + acceleration (Euler velocity update; the hitbox's i16F8 acceleration is converted to i32F4 via vector_3i16F8_to__vector_3i32F4, which right-shifts by FRACTIONAL_PERCISION_4__BIT_SIZE = 4 bits, correctly scaling from 8 fractional bits to 4 fractional bits).
- Acceleration is reset to gravity (VECTOR__3i16F8__0_0_nGRAVITY_PER_TICK), the constant base acceleration applied each tick.

The hitbox's own acceleration is consumed into the velocity update and then overwritten with gravity. This is consistent with a game physics model where per-hitbox acceleration represents transient external forces (player input, impulses) that are integrated into velocity, while gravity is the persistent base acceleration. This differs from the collision resolution call sites in collision_resolver_aabb.c (lines 381 and 444), which preserve the hitbox's own acceleration (with modifications), but that difference is expected: collision resolution is a special-case override, while this function is the general movement poll. The computation matches the semantic intent.

Implementation Correctness:
Type compatibility — every argument type matches its target parameter exactly:
- GET_UUID_P(p_hitbox_aabb) yields Identifier__u32 (Serialization_Header.uuid is Identifier__u32; typedef'd as uint32_t in defines_weak.h:60) → matches Identifier__u32 uuid_of__target__u32.
- add_vectors__3i32F4(...) returns Vector__3i32F4 → matches Vector__3i32F4 position__3i32F4 and Vector__3i32F4 velocity__3i32F4.
- vector_3i16F8_to__vector_3i32F4(...) returns Vector__3i32F4 → matches the Vector__3i32F4 operand to add_vectors__3i32F4.
- VECTOR__3i16F8__0_0_nGRAVITY_PER_TICK is (const Vector__3i16F8){0, 0, -GRAVITY_PER_TICK__16F8} → matches Vector__3i16F8 acceleration__3i16F8.
- Hitbox_Kind__AABB is a Hitbox_Kind enum value → matches Hitbox_Kind the_kind_of__hitbox.
No implicit conversions or truncation.

Undefined behavior — no pointer arithmetic beyond GET_UUID_P's standard struct-cast accessor; p_hitbox_aabb is null-checked (break/continue) before any field access; index_of__hitbox is bounded by quantity_of__hitboxes and get_p_hitbox_aabb_by__index_from__hitbox_aabb_manager performs a debug bounds check; no type punning or out-of-bounds array access. p_game is only forwarded to dispatch_game_action__hitbox, not directly dereferenced here.

Validation — debug-only validation of p_hitbox_aabb_manager is appropriate for this low-level polling function; p_game validation is the caller's responsibility (consistent with the pattern in collision_resolver_aabb.c where p_game is also unvalidated). The dirty+active filter correctly gates which hitboxes receive movement updates.

Loop bound note — the loop iterates up to quantity_of__hitboxes rather than index_of__next_hitbox_aabb_in__records. Because allocated hitboxes are contiguous from index 0 (swap-and-pop pool), the loop hits NULL at index_of__next_hitbox_aabb_in__records and breaks. This is functionally correct but iterates through deallocated slots unnecessarily. Using index_of__next_hitbox_aabb_in__records as the bound would be more efficient and self-documenting; not a bug.

Debug message typo — line 328 reads "p_hitobx_aabb_manager" (missing 'x' in "hitbox"). Cosmetic only; debug-only string.

Side Effects:
The function itself performs no direct mutation of hitbox state. It dispatches Game_Action requests (via dispatch_game_action__hitbox → dispatch_game_action_to__server) for each dirty+active hitbox. Each dispatched action will, when resolved by m_process__game_action__hitbox, overwrite the target hitbox's position, velocity, and acceleration. The function is otherwise a read-only poll over the manager's pointer array. No global state is modified directly.

Lavender-Specific Semantics (Initialization ≠ RAII):
Not applicable — the function name contains no "init", "initialize", or "reset" token; it is a movement poll, not an initialization or pool-cleanup routine.
