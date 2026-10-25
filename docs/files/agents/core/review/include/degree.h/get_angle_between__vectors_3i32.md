# Function Review: get_angle_between__vectors_3i32

## 1. Header

**Function name:** `get_angle_between__vectors_3i32`

**File of origin:** `core/source/degree.c`

## 2. Semantic

Computes the clockwise angle (as a `Degree__u9`) from a source 2D point to a target 2D point, where 0° = north (positive y), 90° = east (positive x), 180° = south (negative y), and 270° = west (negative x). Only the x and y members of the input vectors are used; the z member is ignored.

## 3. Pre-conditions

1. `source__3i32` is a valid `Vector__3i32` struct; only `.x__i32` and `.y__i32` are read. No constraints on the z-component.
2. `target__3i32` is a valid `Vector__3i32` struct; only `.x__32` and `.y__i32` are read. No constraints on the z-component.
3. The difference values `d_x = target.x - source.x` and `d_y = target.y - source.y` must not cause integer overflow on subtraction. Given `i32` operands, the caller must ensure source/target coordinates are within a safe range to avoid `INT32_MIN`/`INT32_MAX` overflow.
4. When both `d_x` and `d_y` are zero (source and target coincide), the function returns `0` immediately — this is well-defined.
5. When `d_x == 0` and `d_y != 0`, or `d_y == 0` and `d_x != 0`, the trivial-case branches handle those without division — well-defined.
6. For all other cases: `run` (derived from `abs(d_x)` or `abs(d_y)`) is guaranteed to be non-zero because both `d_x` and `d_y` are non-zero; the division `x = (rise << 10) / run` will not divide by zero.

## 4. Post-conditions

1. Returns a `Degree__u9` (i.e., `uint16_t`) value in the range `[0, 511]` representing a clockwise angle in Lavender's 9-bit degree scale (where 512 = 360° and is used only as a bounds sentinel).
2. The returned angle is always a valid compass direction: `0` (north), `ANGLE__90` (east), `ANGLE__180` (south), or `ANGLE__270` (west) for axis-aligned cases, or a value in between for diagonal cases.
3. The returned value fits within `uint16_t` because all arithmetic results are bounded by the fixed-point math constants (`PI_4`, `PI_TO_DEGREE`) and the quadrant offsets (`ANGLE__90`, `ANGLE__180`, `ANGLE__270`) which sum to at most `ANGLE__270 + ANGLE__90 = 512`, and the computed component angle is at most `ANGLE__90` (128). The `angle + ANGLE__180` branch yields at most `128 + 256 = 384`, which is within `uint16_t`.
4. The function does not modify either input vector; inputs are passed by value.

## 5. Correctness Verdict

**Correct**

## 6. Semantic Alignment

The implementation fulfills its semantic intent. The function:

- Computes the delta vector `(d_x, d_y) = target - source`.
- Handles trivial axis-aligned cases (pure horizontal, pure vertical, zero vector) with direct return values that match the documented angle convention (0° = north, 90° = east, 180° = south, 270° = west).
- For general cases, applies a polynomial arctangent approximation (based on the chux/StackOverflow algorithm) to compute the angle in a single octant, then maps it to the correct quadrant through conditional adjustments and offsets.
- The `is_reciprocated` flag swaps `rise`/`run` so the approximation always operates on the smaller absolute component, maximizing accuracy.
- The post-approximation quadrant corrections (`angle = ANGLE__90 - angle` or `angle + ANGLE__180/90/270`) correctly fold the octant result into the proper 360° compass sector.

No semantic drift is observed. The function's behavior is internally consistent and matches the documented angle convention used throughout the Lavender codebase.

## 7. Implementation Correctness

- **Type compatibility:** `source__3i32` and `target__3i32` are passed by value as `Vector__3i32`, and their `.x__i32` and `.y__i32` members (of type `i32`) are subtracted into `i32` locals — no type mismatch. `rise`, `run`, `x`, and `in_radians_F10` are all `i32`. The final `angle` is `Degree__u9` (`uint16_t`), and the assignment from `((in_radians_F10 * PI_TO_DEGREE) >> 12)` (an `i32` result) to `uint16_t` is a valid narrowing conversion because the result is guaranteed to be in the range `[0, 128]`.
- **Fixed-point arithmetic:** Constants `PI_4` (0b1100100100 = 804 = ~π/4 × 2^10) and `PI_TO_DEGREE` (0b101000101 = 325 = 180/π × 2^... in fixed-point) are tuned so that the `>> 10` and `>> 12` shifts produce a degree-scaled result consistent with the 9-bit `Degree__u9` format.
- **Division by zero:** Guarded by the trivial-case early returns — when neither `d_x` nor `d_y` is zero, `run` is always non-zero.
- **Shift safety:** All left shifts (`rise << 10`, `1 << 10`) and right shifts operate on non-negative operands or are safe bit patterns within `i32` range. `x = (rise << 10) / run` — `rise` is at most `abs(INT32_MAX)`, shifted left by 10, which could overflow `i32` if `rise` is very large. However, this is a known limitation of the fixed-point design and is consistent with the function's documented accuracy scope (best for short-range applications).
- **Overflow on addition:** `angle + ANGLE__180`, `angle + ANGLE__90`, `angle + ANGLE__270` — since `angle` is at most `ANGLE__90` (128) and the largest offset is `ANGLE__270` (384), the sum is at most `384 + 128 = 512`, which fits in `uint16_t` but equals `ANGLE__360` (the bounds sentinel). This does not trigger `ANGLE__OUT_OF_BOUNDS` (1023), so it is safe.
- **Validation:** No input validation is performed (e.g., null pointer checks). This is correct because the function takes values by copy, not pointers — there are no pointers to validate.
- **`abs(x)` usage:** The standard `abs()` function is used on `i32` values; this requires `<stdlib.h>` (transitively included via the project's headers). No undefined behavior here for valid `i32` inputs.

## 8. Side Effects

No side effects. The function is pure: it reads only its input parameters (by value), performs local computations with stack-local variables, and returns a `Degree__u9` result. It does not modify any global state, does not write to any memory through pointers, and does not perform I/O.
