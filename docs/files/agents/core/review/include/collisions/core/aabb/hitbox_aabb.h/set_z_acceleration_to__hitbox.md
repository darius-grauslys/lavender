set_z_acceleration_to__hitbox — core/include/collisions/core/aabb/hitbox_aabb.h, lines 443-455

## 2. Semantic

Sets the Z-component of the acceleration field on a `Hitbox_AABB` struct to a new fixed-point 8-bit fractional value, and marks the hitbox as dirty so downstream systems re-evaluate it.

## 3. Pre-conditions

1. `p_hitbox_aabb` must be non-null. This is validated in debug builds (when `NDEBUG` is not defined) via a null check that logs an error and returns early. In release builds the check is elided, placing the onus on the caller.
2. `p_hitbox_aabb` must point to a valid, initialized `Hitbox_AABB` struct.
3. `z__acceleration` must be a valid `i16F8` value (a 16-bit signed integer used as a fixed-point type with 8 fractional bits, per the typedef in `core/include/defines_weak.h`).

## 4. Post-conditions

1. The dirty flag on `p_hitbox_aabb` is set to true via `set_hitbox_aabb_as__dirty`, which sets the dirty bit in `hitbox_aabb_flags__u8`.
2. `p_hitbox_aabb->acceleration__3i16F8` `.z__i16F8` field is assigned the value of `z__acceleration`.
3. If the function returns early (null pointer in debug), no state is modified.

## 5. Correctness Verdict

Correct

## 6. Semantic Alignment

The implementation fulfills the semantic intent. The function is a mutator setter that assigns the Z component of the acceleration vector. The struct field `acceleration__3i16F8` is of type `Vector__3i16F8`, which contains `x__i16F8`, `y__i16F8`, and `z__i16F8` members (per `core/include/defines_weak.h`). The function correctly targets the `.z__i16F8` member.

Notably, the function name is `set_z_acceleration_to__hitbox` (without the `_aabb` suffix), whereas its sibling functions `set_x_acceleration_to__hitbox_aabb` and `set_y_acceleration_to__hitbox_aabb` include the `_aabb` suffix. This is a naming inconsistency with the sibling setters, though the callers (e.g., `set_acceleration_to__hitbox_aabb` at line 486) use the correct name, so there is no functional impact.

## 7. Implementation Correctness

- **Type compatibility**: Parameter `z__acceleration` is of type `i16F8` (typedef for `int16_t`), and the target field `p_hitbox_aabb->acceleration__3i16F8.z__i16F8` is also of type `i16F8`. Exact match; no implicit conversion or truncation. ✓
- **Undefined behavior**: The null-pointer check (debug-only) prevents null dereference before the struct access. No pointer arithmetic, no type punning, no out-of-bounds access on the struct field. ✓
- **Validation**: The null check is guarded by `#ifndef NDEBUG`, consistent with the codebase convention for debug-only validation. This is appropriate for a lightweight `static inline` setter in a performance-sensitive engine. ✓

## 8. Side Effects

1. Calls `set_hitbox_aabb_as__dirty(p_hitbox_aabb)`, which sets the dirty bit in `p_hitbox_aabb->hitbox_aabb_flags__u8`. This marks the hitbox as needing re-evaluation by collision/pipeline systems.
2. Mutates `p_hitbox_aabb->acceleration__3i16F8.z__i16F8` by overwriting it with the provided `z__acceleration` value.

Note: This is not an initialization (Lavender-style cleanup/reset) function. It is a straightforward setter mutator.
