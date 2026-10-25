set_center_of__local_space_manager — core/source/world/local_space_manager.c, lines 300-366

## Semantic

Sets the center of a `Local_Space_Manager` to a new global-space coordinate. If the new center is within one chunk (Manhattan distance ≤ 1 on each axis) of the current center, the manager is incrementally shifted via `move_local_space_manager`. If the distance is greater (or the manager was previously uninitialized/out-of-bounds), all local spaces are dropped, the manager is reinitialized with the new center, and all unheld spaces are re-acquired.

## Pre-conditions

1. `p_local_space_manager` must be non-null and point to a valid `Local_Space_Manager` struct.
2. `p_game` must be non-null and point to a valid `Game` instance.
3. `center_of__local_space_manager__3i32` is the desired new center coordinate. It may be `VECTOR__3i32__OUT_OF_BOUNDS` (INT32_MIN on each axis), though this is a degenerate case.
4. If the early-return path is taken (current center equals new center and is not out-of-bounds), no mutation occurs.
5. If the move path is taken, the manager must already be initialized with valid neighbor pointers (`p_local_space__north_west`, etc.) and valid `global_space__vector__3i32` values on its local spaces.

## Post-conditions

1. If the center is unchanged and valid: the function returns immediately. No state is modified.
2. If the distance is within [-1, 1] on each axis (and current center is valid): `move_local_space_manager` is called with the appropriate `Direction__u8` flags, which updates `center_of__local_space_manager__3i32` by ±1 on each relevant axis and shifts local space pointers and global space vectors accordingly.
3. If the distance exceeds 1 on any axis (or current center was out-of-bounds): all global spaces are dropped, the manager is reinitialized via `initialize_local_space_manager` (memset to 0, neighbor pointers re-linked, global space vectors recomputed relative to the new center), all unheld local spaces are re-acquired via `hold_all__unheld_local_spaces_in__local_space_manager`, and `center_of__local_space_manager__3i32` is set to the new center.
4. After return, `p_local_space_manager->center_of__local_space_manager__3i32` equals the `center_of__local_space_manager__3i32` parameter (unless the early-return path was taken, in which case it already matched).

## Correctness Verdict

Correct

## Semantic Alignment

The implementation fulfills the semantic intent of setting the center of the local space manager. The function correctly distinguishes between three cases:

- **No-op case** (center unchanged and valid): Early return is correct.
- **Nearby case** (distance ≤ 1 on each axis): The component-wise difference (`new - current`) is computed via `subtract_vectors__3i32`, and the unsigned wrap-around trick `(u32)distance + 1 < 3` correctly identifies values in {-1, 0, 1}. The direction flags are correctly derived from the sign of each component. `move_local_space_manager` is then called, which updates the center internally by incrementing/decrementing the appropriate axis.
- **Far case** (distance > 1 on any axis, or center was out-of-bounds): The full reload path correctly drops all spaces, reinitializes (Lavender-style: memset + neighbor setup), re-holds spaces, and sets the center.

The variable named `distance_manhattan__3i32` is misleadingly named — it is actually a component-wise difference vector, not a Manhattan distance (which would be a scalar). However, the logic correctly uses it as component-wise differences for both the range check and direction computation, so this is a naming issue, not a correctness bug.

## Implementation Correctness

- **Type compatibility:** The header declares the third parameter as `Chunk_Vector__3i32 chunk_vector__3i32`, while the implementation uses `Global_Space_Vector__3i32 center_of__local_space_manager__3i32`. Both are typedefs for the same `Vector__3i32` struct (defined in `defines.h` lines 107-109), so they are compatible types in C. The parameter name differs between declaration and definition, which is valid in C. No implicit conversions or truncation occur.
- **Undefined behavior:** No null pointer dereferences (the function does not check for null, consistent with the codebase pattern — null-checking is the caller's responsibility). No out-of-bounds array access. No type punning. The unsigned wrap-around cast `(u32)distance + 1` is well-defined for all `i32` values.
- **Validation:** No parameter validation is performed, which is consistent with the codebase pattern (other functions in this file, e.g., `move_local_space_manager`, `initialize_local_space_manager`, also do not validate pointers). Validation is the caller's responsibility.
- **Edge case — center out of bounds:** When the current center is `VECTOR__3i32__OUT_OF_BOUNDS`, the distance is set to `VECTOR__3i32__OUT_OF_BOUNDS` (INT32_MIN per axis). The range check `(u32)INT32_MIN + 1 < 3` evaluates to `2147483649 < 3` = false, correctly routing to the full reload path. This handles the initialization case properly.
- **Edge case — distance = 0:** Caught by the early-return check (current center equals new center and is not out-of-bounds), so the move path with `DIRECTION__NONE` is never reached.
- **Lavender initialization semantics:** `initialize_local_space_manager` is used in the Lavender style — it performs `memset` to zero and resets the struct to initial conditions (cleaning up for pool reuse), NOT RAII-style resource acquisition. This is correct per Lavender conventions.

## Side Effects

- **Move path (nearby):** Calls `move_local_space_manager`, which mutates `p_local_space_manager` by: incrementing/decrementing `center_of__local_space_manager__3i32` on relevant axes, shifting the four (or eight, if `LOCAL_SPACE_MANAGER__DEPTH > 1`) corner `p_local_space_*` pointers via `move_p_ptr_local_space__*` functions, and updating `global_space__vector__3i32` and `p_global_space` on affected local spaces via `update_local_spaces_between__these_two_local_spaces`. Also calls `hold_global_space_within__global_space_manager` and `drop_global_space_within__global_space_manager` on the `Game` instance.
- **Full reload path (far):** Calls `drop_all__local_spaces_in__local_space_manager` (drops all held global spaces), `initialize_local_space_manager` (memset to 0, re-links neighbor pointers, recomputes `global_space__vector__3i32` for each local space based on the new center), `hold_all__unheld_local_spaces_in__local_space_manager` (re-acquires global spaces for all local spaces), and directly sets `center_of__local_space_manager__3i32`.
- **No-op path:** No side effects.
