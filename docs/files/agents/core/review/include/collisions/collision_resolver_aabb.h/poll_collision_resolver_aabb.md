poll_collision_resolver_aabb — core/source/collisions/collision_resolver_aabb.c

Iterates over every hitbox in the manager and polls for tile collisions and AABB-vs-AABB collisions across the hitbox's local space and its eight neighbors.

Pre-conditions:
1. p_game must be a non-null pointer to a valid Game.
2. p_hitbox_aabb_manager must be a non-null pointer to a valid Hitbox_AABB_Manager with an active pool.
3. f_hitbox_aabb_collision_handler may be NULL; when NULL, AABB-vs-AABB collision polling is skipped.
4. f_hitbox_aabb_tile_touch_handler may be NULL; when non-NULL, it is forwarded to each tile-collision poll.

Post-conditions:
1. Each active hitbox in the manager is fetched by index and polled for tile collisions via poll_hitbox_aabb_for__tile_collision (when the collision handler is non-NULL).
2. For each active hitbox, AABB-vs-AABB collision polling occurs against the center local space and up to eight neighbor collision nodes (north, north-east, east, south-east, south, south-east [BUG], west, south-west, north-west).
3. Hitboxes whose local-space manager cannot be resolved are skipped.

Correctness Verdict: Incorrect

Semantic Alignment:
The intended behavior is a 3x3 grid scan of local spaces around the hitbox, polling each for AABB collisions. However, two defects cause the semantic intent to fail:
1. Tile-collision polling is guarded by (f_hitbox_aabb_collision_handler) instead of (f_hitbox_aabb_tile_touch_handler) on line 151. If the collision handler is NULL but a tile-touch handler is provided, tile collision polling is silently skipped, defeating the purpose of the tile-touch handler.
2. The south-neighbor block (lines 231-242) checks is_local_space__active(p_local_space->p_local_space__south) but then passes p_local_space->p_local_space__east to get_p_collision_node_from__local_space. This copy-paste bug means the south local space is conditionally checked but the east local space's collision node is polled instead.

Implementation Correctness:
Type compatibility — all parameter types match their function signatures. Index__u32 is used consistently for the hitbox index loop.
Undefined behavior — get_p_collision_node_from__local_space and get_p_chunk_from__local_space both handle NULL by returning 0, so the is_local_space__active guards prevent null dereferences on neighbor chains. No out-of-bounds array access occurs. However, the logical mismatch in the south-neighbor block (checking south, polling east) results in incorrect collision polling, not a crash.
Validation — the function relies on is_local_space__active to null-check local spaces, which is sufficient. The #warning at line 147 marks an unresolved TODO for disposing orphaned hitboxes.

Side Effects:
Indirectly through callees: poll_hitbox_aabb_for__tile_collision may dispatch game_action__hitbox calls that rewrite hitbox position/velocity; poll_for__collisions_within_this__collision_node may invoke f_hitbox_aabb_collision_handler which mutates hitbox velocities. The function itself does not directly mutate any memory.
