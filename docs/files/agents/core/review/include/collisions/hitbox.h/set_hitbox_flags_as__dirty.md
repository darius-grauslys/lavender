set_hitbox_flags_as__dirty — core/include/collisions/hitbox.h

Semantic:
Sets the dirty flag bit to 1 in the hitbox flags, returning the resulting flags coerced to bool.

Pre-conditions:
1. p_hitbox_flags__u8 must be a non-null pointer to a writable Hitbox_Flags__u8 (u8) object.

Post-conditions:
1. The HITBOX_FLAG__IS_DIRTY bit is set (1) in *p_hitbox_flags__u8; all other bits are unchanged.
2. Returns the post-assignment *p_hitbox_flags__u8 coerced to bool. Because the dirty bit was just set, the return is guaranteed to be true (nonzero).

Correctness Verdict: Correct

Semantic Alignment:
The expression *p |= HITBOX_FLAG__IS_DIRTY performs a bitwise-OR-assign that sets exactly the dirty bit while preserving every other bit. This matches the intent of "set as dirty." The returned value is the new flags word coerced to bool; since the dirty bit is now set, the result is always true, which is consistent with "dirty is now set."

Implementation Correctness:
- Type compatibility: the LHS *p is Hitbox_Flags__u8 (u8); the RHS HITBOX_FLAG__IS_DIRTY is BIT(1) = 2U, an unsigned int. The |= promotes the u8 to unsigned int, ORs, and assigns the result back to the u8 lvalue (truncation to u8). The dirty bit value 2 fits within u8, and all other bits are preserved through the truncation, so no information is lost. The return converts the unsigned int result to bool, which is well-defined (nonzero -> true).
- No undefined behavior: no pointer arithmetic, no null dereference, no out-of-bounds access, no type punning.
- Validation: none required; the caller must supply a non-null pointer.

Side Effects:
Mutates *p_hitbox_flags__u8 by setting the HITBOX_FLAG__IS_DIRTY bit (bit 1). All other bits are preserved.
