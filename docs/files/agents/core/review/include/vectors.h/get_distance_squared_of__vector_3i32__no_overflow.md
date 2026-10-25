get_distance_squared_of__vector_3i32__no_overflow — core/include/vectors.h

## Semantic

Computes the squared distance (x² + y² + z²) of a `Vector__3i32` without overflow, writing the result to `*p_out__u64` if no overflow occurs. Returns `true` if overflow would occur at any step, `false` on success.

## Pre-conditions

1. `vector__3i32` contains three `i32` (signed 32-bit) components `x__i32`, `y__i32`, `z__i32`. These may be negative, zero, or positive (including `INT32_MIN`).
2. `p_out__u64` must be a valid, non-null pointer to a `u32` where the result will be stored.

## Post-conditions

1. If any component's square would overflow `u32`, or if the sum of squares would overflow `u32`, the function returns `true` and `*p_out__u64` is left unmodified.
2. If no overflow occurs, the function writes the squared distance `x² + y² + z²` to `*p_out__u64` as a `u32` and returns `false`.

## Correctness Verdict

**Incorrect**

## Semantic Alignment

The function's intent is to compute the squared distance of a signed 32-bit vector without overflow, returning the result as a `u32`. The implementation does **not** fulfill this semantic intent due to multiple critical bugs:

### Bug 1: Signed integer overflow in multiplication (Undefined Behavior)

The expressions `vector__3i32.x__i32 * vector__3i32.x__i32` are performed in `i32` (signed 32-bit) arithmetic. When `abs(x__i32) > 46340` (since 46341² = 2,147,488,281 > `INT32_MAX` = 2,147,483,647), the multiplication results in signed integer overflow, which is **undefined behavior** in C. The result is then implicitly converted to `u32`, but the UB has already occurred.

For example, with `x__i32 = 50000`:
- `50000 * 50000 = 2,500,000,000` exceeds `INT32_MAX`, causing UB.

### Bug 2: Incorrect overflow check for squaring

The overflow check `UINT32_MAX - vector__3i32.x__i32 < vector__3i32.x__i32` is equivalent to checking whether `2 * x` would overflow `u32`, **not** whether `x * x` would overflow. This is the wrong condition for detecting squaring overflow.

For example, with `x__i32 = 65536`:
- `x * x = 4,294,967,296` overflows `u32`, but the check `UINT32_MAX - 65536 < 65536` evaluates to `4294897759 < 65536` → false, so no overflow is detected.

### Bug 3: Incorrect handling of negative values in overflow check

When `x__i32` is negative, the implicit conversion to `u32` (due to mixing signed and unsigned in the comparison with `UINT32_MAX`) makes the negative value a very large unsigned number, causing the overflow check to incorrectly trigger for small negative values.

For example, with `x__i32 = -5`:
- `vector__3i32.x__i32` is implicitly converted to `u32` as `4294967291`
- `UINT32_MAX - 4294967291 = 4`
- `4 < 4294967291` → true, falsely reporting overflow
- But `(-5) * (-5) = 25`, which does not overflow.

### Bug 4: Misleading parameter name

The output parameter is declared as `u32 *p_out__u64` — the type is `u32*` but the name suggests `u64*`. This is a naming inconsistency that could confuse callers about the expected output width.

### Suggested Fix

The correct implementation should:
1. Take the absolute value of each `i32` component as `u32`, handling `INT32_MIN` safely (since `abs(INT32_MIN)` is UB in signed arithmetic).
2. Check if squaring would overflow `u32` using `u32` arithmetic: `if (ax > 0 && ax > UINT32_MAX / ax) return true;`
3. Perform the squaring in `u32` arithmetic.
4. Use `add_u32__no_overflow` for the additions (already done correctly).

## Implementation Correctness

- **Type compatibility**: The multiplication `vector__3i32.x__i32 * vector__3i32.x__i32` is performed in `i32` (signed) arithmetic, then assigned to `u32`. This causes signed overflow UB when the square exceeds `INT32_MAX`. The overflow check itself also mixes signed `i32` with unsigned `u32` (`UINT32_MAX`), causing implicit signed-to-unsigned conversion that produces incorrect results for negative inputs.
- **Undefined behavior**: Signed integer overflow in the multiplication expressions (lines 627-629) is UB. Additionally, `abs(INT32_MIN)` would be UB if `abs` were used (though the current code doesn't use `abs`).
- **Validation**: The function does not check if `p_out__u64` is null. This may be acceptable as caller responsibility, but is worth noting.

## Side Effects

- Writes the computed squared distance to `*p_out__u64` when no overflow occurs.
- Does not modify `vector__3i32` (passed by value).
- Does not modify any global state.
