# Function Review: `is_vector_3i32_inside__hitbox_aabb`

## 1. Header
- **Function name**: `is_vector_3i32_inside__hitbox_aabb`
- **File of origin**: `core/source/collisions/core/aabb/hitbox_aabb.c`

## 2. Semantic
Determines whether a given 3D integer vector lies inside (or on the boundary of) an axis-aligned bounding box (AABB) hitbox. Returns `true` if the vector is within the box on all three axes, `false` otherwise.

## 3. Pre-conditions
1. `p_hitbox` must not be `NULL` — it is dereferenced by `get_aa_bb_as__vectors_3i32_from__hitbox_aabb`.
2. `vector` is passed by value; no pre-conditions on its contents.
3. The `Hitbox_AABB` struct pointed to by `p_hitbox` must be in a valid, initialized state (the helper function `get_aa_bb_as__vectors_3i32_from__hitbox_aabb` computes corner vectors from the hitbox data, so corrupted data would produce incorrect `aa`/`bb` values).

## 4. Post-conditions
- Returns `true` if `vector.x__i32`, `vector.y__i32`, and `vector.z__i32` all fall within the inclusive range `[aa, bb]` on their respective axes (where `aa` is the south-west corner and `bb` is the north-east corner obtained from the hitbox).
- Returns `false` otherwise.
- No state is mutated; the function is pure aside from reading the input hitbox.

## 5. Correctness Verdict
**Incorrect**

## 6. Semantic Alignment
The implementation **does not** fulfill its semantic intent. On the z-axis upper-bound check (line 585), the code compares `vector.z__i32` against `aa.z__i32` instead of `bb.z__i32`:

```c
&& vector.z__i32 >= aa.z__i32
&& vector.z__i32 <= aa.z__i32   // BUG: should be bb.z__i32
```

This effectively constrains `vector.z__i32` to equal `aa.z__i32` (i.e., `z >= aa.z && z <= aa.z` ⟹ `z == aa.z`), rather than checking that `z` falls within `[aa.z, bb.z]`. This is inconsistent with how the x and y axes are correctly tested (against `aa` for the lower bound and `bb` for the upper bound). The function will incorrectly return `false` for any vector whose z-coordinate differs from the south-west corner's z-coordinate, and will incorrectly return `true` for a vector that is actually outside the box on the z-axis but happens to share the same z as the lower corner.

## 7. Implementation Correctness
- **Type compatibility**: All comparisons use `i32` fields consistently; no type mismatch or truncation issues.
- **Undefined behavior**: No null dereference or out-of-bounds access in the function body itself (the only concern is the caller-provided `p_hitbox` being non-null, which is a pre-condition, not undefined behavior within the function).
- **Validation**: No validation is performed inside the function. This is appropriate for a low-level collision utility — null-checking and data validation should be the caller's responsibility in the Lavender engine pattern.
- **Bug**: Off-by-field error on line 585: `aa.z__i32` should be `bb.z__i32`.

## 8. Side Effects
No side effects. The function reads from `p_hitbox` via the helper and uses stack-local `Vector__3i32` variables `aa` and `bb`. No memory is written beyond the stack.
