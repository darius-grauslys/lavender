get_position_3i32_of__hitbox_aabb — core/include/collisions/core/aabb/hitbox_aabb.h

Converts the hitbox's 4-bit fixed-point position (Vector__3i32F4) to an integer position (Vector__3i32) by applying an arithmetic right-shift by 4 bits per component.

Pre-conditions:
1. p_hitbox_aabb must be a non-null pointer to a readable Hitbox_AABB object (enforced via debug_error in debug builds; release builds assume validity, consistent with the codebase's NDEBUG pattern).

Post-conditions:
1. Returns a Vector__3i32 whose x, y, z components are the integer equivalents of the hitbox's position__3i32F4 field (via i32F4_to__i32, a right-shift by FRACTIONAL_PERCISION_4__BIT_SIZE = 4).
2. The pointed-to Hitbox_AABB is not modified.

Correctness Verdict: Correct

Semantic Alignment:
The function retrieves the position__3i32F4 field from the Hitbox_AABB struct and converts it to Vector__3i32 via vector_3i32F4_to__vector_3i32, which calls i32F4_to__i32 (arithmetic right-shift by 4) on each component. This matches the semantic intent of returning the hitbox's position as an integer vector. The computation is correct.

Implementation Correctness:
Type compatibility — the return type Vector__3i32 matches the return type of vector_3i32F4_to__vector_3i32 exactly; the Vector__3i32F4 argument matches the field type position__3i32F4. No implicit conversions or truncation beyond the intended fixed-point-to-integer scaling.
No undefined behavior — no pointer arithmetic, no null dereference (null is checked in debug builds), no type punning, no out-of-bounds access. The function only reads p_hitbox_aabb->position__3i32F4 and passes it to a pure conversion function.
Validation — appropriate for a low-level getter. The null check is guarded by #ifndef NDEBUG, consistent with the sibling function get_position_3i32F4_of__hitbox_aabb (lines 133-143) and other static inline getters in the same header. The caller is responsible for correctness in release builds.

Side Effects:
No side effects — the function reads from the pointed-to struct and returns a computed value without modifying any state.
