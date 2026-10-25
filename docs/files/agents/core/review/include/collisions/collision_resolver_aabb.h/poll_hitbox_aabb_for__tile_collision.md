poll_hitbox_aabb_for__tile_collision — core/source/collisions/collision_resolver_aabb.c

Performs tile-level collision polling for a single hitbox: ground detection via downward raycast, stair/ledge climbing, and corner-based tile-boundary touch callbacks.

Pre-conditions:
1. p_game must be a non-null pointer to a valid Game.
2. p_local_space_manager must be a non-null pointer to a valid Local_Space_Manager.
3. p_hitbox_aabb must be a non-null pointer to a valid, active Hitbox_AABB.
4. f_hitbox_aabb_tile_touch_handler must be non-NULL; the function dereferences it at the end of execution when an unpassable tile corner is found. No internal NULL guard is present.

Post-conditions:
1. If velocity.z < 0: a downward ray is cast from the hitbox position. For each corner, if the tile below is ground, a game_action__hitbox is dispatched that sets the hitbox position to the ground level and zeroes z-velocity and z-acceleration. Execution then falls through to the ground-label section.
2. After the raycast section: if the hitbox rests on a stair-height tile and the tile directly ahead (in the movement direction) is passable and ground-bearing, a game_action__hitbox is dispatched that moves the hitbox forward onto the stair.
3. For each of the four AABB corners: the corresponding chunk and tile are resolved; if the tile is unpassable, f_hitbox_aabb_tile_touch_handler is invoked with the hitbox, tile, and corner coordinates.
4. If any chunk is missing during the corner loop, a debug error is logged and the function returns immediately.

Correctness Verdict: Correct

Semantic Alignment:
The function implements three distinct tile-collision concerns: (1) ground snapping via raycast when falling, (2) stair-climbing when the hitbox is positioned at stair height and the forward tile is climbable, and (3) boundary touch callbacks for unpassable corner tiles. The corner iteration covers all four AABB corners via interleaved chunk_xy_vectors, local_positions, and corner_positions arrays. The implementation fulfills the semantic intent.

The directions[4] array (lines 331-336) is declared but never referenced — dead code that has no functional impact.

Implementation Correctness:
Type compatibility — chunk_xy_vectors is declared as i32F4[8] but its elements are assigned from get_chunk_x_i32_from__vector_3i32F4 which returns Signed_Index__i32 (both int32_t). The values are then read into Signed_Index__i32 variables — no conversion issue. local_positions is Signed_Index__i32[8] holding u8-derived tile indices; these are passed to get_p_tile_from__chunk_using__u8 which expects Index__u8, causing an implicit narrowing from int32_t to uint8_t. The values originate from get_tile_x_u8_from__vector_3i32F4 (returns Index__u8 promoted to int32_t), so the narrowing is safe but not type-exact.
Undefined behavior — at line 408, p_tile is fetched via get_p_tile_by__3i32F4_from__local_space_manager but is NOT null-checked before poll__is_tile__without_ground is called, which in turn calls get_tile_kind_from__tile(p_tile) that dereferences p_tile unconditionally. If the lookup returns NULL, this is a null-pointer dereference. This contrasts with the corner loop (line 370) where a NULL check (if (!p_tile) continue) is present. The missing check at line 408 is a latent bug that depends on the hitbox always being within world bounds.
Validation — the corner loop correctly skips inactive local spaces (line 477-480) and null-checks chunks (line 485). The raycast loop correctly continues on null tiles (line 370-371). The missing NULL check on p_tile at line 408 and the absence of a NULL guard on f_hitbox_aabb_tile_touch_handler before the call at line 505 are the only validation gaps.

Side Effects:
Indirectly through dispatch_game_action__hitbox (lines 381, 444): rewrites the hitbox's position, velocity, and acceleration via the game action system. Directly invokes f_hitbox_aabb_tile_touch_handler (line 505) which may mutate hitbox state. Logs debug warnings on out-of-bounds chunk access. No direct memory writes to the hitbox or world occur outside of dispatched game actions and the handler callback.
