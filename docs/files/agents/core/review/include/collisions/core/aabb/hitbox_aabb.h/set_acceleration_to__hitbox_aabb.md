## 1. Header

- **Function name**: `set_acceleration_to__hitbox_aabb`
- **File of origin**: `core/include/collisions/core/aabb/hitbox_aabb.h` (lines 473-487)

## 2. Semantic

Sets the full 3-component acceleration vector on a `Hitbox_AABB` by delegating each axis to its respective single-axis setter, and marks the hitbox as dirty so recomputation occurs.

## 3. Pre-conditions

1. `p_hitbox_aabb` must be non-null. A null-pointer guard is present under `#ifndef NDEBUG` (debug builds); release builds assume the caller enforces this and rely on the callee guards.
2. `acceleration` is passed by value (`Vector__3i16F8`); no caller-side constraint beyond being a correctly-typed value.

## 4. Post-conditions

1. The hitbox is marked dirty via `set_hitbox_aabb_as__dirty`.
2. The `acceleration__3i16F8` field of the hitbox is fully set:
   - `x` component assigned to `p_hitbox_aabb->acceleration__3i16F8.x__i16F8`
   - `y` component assigned to `p_hitbox_aabb->acceleration__3i16F8.y__i16F8`
   - `z` component assigned to `p_hitbox_aabb->acceleration__3i16F8.z__i16F8`
3. The function returns `void`.

## 5. Correctness Verdict

Correct

(The function itself behaves correctly — all three axes are set, the dirty flag is raised, and null checks are present. However, see the naming inconsistency flagged below.)

## 6. Semantic Alignment

The implementation fulfills its semantic intent: it sets all three components of the acceleration vector and marks the hitbox dirty, exactly as the parallel `set_velocity_to__hitbox_aabb` does for velocity.

**Naming inconsistency (bug):** The z-axis acceleration setter is named `set_z_acceleration_to__hitbox` (line 444) — it is missing the `_aabb` suffix that its x and y siblings follow:

| Axis | Setter name | Has `_aabb`? |
|------|-------------|--------------|
| x    | `set_x_acceleration_to__hitbox_aabb` (line 416) | yes |
| y    | `set_y_acceleration_to__hitbox_aabb` (line 430) | yes |
| z    | `set_z_acceleration_to__hitbox` (line 444) | **no** |

The call on line 486 (`set_z_acceleration_to__hitbox`) compiles because it matches the (inconsistently-named) definition. The function works, but the inconsistency is a latent hazard: a developer renaming the z setter to follow convention would also have to update this call site, which is easily missed. For comparison, the parallel velocity function `set_velocity_to__hitbox_aabb` (lines 457-471) calls `set_z_velocity_to__hitbox_aabb` (line 470) — consistent naming throughout. The z acceleration setter should be renamed to `set_z_acceleration_to__hitbox_aabb` to match the codebase convention.

## 7. Implementation Correctness

- **Type compatibility**: All argument types match. `acceleration.x__i16F8`, `.y__i16F8`, and `.z__i16F8` are all `i16F8`, and each is passed to a setter expecting `i16F8`. The `Vector__3i16F8` parameter matches the `acceleration__3i16F8` field type returned by `get_acceleration_3i16F8_of__hitbox_aabb` (line 180). No implicit conversions or truncation.
- **Undefined behavior**: No broken pointer arithmetic, type punning, or out-of-bounds access. The `p_hitbox_aabb` pointer dereference is guarded by the same null-check pattern used throughout the file.
- **Validation**: The null-pointer guard under `#ifndef NDEBUG` is consistent with the rest of the file and is appropriate for the function's role.

## 8. Side Effects

1. Mutates `p_hitbox_aabb`: sets the `acceleration__3i16F8` field (all three components) and marks the hitbox as dirty by modifying its internal dirty-flag state via `set_hitbox_aabb_as__dirty`.
2. No other observable side effects; no memory allocation, no I/O, no global state changes.

## Root Cause / Fix Recommendation

Rename `set_z_acceleration_to__hitbox` (definition, line 444) and its call site (line 486) to `set_z_acceleration_to__hitbox_aabb` so it matches the x/y acceleration setters and the velocity setter naming convention. Note the debug error strings (lines 421, 435, 449) consistently use the shortened `set_z_acceleration_to__hitbox` form — that is pre-existing and out of scope for this review, but the function name itself should be brought in line with the rest of the file.
