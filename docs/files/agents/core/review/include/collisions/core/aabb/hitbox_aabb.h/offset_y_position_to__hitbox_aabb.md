offset_y_position_to__hitbox_aabb — core/include/collisions/core/aabb/hitbox_aabb.h, lines 344-356

## Semantic

Offsets the Y component of a `Hitbox_AABB`'s position by a given `i32F4` delta and marks the hitbox as dirty.

## Pre-conditions

1. `p_hitbox_aabb` must be non-null (enforced via debug build runtime check only).
2. `p_hitbox_aabb` must point to a valid, initialized `Hitbox_AABB` instance.
3. `y__position` is an `i32F4` signed fixed-point value (4-bit fractional precision) representing the delta to add; there is no explicit range constraint documented.

## Post-conditions

1. If `p_hitbox_aabb` is null in a debug build, the function returns early with no effect.
2. The hitbox is marked dirty via `set_hitbox_aabb_as__dirty` (sets `hitbox_aabb_flags__u8` dirty bit).
3. `p_hitbox_aabb->position__3i32F4.y__i32F4` has had `y__position` added to it (modulo `int32_t` overflow semantics).
4. No value is returned.

## Correctness Verdict

Correct

## Semantic Alignment

The function performs exactly what its name and the surrounding family of offset/set functions imply: it offsets the Y position, unlike the sibling `set_y_position_to` which assigns. The `+=` operation matches the semantic intent of an "offset" (as opposed to the `=` used in `set_*_position_to`). It is consistent with the sibling `offset_x_position_to` and `offset_z_position_to` functions.

## Implementation Correctness

- **Type compatibility:** The parameter `y__position` is `i32F4` (a typedef for `int32_t`), and `position__3i32F4.y__i32F4` is also `i32F4`. Types match exactly with no implicit conversion or truncation.
- **Undefined behavior:** No out-of-bounds access; the single member access is within the `Vector__3i32F4` struct. Pointer is checked for null in debug builds before dereference. In release builds (`NDEBUG` defined), the null check is omitted — the function silently produces undefined behavior if a null pointer is passed. This is a pre-existing convention consistent with all sibling functions in this file.
- **Validation:** Null-pointer validation is appropriate and consistent with the other `offset_*_position_to` and `set_*_position_to` functions in this file (all use the same `#ifndef NDEBUG` guard pattern).
- All three axes (x, y, z) follow an identical, consistent pattern; no anomalies specific to the Y variant.

## Side Effects

- Mutates `p_hitbox_aabb->hitbox_aabb_flags__u8` (marks the dirty flag).
- Mutates `p_hitbox_aabb->position__3i32F4.y__i32F4`.

## Notes

This function carries the same `/// TODO: REMOVE, must use dispatch_game_action__hitbox instead` marker as its x, z, and set_* siblings, indicating the direct-mutation API is slated for deprecation in favor of the game-action dispatch path. Reviewers should be aware these are temporary helpers.