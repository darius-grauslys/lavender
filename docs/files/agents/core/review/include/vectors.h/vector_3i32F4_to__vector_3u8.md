# Function Review: vector_3i32F4_to__vector_3u8

**File of origin:** `core/include/vectors.h`

## Semantic

Converts a 3D fixed-point vector (`Vector__3i32F4`, with 4 fractional bits per component) to a 3D unsigned byte vector (`Vector__3u8`) by right-shifting each component by `FRACTIONAL_PERCISION_4__BIT_SIZE` (4) to discard fractional bits, then implicitly truncating the result to `uint8_t`.

## Pre-conditions

1. `vector` is any valid `Vector__3i32F4`, passed by value (no pointer validity required).
2. Each component (`x__i32F4`, `y__i32F4`, `z__i32F4`) is an `i32F4` (typedef'd as `int32_t`). No explicit range constraint is enforced by the function itself; any `int32_t` value is accepted.
3. No pre-condition regarding the sign or magnitude of component values — the function does not validate that results fit within `uint8_t` range.

## Post-conditions

1. Returns a new `Vector__3u8` whose `x__u8`, `y__u8`, and `z__u8` fields are the right-shifted (by 4 bits) and implicitly truncated-to-`uint8_t` values of the corresponding input components.
2. The input parameter is not mutated (passed by value).
3. For each component, the result is `(vector.component >> 4)` implicitly converted to `uint8_t`, which truncates to the lowest 8 bits with no clamping.

## Correctness Verdict

**Incorrect**

## Semantic Alignment

The function's intent is to convert from a fixed-point representation (`i32F4` with 4 fractional bits) to an unsigned byte vector by removing the fractional bits. The implementation does perform the right shift to discard fractional bits, but it fails to properly handle two critical aspects:

1. **Implementation-defined right shift on signed values**: The function uses the plain `>>` operator on `int32_t` values. In C, right-shifting a negative signed integer is implementation-defined behavior. The codebase provides the `ARITHMETRIC_R_SHIFT` macro specifically to handle this consistently — it negates negative values before shifting and then negates the result:
   ```c
   #define ARITHMETRIC_R_SHIFT(x, n)\
       (((x)>=0) ? (x) >> (n) : -((-(x)) >> (n)))
   ```
   The related conversion function `i32F4_to__i32()` uses this macro. This function does not, making it non-portable and inconsistent with the codebase's established patterns. For negative `i32F4` values (which are common in a game engine where positions can be negative), the result of plain `>>` is implementation-defined and may produce incorrect integer components.

2. **Implicit narrowing conversion without clamping**: After right-shifting, the result is still an `int32_t`. This is implicitly converted to `Index__u8` (typedef'd as `uint8_t`) via truncation. For negative input values, this conversion wraps around in two's complement (e.g., a value of -1 after shifting becomes 255), producing semantically incorrect results. For values exceeding 255, only the lowest 8 bits are retained. No clamping or validation is performed.

The codebase has a much more robust conversion function for this purpose: `normalize_i32F4__to_tile_u8()` in `tile_vectors.h`, which uses `i32F4_to__i32()` (with `ARITHMETRIC_R_SHIFT`), handles negative value correction (`- (x < 0 && -x < BIT(FRACTIONAL_PERCISION_4__BIT_SIZE))`), and uses `ARITHMETRIC_MASK` to ensure the result fits within tile dimensions. The simpler `vector_3i32F4_to__vector_3u8` does not follow these established patterns, leading to potential data corruption for negative or out-of-range values.

## Implementation Correctness

- **Type compatibility**: `i32F4` is typedef'd as `int32_t`. The right shift produces an `int32_t`, which is then implicitly converted to `Index__u8` (typedef'd as `uint8_t`) via truncation. This is an implicit narrowing conversion that loses data for values outside the range [0, 255]. No explicit cast or clamping is used.
- **Undefined behavior**: No pointer arithmetic, no null dereference, no type punning, no out-of-bounds access. However, the right shift of negative signed integers is implementation-defined (not undefined behavior), which is still a portability concern that the codebase addresses with `ARITHMETRIC_R_SHIFT`.
- **Validation**: No validation is performed. For a function that converts to unsigned bytes, checking or clamping values to the valid range [0, 255] would be appropriate. The absence of such validation means negative values produce wrapped unsigned results rather than being handled meaningfully. This is the caller's responsibility by convention for arithmetic functions, but the implementation-defined right shift is a separate defect from pure lack of clamping.

## Side Effects

No side effects — pure function returning a new `Vector__3u8` by value.
