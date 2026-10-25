get_x_i32_from__camera — core/include/world/camera.h, lines 74-77

## Semantic
Extracts the x-coordinate of the camera's position as a signed 32-bit integer, converting from the internal fixed-point (i32F4) representation to a plain integer.

## Pre-conditions
1. `p_camera` must be a non-null pointer to a valid `Camera` struct.
2. `p_camera->position` must be a valid `Vector__3i32F4` (it is a value member, not a pointer, so it is always present once `p_camera` is valid).

## Post-conditions
1. Returns the x-component of `p_camera->position`, converted from `i32F4` (4-bit fractional fixed-point) to `Signed_Index__i32` (plain `int32_t`) via arithmetic right shift by 4 bits.
2. No state is modified; the function is non-mutating and pure.

## Correctness Verdict
Correct.

## Semantic Alignment
The implementation fulfills its semantic intent. The function correctly delegates to `get_x_i32_from__vector_3i32F4(p_camera->position)`, which in turn calls `get_x_i32F4_from__vector_3i32F4` to extract the raw `x__i32F4` field, then applies `i32F4_to__i32` to perform the fixed-point-to-integer conversion. The conversion uses `ARITHMETRIC_R_SHIFT(x, FRACTIONAL_PERCISION_4__BIT_SIZE)`, which is the correct arithmetic right shift for signed fixed-point values with 4 bits of fractional precision. The returned value represents the integer x-coordinate of the camera's position.

## Implementation Correctness
- **Type compatibility**: `p_camera->position` is of type `Vector__3i32F4`, which matches the parameter type of `get_x_i32_from__vector_3i32F4` exactly (passed by value). The return type `Signed_Index__i32` matches the return type of the delegated function. No implicit conversions or truncation occur.
- **Undefined behavior**: No pointer arithmetic, no null dereference (null-checking is the caller's responsibility per engine convention), no out-of-bounds access. The `position` field is a direct struct member, so access is always valid given a valid `p_camera`.
- **Validation**: No null check is performed on `p_camera`. This is consistent with the engine's pattern for performance-critical inline accessors (e.g., `get_position_3i32_of__camera`, `get_position_3i32F4_of__camera` all follow the same convention). Validation is the caller's responsibility.

## Side Effects
No side effects. This is a pure function that reads `p_camera->position` and returns a computed value.
