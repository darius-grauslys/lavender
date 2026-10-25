is_hitbox_flags__active — core/include/collisions/hitbox.h

Semantic:
Returns true if the active flag bit is set in the hitbox flags.

Pre-conditions:
1. p_hitbox_flags__u8 must be a non-null pointer to a readable Hitbox_Flags__u8 (u8) object.

Post-conditions:
1. Returns a bool that is true iff the HITBOX_FLAG__IS_ACTIVE bit is set in *p_hitbox_flags__u8.
2. The pointed-to value is not modified.

Correctness Verdict: Correct

Semantic Alignment:
The function ANDs the flags byte with the active flag constant (HITBOX_FLAG__IS_ACTIVE = BIT(0) = 1U), yielding a nonzero (truthy) value when the active bit is set and zero otherwise. This correctly fulfills the intent of querying the active flag. The implicit bool conversion of the bitwise-AND result is well-defined (nonzero converts to true).

Implementation Correctness:
- Type compatibility: *p_hitbox_flags__u8 is Hitbox_Flags__u8 (u8 / uint8_t); HITBOX_FLAG__IS_ACTIVE is BIT(0) = (1U) << 0 = 1U, an unsigned int. The u8 operand is promoted to unsigned int for the &, so no truncation occurs on the query path (the result is not reassigned to a u8). The unsigned int result is then implicitly converted to bool (nonzero -> true) — well-defined.
- No undefined behavior: no pointer arithmetic, no null dereference (the caller must pass non-null per the pre-condition), no type punning, no out-of-bounds access.
- Validation: none needed for this low-level inline accessor; ensuring the pointer is non-null is the caller's responsibility, consistent with the file's other accessors.

Side Effects:
No side effects. The pointed-to byte is only read; no mutation occurs.
