move_local_space_manager — core/source/world/local_space_manager.c

Shifts the local space manager's rendering window by one step in the given direction(s), updating corner pointers and reloading global spaces along the newly exposed edge.

Pre-conditions:
1. `p_local_space_manager` must be a non-null pointer to an initialized `Local_Space_Manager`.
2. `p_game` must be a non-null pointer to a valid `Game` instance with an initialized `Global_Space_Manager`.
3. `direction__u8` is a bitmask of `DIRECTION__*` flags. At least one direction bit should be set for meaningful work; `DIRECTION__NONE` results in no-op behavior.
4. The `Local_Space_Manager` must have been previously initialized via `initialize_local_space_manager` (or `load_local_space_manager_at__global_space_vector__3i32`), so that all corner pointers (`p_local_space__north_west`, `p_local_space__north_east`, `p_local_space__south_west`, `p_local_space__south_east`, and their `__top` variants when `LOCAL_SPACE_MANAGER__DEPTH > 1`) are valid and the toroidal neighbor links (`p_local_space__north`, `p_local_space__east`, `p_local_space__south`, `p_local_space__west`, `p_local_space__above`, `p_local_space__below`) are correctly established.
5. When `LOCAL_SPACE_MANAGER__DEPTH > 1`, the `DIRECTION__UPWARDS` and `DIRECTION__DOWNWARDS` bits are only processed inside the `#if LOCAL_SPACE_MANAGER__DEPTH > 1` guard.

Post-conditions:
1. `center_of__local_space_manager__3i32` is incremented by 1 in each axis corresponding to a set direction bit (NORTH/SOUTH affect `.y__i32`, EAST/WEST affect `.x__i32`, UPWARDS/DOWNWARDS affect `.z__i32`).
2. All eight corner pointers (four bottom-layer and four top-layer, when `DEPTH > 1`) are shifted in the requested direction(s) by following the corresponding `p_local_space__*` neighbor pointer (which wraps toroidally).
3. The global spaces along the newly exposed edge are dropped (if their existing chunk vector does not match the expected position) and reloaded via `hold_global_space_within__global_space_manager`, with each local space's `global_space__vector__3i32` field updated to the correct chunk vector for its new position.
4. For diagonal moves (e.g., NORTH|EAST), the 2D direction blocks execute first (NORTH/SOUTH, then EAST/WEST), followed by the 3D direction block (UPWARDS/DOWNWARDS). Each block correctly uses the already-updated corner pointers from prior blocks.
5. No return value (void).

Correctness Verdict: Correct

Semantic Alignment:
The function correctly shifts the local space manager's window in any combination of the six cardinal directions. For each direction, it:
- Updates the center coordinate.
- Computes `chunk_vector__start__3i32` from the appropriate corner pointer's `global_space__vector__3i32` (north_west__top for UPWARDS, north_west for DOWNWARDS), then adjusts the z-component by ±1 to target the new layer.
- Moves all eight corner pointers by following the corresponding neighbor pointer (toroidal wraparound).
- Sets `p_local_space__current` and `p_local_space__end` to the appropriate corner pointers after the move.
- Calls `update_local_spaces_between__these_two_local_spaces` to reload global spaces along the newly exposed edge.

The traversal pattern for UPWARDS/DOWNWARDS differs from the 2D directions: instead of iterating over z-levels with `dz_update` and traversing EAST, it iterates over x-columns (incrementing `chunk_vector__start__3i32.x__i32` and moving `p_local_space__end` east) while traversing SOUTH within each column. This correctly covers the entire new top/bottom layer.

For diagonal 2D+3D moves (e.g., NORTH|UPWARDS), the NORTH block runs first and updates the north edge (including the top layer), so the UPWARDS block's `chunk_vector__start__3i32` computation uses the already-updated `p_local_space__north_west__top->global_space__vector__3i32`, which is correct.

The `chunk_vector__start__3i32` is passed by value to `update_local_spaces_between__these_two_local_spaces`, so modifications inside that function (y-decrement for SOUTH traversal) do not affect the caller's copy. The caller only increments x between columns, preserving the correct y (north) starting value for each column.

Implementation Correctness:
Type compatibility: All pointer and parameter types match their target field/function types exactly. `Direction__u8` is `uint8_t`, matching the bitmask flags. `Chunk_Vector__3i32` is passed by value (struct copy), which is correct for the per-column start vector.
Undefined behavior: No null pointer dereferences occur under normal operation — corner pointers are always valid after initialization. The `move_p_ptr_local_space__upwards`/`downwards` functions follow `p_local_space__above`/`p_local_space__below` neighbor pointers, which are guaranteed non-null by the toroidal initialization in `initialize_local_space_manager`. No out-of-bounds array access occurs — all local space access is through neighbor pointers.
Validation: No runtime validation is performed for `direction__u8` or pointer nullity, which is consistent with the function's role as a low-level internal helper called only after `set_center_of__local_space_manager` or `poll_local_space_for__scrolling` have validated the movement parameters.

Side Effects:
Mutates `p_local_space_manager` — specifically `center_of__local_space_manager__3i32` and all eight corner pointer fields, as well as `global_space__vector__3i32` and `p_global_space` fields of the local spaces along the newly exposed edge. Calls `drop_global_space_within__global_space_manager` and `hold_global_space_within__global_space_manager` (via `update_local_spaces_between__these_two_local_spaces`), which may allocate or deallocate `Global_Space` objects.
