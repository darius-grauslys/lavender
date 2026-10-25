set_hitbox_aabb_as__disabled — core/include/collisions/core/aabb/hitbox_aabb.h, lines 128-131

Thin wrapper that delegates to set_hitbox_flags_as__disabled, clearing the HITBOX_FLAG__IS_ACTIVE bit on the hitbox_aabb_flags__u8 field of the passed Hitbox_AABB.

Pre-conditions:
1. p_hitbox_aabb must be a non-null pointer to a writable Hitbox_AABB object.

Post-conditions:
1. The HITBOX_FLAG__IS_ACTIVE bit (bit 0) is cleared in p_hitbox_aabb->hitbox_aabb_flags__u8; all other bits are unchanged.
2. Returns the post-assignment flags word coerced to bool (true iff at least one non-active bit remains set).

Correctness Verdict: Correct

Semantic Alignment:
The function delegates directly to set_hitbox_flags_as__disabled, which performs *p &= ~HITBOX_FLAG__IS_ACTIVE on the hitbox_aabb_flags__u8 member. This clears exactly the active bit while preserving all other bits, matching the intent of "set as disabled." No fields are omitted or reordered — the function operates solely on the hitbox_aabb_flags__u8 member of the Hitbox_AABB struct. The delegation is a faithful pass-through with no reinterpretation.

Implementation Correctness:
- Type compatibility: p_hitbox_aabb->hitbox_aabb_flags__u8 is of type Hitbox_Flags__u8 (typedef'd to u8 at defines.h:329), and &p_hitbox_aabb->hitbox_aabb_flags__u8 is Hitbox_Flags__u8 *, which exactly matches the parameter type of set_hitbox_flags_as__disabled(Hitbox_Flags__u8 *). The return type bool matches exactly. No implicit conversions or truncation at the wrapper level.
- Undefined behavior: no pointer arithmetic, no type punning, no out-of-bounds access. The wrapper dereferences p_hitbox_aabb without a null guard; the underlying set_hitbox_flags_as__disabled also performs no null check, so the caller bears responsibility for a valid non-null pointer.
- Validation: none is present. This is consistent with the sibling flag-wrapper functions in the same file (is_hitbox_aabb__dirty, set_hitbox_aabb_as__dirty, set_hitbox_aabb_as__not_dirty, is_hitbox_aabb__active, set_hitbox_aabb_as__active) and with the underlying hitbox.h callee, all of which omit null checks. However, this is inconsistent with the getter/setter functions elsewhere in the same file (e.g., get_position_3i32F4_of__hitbox_aabb, set_size_of__hitbox_aabb), which guard with #ifndef NDEBUG / debug_error. The lack of a debug-build null check here is a minor inconsistency within the file.

Side Effects:
Mutates p_hitbox_aabb->hitbox_aabb_flags__u8 by clearing the HITBOX_FLAG__IS_ACTIVE bit (bit 0); all other bits are preserved. The returned bool reflects the entire post-state flags word.
