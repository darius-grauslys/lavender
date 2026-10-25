offset_z_position_to__hitbox_aabb — core/include/collisions/core/aabb/hitbox_aabb.h

Offsets the z-component of the hitbox AABB's position by the provided delta and marks the hitbox as dirty.

Pre-conditions:
1. p_hitbox_aabb must be a non-null pointer to a writable Hitbox_AABB object (null check is debug-only under NDEBUG; release builds place this on the caller).
2. z__position is any i32F4 (int32_t); no range constraint.

Post-conditions:
1. p_hitbox_aabb->position__3i32F4.z__i32F4 is incremented by z__position.
2. p_hitbox_aabb is marked as dirty (the dirty flag in hitbox_aabb_flags__u8 is set via set_hitbox_aabb_as__dirty).
3. All other fields (x/y position, velocity, acceleration, size, other flags) remain unchanged.

Correctness Verdict: Correct

Semantic Alignment:
The function adds z__position to the z-component of position__3i32F4 — matching the "offset" intent. Marking the hitbox dirty is consistent with all sibling position/velocity mutators in this file (e.g., offset_y_position_to__hitbox_aabb, set_z_position_to__hitbox_aabb). The implementation fulfills the semantic intent.

Implementation Correctness:
Type compatibility — z__position is i32F4 (int32_t) and p_hitbox_aabb->position__3i32F4.z__i32F4 is i32F4 (int32_t); types match exactly with no implicit conversion or truncation.
No undefined behavior — the debug-only null guard returns early before any dereference; no pointer arithmetic, no type punning, no out-of-bounds access. Signed overflow on the += is technically UB in C, but this is not a defect unique to this function — every apply/set velocity and position mutator in this file uses the same += pattern, so no additional overflow guard is appropriate at this layer.
Validation — the debug-only null check is consistent with all sibling mutators in this file; no field/range validation is appropriate for this low-level offset routine. Caller responsibility matches the established convention.
Minor observation: the debug_error string reads "offset_z_position_to__hitbox" (truncated, dropping the "_aabb" suffix). This is consistent with every sibling function in this file and is an established naming convention for these error messages, not a correctness defect.

Side Effects:
Mutates p_hitbox_aabb: increments position__3i32F4.z__i32F4 by z__position, and sets the dirty flag in hitbox_aabb_flags__u8 (via set_hitbox_aabb_as__dirty).