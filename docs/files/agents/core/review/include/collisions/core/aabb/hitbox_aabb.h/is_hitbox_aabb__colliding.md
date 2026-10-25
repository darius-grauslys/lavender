is_hitbox_aabb__colliding — core/source/collisions/core/aabb/hitbox_aabb.c

Delegates to is_this_hitbox_aabb__overlapping_this_hitbox_aabb to detect whether two AABB hitboxes are colliding and, if so, returns the direction(s) of collision.

Pre-conditions:
1. hitbox__checking must be a non-null pointer to a valid Hitbox_AABB object.
2. hitbox__other must be a non-null pointer to a valid Hitbox_AABB object.

Post-conditions:
1. Returns a Direction__u8 (u8) bitmask indicating the collision direction:
   - DIRECTION__NONE (0): no collision detected.
   - A specific direction bitmask (e.g. DIRECTION__EAST): the direction(s) of collision between the two hitboxes.
   - DIRECTION__ANY (MASK(6)): overlap was detected but no specific movement direction matched, so direction is indeterminate.

Correctness Verdict: Correct

Semantic Alignment:
The function's intent is to determine whether two hitboxes are colliding and return the collision direction. The implementation fulfills this intent by directly delegating to is_this_hitbox_aabb__overlapping_this_hitbox_aabb, passing hitbox__checking as hitbox__one and hitbox__other as hitbox__two. The helper performs the actual AABB corner/edge overlap detection and direction computation. The delegation is a straightforward passthrough with no transformation of the parameters, so the semantic intent is fully preserved.

Implementation Correctness:
Type compatibility — hitbox__checking (Hitbox_AABB *) matches the helper's hitbox__one parameter (Hitbox_AABB *); hitbox__other (Hitbox_AABB *) matches hitbox__two (Hitbox_AABB *); both the caller and callee return Direction__u8. No implicit conversions or truncation.
Undefined behavior — No pointer arithmetic, no null dereference, no type punning, and no out-of-bounds access in this function. The two pointers are forwarded to the helper without dereferencing them directly here.
Validation — No validation is performed in this function. Both pointers are assumed to be valid. This is consistent with the codebase convention: validation is the caller's responsibility at this level of abstraction.

Side Effects:
No side effects — the function is read-only. It forwards both hitbox pointers to the helper, which computes corner/edge positions and movement direction without modifying either hitbox. Neither hitbox__checking nor hitbox__other is mutated.

Note: The helper function has a documented limitation (see hitbox_aabb.h lines 82-86): if hitbox__other is fully contained within hitbox__checking without any edge alignment, the helper returns DIRECTION__NONE even though the hitboxes overlap. This limitation is inherited by this wrapper.
