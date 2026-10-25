# get_y_i32_from__camera

**File of origin:** `core/include/world/camera.h`

## Semantic

Extracts the Y component of the camera's position as a plain signed 32-bit integer, converting from the camera's internal fixed-point (i32F4) representation to a whole integer value.

## Pre-conditions

1. `p_camera` must be a non-null pointer to a valid `Camera` struct.
2. The `position` field of the `Camera` struct must contain a valid `Vector__3i32F4` value. If the camera is in an "out of bounds" state (initialized via `initialize_camera_as__inactive`), the position will be `VECTOR__3i32F4__OUT_OF_BOUNDS`, and the returned value will reflect that sentinel value.

## Post-conditions

1. The function returns a `Signed_Index__i32` (i.e., `int32_t`) representing the Y coordinate of the camera's position, converted from fixed-point (i32F4, 4-bit fractional) to a plain integer via arithmetic right shift.
2. The `Camera` struct is not modified; the function has no side effects on the camera or any other state.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation correctly fulfills the semantic intent. It delegates to `get_y_i32_from__vector_3i32F4(p_camera->position)`, which in turn:

1. Extracts the `y__i32F4` field from the `Vector__3i32F4` (an `i32F4` fixed-point value).
2. Converts it to a plain `int32_t` using `i32F4_to__i32`, which performs an arithmetic right shift by `FRACTIONAL_PERCISION_4__BIT_SIZE` bits.

The function correctly accesses the `position` field of the `Camera` struct (confirmed by the struct definition in `core/include/defines.h`), which is of type `Vector__3i32F4`. The return type `Signed_Index__i32` matches the return type of `get_y_i32_from__vector_3i32F4`. The parameter type `Camera *p_camera` is appropriate for an accessor function.

## Implementation Correctness

- **Type compatibility:** The parameter `Camera *p_camera` is a pointer to the `Camera` struct, which is correct. The `position` field is of type `Vector__3i32F4`, matching the parameter type expected by `get_y_i32_from__vector_3i32F4`. The return type `Signed_Index__i32` matches the return type of the delegated function. No implicit conversions or truncation occur.
- **Undefined behavior:** No null pointer check is performed, but this is consistent with the codebase's convention — the function is `static inline` and callers are expected to ensure the pointer is valid (matching the pattern used by the sibling functions `get_x_i32_from__camera` and `get_z_i32_from__camera`). No broken pointer arithmetic, no out-of-bounds access.
- **Validation:** No validation is performed, which is appropriate for a lightweight accessor function. Validation is the caller's responsibility, consistent with the surrounding code style.

## Side Effects

No side effects. The function is a pure accessor: it reads the `position` field of the camera and returns a computed value without modifying any state.
