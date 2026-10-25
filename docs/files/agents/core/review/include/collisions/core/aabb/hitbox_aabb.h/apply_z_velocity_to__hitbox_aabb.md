apply_z_velocity_to__hitbox_aabb — core/include/collisions/core/aabb/hitbox_aabb.h

### 2. Semantic

Adds the supplied z-axis velocity delta to the hitbox's velocity vector, accumulating it into the existing z component.

### 3. Pre-conditions

1. `p_hitbox_aabb` must be non-null. A debug-only null check (`!p_hitbox_aabb`) calls `debug_error` and returns early; in release builds (`NDEBUG` defined) passing null is undefined behavior since the pointer is dereferenced unconditionally.
2. `z__velocity` is an `i32F4` (alias of `int32_t`), representing a 4-bit-fraction fixed-point value. No range constraint is imposed by the function; overflow of the `int32_t` addition is left to the caller.

### 4. Post-conditions

1. Returns `void`.
2. `p_hitbox_aabb->velocity__3i32F4.z__i32F4` is increased by `z__velocity`. All other fields of `velocity__3i32F4` (x, y) and all other members of `p_hitbox_aabb` are left unchanged.

### 5. Correctness Verdict

Correct

### 6. Semantic Alignment

The implementation directly adds `z__velocity` to `p_hitbox_aabb->velocity__3i32F4.z__i32F4`, which is exactly the semantic intent: applying (accumulating) a z-axis velocity delta onto the hitbox's velocity. This is consistent with the sibling functions `apply_x_velocity_to__hitbox_aabb` (line 233) and `apply_y_velocity_to__hitbox_aabb` (line 246), which perform the analogous accumulation on their respective components. No semantic drift.

### 7. Implementation Correctness

- **Type compatibility:** `z__velocity` is declared `i32F4` (`int32_t`) and `z__i32F4` is a member of type `i32F4` (`int32_t`). The `+=` operates on exact-matching types, so there is no implicit conversion or truncation.
- **Undefined behavior:** None. The only dereference is `p_hitbox_aabb->velocity__3i32F4.z__i32F4`, which is a plain struct member access on a valid pointer (guaranteed by the debug null check; release builds rely on caller compliance, which is the established contract for these static-inline header functions). There is no pointer arithmetic, no out-of-bounds access, and no type punning.
- **Validation:** The null check is debug-only (`#ifndef NDEBUG`), which is consistent with the pattern used by all sibling `apply_*_velocity_to__hitbox_aabb` functions in this file. Validation is appropriate for the function's role as an inlinable hot-path mutator; the responsibility for passing a valid pointer rests with the caller, matching the rest of the codebase.

### 8. Side Effects

Mutates `p_hitbox_aabb->velocity__3i32F4.z__i32F4` in place (adds `z__velocity`). No other state is read or written. No side effects beyond the documented mutation.
