# is_ray__out_of_bouds

**File of origin:** `core/include/raycast/ray.h`

## Semantic
Checks whether a `Ray__3i32F20` is in an out-of-bounds state by testing if either its current vector or its angle is out of bounds.

## Pre-conditions
1. `ray` is a valid `Ray__3i32F20` struct, passed by value (no null concerns).
2. `ray.ray_current_vector__3i32F20` is a `Vector__3i32F20` that may or may not have been set to the `VECTOR__3i32F20__OUT_OF_BOUNDS` sentinel.
3. `ray.angle_of__ray` is a 10-bit bitfield of type `Degree__u9` (uint16_t) with values in range 0–1023.

## Post-conditions
1. Returns `true` if `ray.ray_current_vector__3i32F20` is out of bounds (any component matches `VECTOR__3i32F20__OUT_OF_BOUNDS`) OR if `ray.angle_of__ray >= ANGLE__OUT_OF_BOUNDS` (i.e., >= 1023).
2. Returns `false` if both the current vector and angle are within bounds.
3. The function does not modify `ray` (passed by value).

## Correctness Verdict
**Correct**

## Semantic Alignment
The implementation correctly fulfills the semantic intent of detecting an out-of-bounds ray. The function delegates to two well-defined out-of-bounds checkers:
- `is_vectors_3i32F20__out_of_bounds` checks if any component of the current vector matches the `VECTOR__3i32F20__OUT_OF_BOUNDS` sentinel (all components set to `BIT(31)`, i.e., `INT_MIN`).
- `is_degree_u9__out_of_bounds` checks if the angle is >= `ANGLE__OUT_OF_BOUNDS` (which is `MASK(10)` = 1023, the maximum value of the 10-bit bitfield).

The `get_ray__out_of_bounds()` function sets both `ray_starting_vector__3i32F20` and `ray_current_vector__3i32F20` to `VECTOR__3i32F20__OUT_OF_BOUNDS` and `angle_of__ray` to `ANGLE__OUT_OF_BOUNDS`. Since `is_ray__out_of_bouds` checks the current vector (which is set to out-of-bounds) and the angle (which is set to out-of-bounds), it correctly identifies a ray created with `get_ray__out_of_bounds()` as out of bounds.

**Note:** The function only checks `ray_current_vector__3i32F20`, not `ray_starting_vector__3i32F20`. This is a deliberate design choice: the starting vector is the origin set once during creation and does not change during ray stepping. The function checks the ray's *current* state, which is determined by the current vector and angle. A ray created with `get_ray__out_of_bounds()` will still be detected because its current vector is also set to out-of-bounds.

**Note:** The function name contains a typo: `is_ray__out_of_bouds` should be `is_ray__out_of_bounds`. This does not affect correctness but is a naming inconsistency.

## Implementation Correctness
- **Type compatibility:** `ray.ray_current_vector__3i32F20` is `Vector__3i32F20`, matching the parameter type of `is_vectors_3i32F20__out_of_bounds(const Vector__3i32F20)`. `ray.angle_of__ray` is a 10-bit bitfield of type `Degree__u9` (uint16_t), which is implicitly promoted to `int` in expressions and then converted to `Degree__u9` (uint16_t) when passed to `is_degree_u9__out_of_bounds(Degree__u9)`. No truncation occurs since the bitfield value (0–1023) fits within uint16_t.
- **Undefined behavior:** No broken pointer arithmetic, no null dereference, no type punning, no out-of-bounds access. The function receives the struct by value and accesses only valid struct members.
- **Validation:** Appropriate for the function's role. The function performs bounds checking on the ray's components using existing sentinel-based validation functions.

## Side Effects
No side effects. The function is pure: it takes a `Ray__3i32F20` by value and returns a `bool` without modifying any state.
