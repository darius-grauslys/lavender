# Function Review: set_x_position_to__hitbox_aabb

## 1. Header

- **Function name:** `set_x_position_to__hitbox_aabb`
- **File of origin:** `core/include/collisions/core/aabb/hitbox_aabb.h`

## 2. Semantic

Sets the x-component of a `Hitbox_AABB`'s 3D position to the given fixed-point value and marks the hitbox as dirty (requiring recomputation of derived state).

## 3. Pre-conditions

1. `p_hitbox_aabb` must be a non-null pointer to a valid `Hitbox_AABB` struct. This is checked in debug builds only (`#ifndef NDEBUG`); in release builds the null check is omitted per codebase convention.
2. `x__position` may be any valid `i32F4` value (no range constraint; it is a raw fixed-point integer with 4 fractional bits).

## 4. Post-conditions

1. `p_hitbox_aabb->hitbox_aabb_flags__u8` has its dirty bit set via `set_hitbox_aabb_as__dirty` (returns the resulting dirty state).
2. `p_hitbox_aabb->position__3i32F4.x__i32F4` equals the provided `x__position`.
3. The y and z components of `position__3i32F4`, as well as the velocity, acceleration, dimensions, and other fields, are left unchanged.

## 5. Correctness Verdict

Correct

## 6. Semantic Alignment

The implementation fulfills its semantic intent. It follows the same two-step pattern used throughout the file: mark dirty first, then mutate the position field. The sibling functions `set_y_position_to__hitbox_aabb` (lines 300–311) and `set_z_position_to__hitbox_aabb` (lines 315–326) use the identical pattern for their respective components. The canonical `set_hitbox_aabb__position_with__3i32F4` (hitbox_aabb.c:77) also calls `set_hitbox_aabb_as__dirty` before writing to `position__3i32F4`. No semantic drift is observed.

**Note:** The function is annotated with `/// TODO: REMOVE, must use dispatch_game_action__hitbox instead`, indicating it is deprecated in favor of a dispatch/game-action mechanism. This does not affect correctness of the implementation itself.

## 7. Implementation Correctness

- **Type compatibility:** The parameter `x__position` is `i32F4`, and the target field `p_hitbox_aabb->position__3i32F4.x__i32F4` is also `i32F4` (confirmed from `Vector__3i32F4_t` in `defines_weak.h:77`). Exact type match — no implicit conversion or truncation.
- **Undefined behavior:** No broken pointer arithmetic, no null dereference (debug-mode null check guards the dereferences), no type punning, no out-of-bounds access.
- **Validation:** Null validation is present in debug builds (`#ifndef NDEBUG`), consistent with the codebase-wide convention. This is appropriate for the function's role as a low-level mutator; additional validation is the caller's responsibility per the established pattern.

## 8. Side Effects

- Mutates `p_hitbox_aabb->hitbox_aabb_flags__u8` by setting the dirty flag (via `set_hitbox_aabb_as__dirty`).
- Mutates `p_hitbox_aabb->position__3i32F4.x__i32F4` to the provided `x__position`.
- No other memory locations or global state are affected.
- No output/side-effect-only callers are traced in this review.
