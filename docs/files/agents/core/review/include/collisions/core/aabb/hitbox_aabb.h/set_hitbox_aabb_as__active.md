set_hitbox_aabb_as__active — core/include/collisions/core/aabb/hitbox_aabb.h

Delegates the active-flag mutation to the shared hitbox-flags layer. Sets the IS_ACTIVE bit on the Hitbox_AABB's flag byte via set_hitbox_flags_as__active.

Pre-conditions:
1. p_hitbox_aabb must be a non-null pointer to a writable Hitbox_AABB object.
2. No other constraints — the target field (hitbox_aabb_flags__u8) accepts any Hitbox_Flags__u8 bit pattern; the function only sets a single flag bit regardless of current state.

Post-conditions:
1. p_hitbox_aabb->hitbox_aabb_flags__u8 has the HITBOX_FLAG__IS_ACTIVE bit set.
2. The previous value of the other flag bits is preserved (OR-semantics).
3. The function returns the new (post-OR) value of the flag byte, which is truthy when the active bit is set.

Correctness Verdict: Correct

Semantic Alignment:
The implementation faithfully fulfills the intent of "set this hitbox as active" by delegating to set_hitbox_flags_as__active, which performs a bitwise-OR of HITBOX_FLAG__IS_ACTIVE onto the flag byte. This matches the Lavender pattern where the per-aabb functions are thin wrappers over the shared hitbox-flags inline functions.

Implementation Correctness:
Type compatibility — p_hitbox_aabb is a Hitbox_AABB *, and hitbox_aabb_flags__u8 is a Hitbox_Flags__u8 member of that struct, matching the Hitbox_Flags__u8 * parameter of set_hitbox_flags_as__active exactly. No implicit conversions or truncation.
No undefined behavior — no pointer arithmetic, no null dereference (caller must pass valid pointer; this is a low-level inline wrapper with no NDEBUG guard, consistent with its sibling flag wrappers at lines 104-131), no type punning, no out-of-bounds access.
No validation is needed — this is a low-level struct-bit mutation. The caller is responsible for ensuring p_hitbox_aabb is valid, matching the convention of the sibling functions is_hitbox_aabb__active, set_hitbox_aabb_as__dirty, set_hitbox_aabb_as__disabled, etc.

Side Effects:
Mutates p_hitbox_aabb->hitbox_aabb_flags__u8 by setting the HITBOX_FLAG__IS_ACTIVE bit. No other members of the struct or any global/external state are touched.
