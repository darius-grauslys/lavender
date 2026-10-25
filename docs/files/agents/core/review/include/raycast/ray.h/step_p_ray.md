# Function Review: step_p_ray

## 1. Header
- **Function name**: `step_p_ray`
- **File of origin**: `core/source/raycast/ray.c`

## 2. Semantic
Advances a ray's current position by one step along its direction vector, constrained to the ray's configured 2D plane (XY, XZ, or YZ). The direction is looked up from a precomputed trigonometric lookup table indexed by the ray's angle.

## 3. Pre-conditions
1. `p_ray` must be non-null (the function dereferences it without null-checking; consistent with codebase convention where validation is the caller's responsibility).
2. `p_ray->angle_of__ray` must be a valid index into `__DEGREE_TO_2i32F10__LOOKUP_TABLE` (0–511, since the table has 512 entries and `ANGLE__360` is 512). Values ≥ 512 would cause an out-of-bounds array access. The `angle_of__ray` field is a 10-bit bitfield (`Degree__u9 : 10`), so it can hold 0–1023, meaning the caller is responsible for ensuring the angle is within the valid range.
3. `p_ray->ray_plane_mode` should be a valid `Ray_Plane_Mode` value (`Ray_Plane_Mode__XY`, `Ray_Plane_Mode__XZ`, or `Ray_Plane_Mode__YZ`). Any unrecognized value falls through to the `default`/`XY` case, which is safe.

## 4. Post-conditions
1. `p_ray->ray_current_vector__3i32F20` has been mutated: the direction offset for the ray's angle (remapped to the ray's plane mode) has been added to it via `add_p_vectors__3i32F20`.
2. `p_ray->ray_starting_vector__3i32F20` is unchanged.
3. `p_ray->angle_of__ray` and `p_ray->ray_plane_mode` are unchanged.

## 5. Correctness Verdict
**Correct**

## 6. Semantic Alignment
The implementation fulfills the semantic intent. The function:

1. **Looks up the 2D direction vector** for the ray's angle from `__DEGREE_TO_2i32F10__LOOKUP_TABLE`. The table stores 512 unit direction vectors in the XY plane (z = 0), where each entry is a `Vector__3i32F20` with the 2D direction stored in the x and y components.

2. **Remaps the 2D direction to the appropriate 3D plane** based on `ray_plane_mode`:
   - **Ray_Plane_Mode__XY** (default): The offset is used as-is: `(x, y, 0)`. This is correct since the lookup table already stores 2D vectors in the XY plane.
   - **Ray_Plane_Mode__XZ**: The y component is moved to z, and y is zeroed: `(x, 0, y)`. This correctly maps the 2D direction `(x, y)` from the lookup table to the XZ plane as `(x, 0, y)`.
   - **Ray_Plane_Mode__YZ**: The x component is moved to z, and x is zeroed: `(0, y, x)`. This correctly maps the 2D direction `(x, y)` from the lookup table to the YZ plane as `(0, y, x)`.

3. **Adds the offset** to the ray's current position via `add_p_vectors__3i32F20`, which performs component-wise addition on `p_ray->ray_current_vector__3i32F20`.

The plane remapping logic is consistent with the `__step_p_ray_until` helper function, which selects the same two components for each plane mode (XY: x,y; XZ: x,z; YZ: y,z).

This is **not** a Lavender-style initialization function (it does not reset/clean up a struct). It is a stateful mutation function that advances the ray's position.

## 7. Implementation Correctness
- **Type compatibility**: All types are compatible. `angle_of__ray` (10-bit bitfield of `Degree__u9`/`uint16_t`) is used as an array index, which is valid in C (the bitfield value is promoted to `int` for indexing). The lookup table returns `Vector__3i32F20`, which matches the local variable `offset__2i32F20`. The `add_p_vectors__3i32F20` function takes `Vector__3i32F20 *` pointers, and both `&p_ray->ray_current_vector__3i32F20` and `&offset__2i32F20` are of the correct type.
- **Undefined behavior**: No null dereference risk beyond the missing null check (which is consistent with the codebase pattern). No broken pointer arithmetic or type punning. The `default` case in the switch safely handles `Ray_Plane_Mode__XY` and any unknown values.
- **Validation**: No validation of `p_ray` for null, consistent with the codebase convention. No validation of `angle_of__ray` range — this is the caller's responsibility (pre-condition #2).
- **Declaration mismatch**: The `extern` declaration in `ray.c` line 8 declares the lookup table as `[255]`, but the actual definition in `degree.c` line 8 defines it as `[512]`. This is a declaration mismatch that could cause confusion and may trigger warnings on some compilers, but does not cause a runtime bug since the definition's size is used by the linker. This is a code quality issue worth noting.

## 8. Side Effects
- **Mutates** `p_ray->ray_current_vector__3i32F20` by adding the direction offset (looked up from the angle-based table and remapped to the ray's plane) to it.
- Does not modify `p_ray->ray_starting_vector__3i32F20`, `p_ray->angle_of__ray`, or `p_ray->ray_plane_mode`.
- Does not allocate, deallocate, or access any external resources.
- The local variable `offset__2i32F20` is a stack copy of the lookup table entry; modifications to it (for plane remapping) do not affect the lookup table.
