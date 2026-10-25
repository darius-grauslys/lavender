# is_vector_3i32F4_within__local_space_manager

**File of origin:** `core/source/world/local_space_manager.c` (lines 960-1000)

## Semantic

Checks whether a `Vector__3i32F4` (fixed-point 3D vector with 4 fractional bits) falls within the bounds of the local space manager's active viewport. The vector is first converted to chunk-space integer coordinates, then compared against the `global_space__vector__3i32` values stored in the `p_local_space__south_west` and `p_local_space__north_east` corner `Local_Space` pointers, which represent the minimum and maximum corners of the viewport respectively.

## Pre-conditions

1. `p_local_space_manager` must be non-null and must have been initialized via `initialize_local_space_manager` or `load_local_space_manager_at__global_space_vector__3i32`.
2. `p_local_space_manager->p_local_space__north_east` must be non-null (guaranteed by initialization).
3. `p_local_space_manager->p_local_space__south_west` must be non-null (guaranteed by initialization).
4. `p_local_space_manager->p_local_space__north_east->global_space__vector__3i32` must represent the maximum (x, y, z) corner of the viewport.
5. `p_local_space_manager->p_local_space__south_west->global_space__vector__3i32` must represent the minimum (x, y, z) corner of the viewport.

## Post-conditions

1. Returns `true` if and only if the chunk-space coordinate derived from `vector_3i32F4` satisfies all of:
   - `south_west.x <= x <= north_east.x`
   - `south_west.y <= y <= north_east.y`
   - `south_west.z <= z <= north_east.z`
2. Returns `false` otherwise.
3. No state is modified; the function is pure.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation correctly fulfills the semantic intent of checking whether a fixed-point vector falls within the local space manager's viewport bounds.

- The conversion from `Vector__3i32F4` to chunk coordinates via `vector_3i32F4_to__chunk_vector_3i32` is correct. This function first converts the `i32F4` value to `i32` via arithmetic right shift (dividing by 16), then normalizes the tile-space coordinate to chunk-space via arithmetic right shift by `LOCAL_SPACE__WIDTH_AND__HEIGHT_IN__PIXELS__BIT_SHIFT` (6 bits), with appropriate negative-value adjustment.
- The bounds check correctly uses `p_local_space__north_east` as the maximum corner and `p_local_space__south_west` as the minimum corner. From the initialization in `initialize_local_space_manager`, `north_east` is assigned the highest (x, y, z) indices and `south_west` the lowest, confirming the bounds are checked in the correct direction for all three axes.
- The `&=` operator is used for combining the lower-bound check with the upper-bound check. For `bool` values (0 or 1), bitwise AND is semantically equivalent to logical AND. While it does not short-circuit, this is harmless here since there are no side effects.

## Implementation Correctness

- **Type compatibility:** `Global_Space_Vector__3i32` is a typedef for `Vector__3i32` (via `struct Vector__3i32_t`), and `Chunk_Vector__3i32` is also a typedef for the same struct. The `vector_3i32F4_to__chunk_vector_3i32` function returns `Chunk_Vector__3i32`, which is assigned to `Global_Space_Vector__3i32` — both are the same underlying type, so no conversion issues. The `.x__i32`, `.y__i32`, `.z__i32` fields are `Signed_Index__i32` (`int32_t`), and comparisons are between `int32_t` values. No implicit conversions or truncation occur.
- **Undefined behavior:** No broken pointer arithmetic, no null dereference (assuming pre-conditions hold), no type punning, no out-of-bounds access. The function only reads from the provided pointers and performs comparisons.
- **Validation:** No validation of null pointers is performed. However, this is consistent with the codebase pattern — other functions in `local_space_manager.c` (e.g., `get_p_local_space_from__local_space_manager`) also dereference these corner pointers without null checks. The pre-condition that the manager is initialized is the caller's responsibility.

## Side Effects

No side effects. The function is pure: it reads from `p_local_space_manager` and its referenced `Local_Space` objects but does not modify any state. It returns a `bool` result.
