is_vector_3i32F4_inside__hitbox_aabb — core/source/collisions/core/aabb/hitbox_aabb.c, lines 541-563

## Semantic

Tests whether a 3D vector (F4 fixed-point) lies within the axis-aligned bounding box (AABB) of a `Hitbox_AABB`, returning `true` iff the vector is inside on all three axes.

## Pre-conditions

1. `p_hitbox` must be non-null. While the function itself does not check this, the delegated `get_aa_bb_as__vectors_3i32F4_from__hitbox_aabb` -> `initialize_vector_3i32F4_as__aa_bb` performs a debug-only null check (`#ifndef NDEBUG`).
2. `p_hitbox` must have a valid `position__3i32F4`, `width__quantity_u32`, `height__quantity_u32`, and `velocity__3i32F4` (standard struct validity assumed by the codebase).
3. `vector` is passed by value; no constraints beyond being a valid `Vector__3i32F4` (any bit pattern is a valid F4 value).

## Post-conditions

1. Returns `true` if and only if `vector.x >= aa.x && vector.x <= bb.x` AND `vector.y >= aa.y && vector.y <= bb.y` AND (intended) `vector.z >= aa.z && vector.z <= bb.z`, where `aa` is the south-west (minimum) corner and `bb` is the north-east (maximum) corner of the hitbox.
2. `p_hitbox` is not modified.
3. No global or local state is altered.

## Correctness Verdict

Incorrect.

## Semantic Alignment

The implementation intends to test containment within an AABB by comparing the input vector against the lower (`aa`, south-west) and upper (`bb`, north-east) corners. The x and y axes are correct:

- `vector.x >= aa.x && vector.x <= bb.x`
- `vector.y >= aa.y && vector.y <= bb.y`

However, the z-axis upper-bound check on line 561 is broken. Line 559 correctly uses `aa.z__i32F4` (lower bound), but line 561 repeats `aa.z__i32F4` instead of using `bb.z__i32F4` (upper bound):

```c
&& vector.z__i32F4
>= aa.z__i32F4
&& vector.z__i32F4
<= aa.z__i32F4    // line 561: should be bb.z__i32F4
```

This collapses the z test to `vector.z == aa.z` — an exact equality check against the lower bound, not a range check.

**Confirmation that `bb` is the upper bound:** `get_aa_bb_as__vectors_3i32F4_from__hitbox_aabb` (lines 491-503) assigns `DIRECTION__SOUTH_WEST` to `aa` and `DIRECTION__NORTH_EAST` to `bb`. The sibling function `clamp_p_vector_3i32_to__hitbox_aabb` (line 538) correctly clamps z to `bb.z`, further confirming `bb` is the max corner.

**Latent nature of the bug:** Because `initialize_vector_3i32F4_as__aa_bb_without__velocity` sets `z = position.z` identically for both SW and NE corners (lines 224-225), `aa.z == bb.z` always holds today (the AABB has no z-extent). Consequently the broken test `vector.z <= aa.z` happens to equal `vector.z <= bb.z`, and the bug produces correct results by coincidence. If the AABB ever gains z-extent, the function would only accept points at exactly the floor.

## Implementation Correctness

- **Type compatibility:** All comparisons are between `i32F4` fields; no implicit conversions or truncation.
- **Undefined behavior:** No pointer arithmetic, no null dereference (debug-guarded), no out-of-bounds access. The bug is a logical error, not UB.
- **Copy-paste bug (off-by-reference):** Line 561 should read `vector.z__i32F4 <= bb.z__i32F4`. This is the same defect found in the sibling function `is_vector_3i32_inside__hitbox_aabb` (line 585 uses `aa.z__i32` instead of `bb.z__i32`).
- **Validation:** Appropriate for the function's role. Debug-only null checks are consistent with the codebase convention (inline getters in hitbox_aabb.h follow the same `#ifndef NDEBUG` pattern).

## Side Effects

No side effects. The function is a pure query. It reads `p_hitbox` (including its velocity, since `get_aa_bb_as__vectors_3i32F4_from__hitbox_aabb` routes through `initialize_vector_3i32F4_as__aa_bb` which applies velocity to the x and y components of both corners) but does not write to it, does not mark it dirty, and does not touch any global state.

## Lavender-Specific Semantics

This function name contains "inside," not "init"/"initialize"/"reset." It does not perform Lavender-style pool cleanup or RAII-style resource acquisition. It is a read-only containment predicate, which is consistent with its role.
