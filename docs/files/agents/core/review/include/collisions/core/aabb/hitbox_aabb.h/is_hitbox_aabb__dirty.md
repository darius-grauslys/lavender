is_hitbox_aabb__dirty — core/include/collisions/core/aabb/hitbox_aabb.h, lines 103-106

Checks whether the dirty flag bit is set on a Hitbox_AABB's flags field.

Pre-conditions:
1. p_hitbox_aabb must be a non-null pointer to a validly initialized Hitbox_AABB object.

Post-conditions:
1. Returns true if the HITBOX_FLAG__IS_DIRTY bit (bit 1) is set in p_hitbox_aabb->hitbox_aabb_flags__u8; false otherwise.
2. The Hitbox_AABB struct is not modified.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly queries the dirty flag. It delegates to is_hitbox_flags__dirty, which tests the HITBOX_FLAG__IS_DIRTY bit (BIT(1)) against the flags u8. This matches the semantic intent: returning whether the hitbox is marked dirty.

Implementation Correctness:
Type compatibility — p_hitbox_aabb is Hitbox_AABB *, and hitbox_aabb_flags__u8 is Hitbox_Flags__u8 (a u8 typedef). The address &p_hitbox_aabb->hitbox_aabb_flags__u8 is passed to is_hitbox_flags__dirty, which expects Hitbox_Flags__u8 *. The types match exactly; no implicit conversion or truncation.
No undefined behavior — no pointer arithmetic, no type punning, no out-of-bounds access. The only dereference reads p_hitbox_aabb->hitbox_aabb_flags__u8; a null p_hitbox_aabb would be UB, but that is the caller's responsibility (consistent with all sibling inline flag functions such as set_hitbox_aabb_as__dirty and is_hitbox_aabb__active, which also do not null-check).
No validation is needed — this is a low-level inline accessor. Null-check overhead would contradict the inline-query role and the codebase convention. The caller is responsible for ensuring p_hitbox_aabb is valid.

Side Effects:
No side effects — the only observable effect is reading the flags field and returning a bool.
