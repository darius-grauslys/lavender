get_tile_transition_direction_of__hitbox_aabb — core/source/collisions/core/aabb/hitbox_aabb.c

Determines which cardinal tile boundaries the hitbox will cross given its current position and velocity, by projecting corner positions (with velocity) against the center tile position.

Pre-conditions:
1. hitbox must be a non-null pointer to an initialized Hitbox_AABB.
2. aa must be a non-null pointer to a writable Vector__3i32F4 (output — SW corner with velocity).
3. bb must be a non-null pointer to a writable Vector__3i32F4 (output — NE corner with velocity).

Post-conditions:
1) aa is mutated to hold the SW corner position of the hitbox including velocity.
2) bb is mutated to hold the NE corner position of the hitbox including velocity.
3) The return value is a Direction__u8 bitmask of DIRECTION__NONE or any combination of DIRECTION__EAST, DIRECTION__WEST, DIRECTION__NORTH, DIRECTION__SOUTH — set only for directions in which the movement direction is active and the corresponding projected corner crosses a tile boundary relative to the center tile.

Correctness Verdict: Correct

Semantic Alignment:
The function fulfills its semantic intent. It obtains the movement direction from the hitbox's velocity, computes the center tile position from the hitbox's position without velocity, then computes the SW and NE corner vectors including velocity (via initialize_vector_3i32F4_as__aa_bb with DIRECTION__SOUTH_WEST and DIRECTION__NORTH_EAST respectively). It then checks each cardinal direction:
- EAST: the NE corner (bb, with velocity) has an x-tile position greater than the center — correct, since the NE corner is the easternmost extent.
- WEST: the SW corner (aa, with velocity) has an x-tile position less than the center — correct, since the SW corner is the westernmost extent.
- NORTH: the NE corner (bb, with velocity) has a y-tile position greater than the center — correct, since the NE corner is the northernmost extent.
- SOUTH: the SW corner (aa, with velocity) has a y-tile position less than the center — correct, since the SW corner is the southernmost extent.
The guard `direction_of_movement & DIRECTION__<X>` ensures transitions are only reported for directions the hitbox is actually moving, preventing false positives from large hitboxes that already span multiple tiles when stationary.

Implementation Correctness:
Type compatibility — all parameter and local types match their targets exactly: Direction__u8 for direction values, Signed_Index__i32 for tile positions (matching the return type of normalize_xyz_i32F4_to__tile_xyz_i32), Vector__3i32F4 * for aa/bb (matching initialize_vector_3i32F4_as__aa_bb's parameter). No implicit conversions or truncation.
Undefined behavior — no pointer arithmetic, no type punning, no out-of-bounds access. The function directly accesses hitbox->position__3i32F4.x__i32F4 and .y__i32F4 on lines 260 and 263 without its own NULL check; however, get_movement_direction_of__hitbox_aabb is called first and performs a debug-mode NULL check, following the codebase convention where callers are expected to provide valid non-null pointers.
Validation — validation is appropriate for the function's low-level role. No debug-mode NULL check is performed on aa or bb (output parameters), consistent with the codebase pattern where output parameters are the caller's responsibility. The hitbox pointer is not checked in this function but is relied upon to be non-null by the call site.

Side Effects:
Mutates the vectors pointed to by aa and bb (writing their x, y, and z components via initialize_vector_3i32F4_as__aa_bb). Does not modify hitbox or any global state. The return value is a bitmask of detected tile transitions.
