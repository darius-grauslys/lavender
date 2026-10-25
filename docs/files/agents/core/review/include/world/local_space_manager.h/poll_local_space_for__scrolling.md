poll_local_space_for__scrolling — core/source/world/local_space_manager.c, lines 918-958

Gradually scrolls the local space manager's center toward a target global space vector by computing a per-axis direction and calling move_local_space_manager in a loop until the center matches the target.

Pre-conditions:
1. p_local_space_manager must be non-null and properly initialized — center_of__local_space_manager__3i32 must be a valid Vector__3i32 (not VECTOR__3i32__OUT_OF_BOUNDS), and all corner pointer fields must point to valid Local_Space entries within the local_spaces array.
2. p_game must be non-null (passed through to move_local_space_manager, which uses it to access the global space manager).
3. p_global_space_manager is accepted as a parameter but is NOT referenced anywhere in the function body. The global space manager is instead accessed indirectly through p_game.
4. global_space_vector__center__3i32 is the target center position; should be a valid chunk vector (not out of bounds) for the scroll to converge.

Post-conditions:
1. p_local_space_manager->center_of__local_space_manager__3i32 equals global_space_vector__center__3i32 upon return.
2. The local space manager's corner pointers (p_local_space__north_west, etc.) and the global_space__vector__3i32 / p_global_space fields of affected Local_Space entries have been updated to reflect the new center (via move_local_space_manager).

Correctness Verdict: Correct

Semantic Alignment:
The function fulfills its semantic intent of gradually scrolling the local space manager to center on a target global space vector. The direction is computed as the sign of each per-axis delta, and move_local_space_manager moves the center by exactly one step in each indicated direction. Because the direction always points toward the target, the Manhattan distance decreases monotonically and the do-while loop converges.

The p_global_space_manager parameter is unused — it is accepted but never read. This is a code quality concern rather than a correctness bug, since the global space manager is accessible through p_game. However, it is misleading to callers and suggests the signature may be incomplete or carry a stale parameter.

Implementation Correctness:
Type compatibility — all parameter types match the expected types. Direction__u8 is uint8_t; the direction flags (each a single BIT) are correctly combined with |= and passed to move_local_space_manager which expects Direction__u8.

No undefined behavior in the normal path — no pointer arithmetic, no null dereference, no type punning, no out-of-bounds array access.

Potential issues:
1. Infinite loop when LOCAL_SPACE_MANAGER__DEPTH == 1 and z coordinates differ: The UPWARDS and DOWNWARDS movement blocks in move_local_space_manager are guarded by #if LOCAL_SPACE_MANAGER__DEPTH > 1. When DEPTH is 1 (the default), those blocks are compiled out, so move_local_space_manager never modifies center_of__local_space_manager__3i32.z__i32. If poll_local_space_for__scrolling is called with a target z that differs from the current z, the direction will include DIRECTION__UPWARDS or DIRECTION__DOWNWARDS, but move_local_space_manager will silently ignore it. The z component of the center never changes, the loop condition never becomes true, and the do-while loop never terminates. In practice this does not occur with 2D gameplay (DEPTH == 1 implies a single z-level), but the function provides no guard against it.

2. Integer overflow when center is out of bounds: If center_of__local_space_manager__3i32 is VECTOR__3i32__OUT_OF_BOUNDS (each component = BIT(31) = -2147483648 as i32), the delta computation (target - center) can overflow a 32-bit signed integer, resulting in undefined behavior. The sibling function set_center_of__local_space_manager explicitly checks for this case and reinitializes, but poll_local_space_for__scrolling does not.

Side Effects:
Mutates p_local_space_manager — updates center_of__local_space_manager__3i32, corner pointer fields, and the global_space__vector__3i32 and p_global_space fields of traversed Local_Space entries (all via move_local_space_manager). No direct side effects on p_global_space_manager (it is unused).
