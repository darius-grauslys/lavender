# Function Review: get_angle_from__direction

## 1. Header

- **Function name:** `get_angle_from__direction`
- **File of origin:** `core/source/degree.c`

## 2. Semantic

Maps a 2D compass `Direction__u8` bitmask to its corresponding `Degree__u9` angle in the engine's 512-unit-per-revolution system, returning `ANGLE__OUT_OF_BOUNDS` for any direction that cannot be represented as a single 2D angle (e.g., `DIRECTION__NONE`, `DIRECTION__UPWARDS`, and any 3D composite direction).

## 3. Pre-conditions

1. `direction` is a value of type `Direction__u8` (`uint8_t`); it need not be one of the named direction macros, though only the eight recognized cardinal/diagonal directions yield a valid angle.
2. Any direction value **not** in the set {NORTH, EAST, SOUTH, WEST, NORTH_EAST, NORTH_WEST, SOUTH_EAST, SOUTH_WEST} — including `DIRECTION__NONE` (0), `DIRECTION__UPWARDS` (16), `DIRECTION__DOWNWARDS` (32), and all 3D composites — is accepted but will produce `ANGLE__OUT_OF_BOUNDS`.
3. The caller assumes responsibility for testing the return value with `is_degree_u9__out_of_bounds` before using it as an index into `__DEGREE_TO_2i32F10__LOOKUP_TABLE` (which is only 512 entries, indices 0–511); the out-of-bounds sentinel (1023) is not a valid table index.

## 4. Post-conditions

- Returns `ANGLE__0` (0) when `direction == DIRECTION__NORTH`.
- Returns `ANGLE__90` (128) when `direction == DIRECTION__EAST`.
- Returns `ANGLE__180` (256) when `direction == DIRECTION__SOUTH`.
- Returns `ANGLE__270` (384) when `direction == DIRECTION__WEST`.
- Returns `ANGLE__45` (64) when `direction == DIRECTION__NORTH_EAST`.
- Returns `ANGLE__270 + ANGLE__45` (448) when `direction == DIRECTION__NORTH_WEST`.
- Returns `ANGLE__90 + ANGLE__45` (192) when `direction == DIRECTION__SOUTH_EAST`.
- Returns `ANGLE__180 + ANGLE__45` (320) when `direction == DIRECTION__SOUTH_WEST`.
- Returns `ANGLE__OUT_OF_BOUNDS` (1023) for **any** other `direction` value (default case).
- Every non-sentinel return is a multiple of 32 (the engine's base angle unit) and lies within the valid 9-bit range 0–511; the sentinel is 1023, which `is_degree_u9__out_of_bounds` recognizes as out of bounds.

## 5. Correctness Verdict

Correct

## 6. Semantic Alignment

The implementation fulfills its semantic intent. The function is a direct switch/case lookup table with no arithmetic that could drift from the intended compass convention. The angle-to-direction mapping follows the engine's clockwise convention:

| Direction            | Bitmask | Returned angle | Degrees (512 = 360°) |
|----------------------|---------|----------------|-----------------------|
| NORTH                | 1       | 0              | 0°                    |
| NORTH_EAST           | 3       | 64             | 45°                   |
| EAST                 | 2       | 128            | 90°                   |
| SOUTH_EAST           | 6       | 192            | 135°                  |
| SOUTH                | 4       | 256            | 180°                  |
| SOUTH_WEST           | 12      | 320            | 225°                  |
| WEST                 | 8       | 384            | 270°                  |
| NORTH_WEST           | 9       | 448            | 315°                  |

All eight values are exactly the named `ANGLE__` constants (or sums thereof), confirming the mapping is intentional and matches the engine's 512-unit circle. Round-trip consistency was verified against the inverse function `get_direction_from__angle` (`degree.c`, lines 523–546): applying forward-then-reverse restores each of the eight recognized directions exactly. The `default` case returning `ANGLE__OUT_OF_BOUNDS` for non-representable 2D directions is semantically correct — there is no single 2D angle for directions that include a vertical component.

## 7. Implementation Correctness

- **Type compatibility:** No issues. The parameter `Direction__u8` (`uint8_t`) is compared against `BIT(n)` constants (type `int`); `uint8_t` is integer-promoted to `int` for the comparison, which is well-defined. All return expressions are `int` values that fit within `Degree__u9` (`uint16_t`): the largest non-sentinel is 448, and the sentinel is 1023 — both far below 65536. No implicit truncation occurs.
- **Undefined behavior:** None. The function performs no pointer dereference, no array indexing, no type punning, and no floating-point operations. The `switch` is exhaustive via the `default` case: every possible `uint8_t` value takes a path that executes a `return`, so control never reaches the end of the function body. The two additions in the diagonal cases (`ANGLE__270 + ANGLE__45` = 448, `ANGLE__90 + ANGLE__45` = 192, `ANGLE__180 + ANGLE__45` = 320) are compile-time constant `int` computations with no overflow.
- **Validation:** Appropriate for the function's role. The parameter is a value type (not a pointer), so there is nothing to null-check. Unrecognized direction values are handled gracefully by the `default` case rather than being silently misclassified. It is the caller's responsibility to check the return with `is_degree_u9__out_of_bounds` before indexing the 512-entry lookup table; the function itself does not and should not perform this check.

## 8. Side Effects

No side effects. The function is pure: it reads only its by-value parameter and returns a value. It does not modify any variable, global or static state, perform I/O, or alter the argument passed to it.
