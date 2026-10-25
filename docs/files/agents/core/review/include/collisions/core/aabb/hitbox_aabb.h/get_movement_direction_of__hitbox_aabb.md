get_movement_direction_of__hitbox_aabb — core/source/collisions/core/aabb/hitbox_aabb.c

Derives a bitmask of cardinal movement directions (NORTH, EAST, SOUTH, WEST) from the sign of the hitbox's x and y velocity components.

Pre-conditions:
1. p_hitbox_aabb must be a non-null pointer to a valid Hitbox_AABB in debug builds. In release builds (NDEBUG defined), the null check is compiled out and the caller is responsible for pointer validity.
2. The velocity__3i32F4 field must be initialized to a valid Vector__3i32F4.

Post-conditions:
1. Returns a Direction__u8 bitmask combining applicable direction flags: DIRECTION__EAST for positive x velocity, DIRECTION__WEST for negative x velocity, DIRECTION__NORTH for positive y velocity, DIRECTION__SOUTH for negative y velocity.
2. Returns DIRECTION__NONE (0) when both x and y velocity components are zero.
3. The hitbox and all other state remain unmodified.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly maps velocity signs to direction flags. Positive x maps to EAST and negative x to WEST; positive y maps to NORTH and negative y to SOUTH. This matches the semantic intent of deriving a movement direction bitmask. The z velocity component is intentionally ignored—NORTH/EAST/SOUTH/WEST are 2D cardinal compass directions, and the z component likely represents elevation/layering handled separately. This is consistent with the function's role as a planar movement direction query.

Implementation Correctness:
Type compatibility — velocity components are i32F4 (typedef'd to int32_t), and the comparisons 0 < / 0 > are valid signed integer comparisons. Direction__u8 is uint8_t; the direction flags BIT(0)–BIT(3) yield values 1, 2, 4, 8, all within uint8_t range. The |= operation is well-defined: the uint8_t is promoted, OR'd with unsigned int constants, then narrowed back with no truncation since the maximum combined value (15) fits.
Undefined behavior — no pointer arithmetic, no null dereference (guarded in debug), no type punning, no out-of-bounds access.
Validation — the null check is guarded by #ifndef NDEBUG, consistent with the codebase convention used throughout hitbox_aabb.h and hitbox_aabb.c. The caller is responsible for passing a valid pointer in release builds.

Side Effects:
No side effects. The function is a pure query; it only reads velocity fields and returns a computed bitmask. No state is mutated.
