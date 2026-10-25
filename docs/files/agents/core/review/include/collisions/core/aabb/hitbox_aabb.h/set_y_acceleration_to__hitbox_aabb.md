set_y_acceleration_to__hitbox_aabb — core/include/collisions/core/aabb/hitbox_aabb.h

Sets the y-component of the acceleration vector on a Hitbox_AABB and marks the hitbox as dirty.

Pre-conditions:
1. p_hitbox_aabb must be a non-null pointer to a writable Hitbox_AABB object (checked only in non-NDEBUG / debug builds; in release builds the caller is responsible).
2. y__acceleration is any i16F8 value (int16_t with 8 fractional bits); no range constraint is imposed or expected.

Post-conditions:
1. p_hitbox_aabb->acceleration__3i16F8.y__i16F8 is set to the value of y__acceleration.
2. p_hitbox_aabb's hitbox_aabb_flags__u8 dirty flag is set (via set_hitbox_aabb_as__dirty) prior to the assignment.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills its semantic intent: it writes the y-component of the acceleration vector to the hitbox and marks the hitbox dirty so downstream collision/integration code knows to recompute. The field name y__i16F8 correctly targets the y-component of the acceleration member, matching the function's purpose.

Implementation Correctness:
Type compatibility — the parameter y__acceleration is i16F8 (int16_t) and the target field acceleration__3i16F8.y__i16F8 is also i16F8; the types match exactly with no implicit conversion or truncation.
No undefined behavior — no pointer arithmetic, no null dereference (guarded by the debug null-check and by caller responsibility in release), no type punning, no out-of-bounds access.
Validation — the null check is guarded by #ifndef NDEBUG, consistent with all sibling setter functions in this file (e.g. set_x_acceleration_to__hitbox_aabb at lines 416-427, set_z_acceleration_to__hitbox at lines 444-455). The return-after-error pattern prevents the subsequent dereference when p_hitbox_aabb is null in debug builds. In release builds validation is the caller's responsibility, which is the established pattern for these low-level inline setters.
Note: the debug_error message string says "set_y_acceleration_to__hitbox" (omitting the "_aabb" suffix), matching the identical labeling in the sibling x and z functions. This is a cosmetic inconsistency in the log message, not a correctness defect.

Side Effects:
1. Mutates p_hitbox_aabb->acceleration__3i16F8.y__i16F8 (sets the y-acceleration).
2. Mutates p_hitbox_aabb->hitbox_aabb_flags__u8 (sets the dirty flag via set_hitbox_aabb_as__dirty, which itself calls set_hitbox_flags_as__dirty on the same struct member).
