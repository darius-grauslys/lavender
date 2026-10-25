is_this_hitbox_aabb__overlapping_this_hitbox_aabb — core/source/collisions/core/aabb/hitbox_aabb.c

Determines whether the swept (moving) corners of hitbox__one (position + velocity) overlap the static hitbox__two, and if so returns the movement direction(s) that caused the collision.

Pre-conditions:
1. hitbox__one must be a non-null pointer to a valid, initialized Hitbox_AABB object.
2. hitbox__two must be a non-null pointer to a valid, initialized Hitbox_AABB object.
3. No validation is performed in this function; null-safety is delegated to the debug-mode guards in the helper functions, and is the caller's responsibility (consistent with engine convention).

Post-conditions:
1. If no corner of hitbox__one (at its moving position) overlaps hitbox__two, returns DIRECTION__NONE.
2. If a collision is detected, returns one or more Direction__u8 bit flags (EAST, WEST, NORTH, SOUTH) indicating which movement axis caused the collision.
3. If a collision is detected but the direction cannot be determined from the static-position checks, returns DIRECTION__ANY (all bits set).

Correctness Verdict: Correct

Semantic Alignment:
The implementation matches the intended semantic. Phase 1 computes the swept corners of hitbox__one via initialize_vector_3i32F4_as__aa_bb (which adds velocity to the position-derived corner) and the static corners of hitbox__two via initialize_vector_3i32F4_as__aa_bb_without__velocity. The four containment checks (using strict > and <) plus the two alignment checks (using ==) correctly detect corner-interior and edge-touching overlap. The header's documented limitation — that a fully-encompassing hitbox__two yields DIRECTION__NONE because no corner of hitbox__one falls inside it — is acknowledged in the header comment (lines 82-85) and is consistent with the corner-only check approach.

Phase 2 (get_direction) re-computes containment/alignment using the static (pre-movement) corners of hitbox__one against hitbox__two, and maps the result to the movement direction returned by get_movement_direction_of__hitbox_aabb. The axis logic is correct: east/west collision requires vertical (y-axis) overlap between the static boxes; north/south collision requires horizontal (x-axis) overlap. For pure single-axis movement the direction is determined correctly. For diagonal movement where the static position has no axis overlap, neither direction is registered and the function returns DIRECTION__ANY — a well-defined fallback for ambiguous diagonal collisions.

Implementation Correctness:
Type compatibility — All types match exactly. Direction__u8 (uint8_t typedef'd from uint8_t) is used for return and direction variables. Vector__3i32F4 local variables are passed to helper functions expecting Vector__3i32F4*. The Direction__ bit macros (DIRECTION__EAST = BIT(1) = 2U, etc.) are unsigned int and are safely combined with uint8_t via bitwise & and |=; no value within the defined direction range is truncated. The ternary (DIRECTION__NONE == direction_of_collision) ? DIRECTION__ANY : direction_of_collision produces DIRECTION__ANY (63U) which fits in uint8_t, so no truncation occurs on return.

Undefined behavior — No pointer arithmetic. No null dereference: debug-mode null guards exist in the helper functions (lines 117-121, 165-169), and the top-level function has no dereference of its own (it passes pointers directly to helpers). No type punning. No out-of-bounds array access — only struct field accesses occur. The goto jumps to get_direction within the same function scope; the label is followed by an empty statement (;) then variable declarations with no initializers in the declarations themselves. The variables are initialized immediately by subsequent initialize_vector_3i32F4_as__aa_bb_without__velocity calls after the jump, so no uninitialized variable is ever read.

Validation — No null checks at the top level is appropriate for this function's role as a low-level geometric query. Validation is the caller's responsibility, consistent with is_hitbox_aabb__colliding and other functions in this translation unit.

Side Effects: No side effects. The function is a pure geometric query. It does not modify hitbox__one or hitbox__two (the helper functions only read from them to compute corner vectors). Only local stack variables are written.
