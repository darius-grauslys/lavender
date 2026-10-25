f_hitbox_aabb_tile_touch_handler__default — core/source/collisions/collision_resolver_aabb.c

Computes a corrective hitbox velocity that pushes the hitbox away from a tile it is touching.

Pre-conditions:
1. p_game must be a valid Game pointer (not dereferenced in body; required by function-pointer signature).
2. p_world must be a valid World pointer (not dereferenced in body; required by function-pointer signature).
3. p_hitbox_aabb must be a non-null pointer to a valid, active Hitbox_AABB.
4. p_tile is a Tile pointer (not dereferenced in body; required by function-pointer signature but unused).
5. x_collision__i32 is the tile-grid x coordinate of the collision point (Signed_Index__i32).
6. y_collision__i32 is the tile-grid y coordinate of the collision point (Signed_Index__i32).

Post-conditions:
1. If delta_x^2 >= delta_y^2: velocity__3i32F4.x__i32F4 of p_hitbox_aabb is overwritten with -(ideal_delta_x - delta_x) >> 2.
2. If delta_x^2 <= delta_y^2: velocity__3i32F4.y__i32F4 of p_hitbox_aabb is overwritten with -(ideal_delta_y - delta_y) >> 2.
3. When delta_x^2 == delta_y^2, both conditions are true and both velocity axes are set.

Correctness Verdict: Correct

Semantic Alignment:
The tile center is reconstructed from the tile-grid coordinates (tile_coord << 4 + 8, i.e. tile-grid position in i32F4 plus half a tile). The delta from the hitbox position to the tile center is computed per-axis. The ideal separation is (tile_size + hitbox_dimension) >> 2, representing one-quarter of the combined sizes. When the x-delta dominates (or equals the y-delta), the x-velocity is set to push the hitbox away; when the y-delta dominates (or equals the x-delta), the y-velocity is set. The negated sign ensures the hitbox is pushed away from the tile. The implementation fulfills the semantic intent correctly.

Implementation Correctness:
Type compatibility — ideal_delta_x and ideal_delta_y are Signed_Index__i32 assigned from Quantity__u32 >> 2 expressions. The unsigned right-shift on Quantity__u32 is well-defined. The result is narrowed to signed int32_t, which is acceptable for tile/hitbox sizes.
Undefined behavior — the expression -(ideal_delta_x - delta_x) >> 2 is parsed as (-(ideal_delta_x - delta_x)) >> 2 due to operator precedence (unary minus binds tighter than >>). The negation produces a negative value when ideal_delta_x > delta_x (the common case). Right-shifting a negative signed integer is implementation-defined in C. The codebase provides ARITHMETRIC_R_SHIFT in numerics.h for portable arithmetic right shifts on potentially-negative values, but this function uses raw >> instead. This is a portability concern; on compilers where >> on negative signed types is arithmetic (the common case), behavior is correct.
Validation — no validation is needed; caller ensures p_hitbox_aabb is valid. The unused p_game, p_world, and p_tile parameters are mandated by the f_Hitbox_AABB_Tile_Touch_Handler function-pointer type.

Side Effects:
Mutates velocity__3i32F4.x__i32F4 and/or velocity__3i32F4.y__i32F4 on p_hitbox_aabb (depending on which axis condition is met). Reads-only from the hitbox AABB struct otherwise.
