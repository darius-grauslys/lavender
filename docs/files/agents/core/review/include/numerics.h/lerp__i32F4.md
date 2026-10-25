# Function Review: lerp__i32F4

## 1. Header

- **Function name:** `lerp__i32F4`
- **File of origin:** `core/include/numerics.h`

## 2. Semantic

Performs linear interpolation between two fixed-point (4-bit fractional) values `one__i32F4` and `two__i32F4` using the interpolation factor `x__i32F4`, returning the interpolated fixed-point value. In real-number terms, computes `one + (two - one) * (x / 16)`, where `x` is a fixed-point fraction in the range [0, 16] representing [0.0, 1.0].

## 3. Pre-conditions

1. All three parameters (`one__i32F4`, `two__i32F4`, `x__i32F4`) are `i32F4` (typedef'd to `int32_t`), passed by value. No null-pointer constraints apply.
2. `x__i32F4` should be in the range [0, 16] for the result to lie within the [one, two] interval, but the function does not enforce this. Range validation is the caller's responsibility.
3. The intermediate product `(two__i32F4 - one__i32F4) * x__i32F4` must not overflow `int32_t`. This is consistent with the codebase's `multiply__i32F4` function, which also performs no overflow checking and documents valid input ranges via comments rather than enforcement.
4. No struct or memory initialization is involved — this is a pure arithmetic computation function, not an initialization/RAII function.

## 4. Post-conditions

1. Returns an `i32F4` value representing the fixed-point linear interpolation result: `one + ((two - one) * x) >> 4`.
2. When `x == 0` (representing 0.0), the result equals `one__i32F4`.
3. When `x == 16` (representing 1.0), the result equals `two__i32F4`.
4. No state is mutated. The function is pure.

## 5. Correctness Verdict

**Correct**

## 6. Semantic Alignment

The implementation faithfully implements the standard fixed-point linear interpolation formula. The computation proceeds as follows:

1. `two__i32F4 - one__i32F4` — fixed-point subtraction (result retains 4 fractional bits).
2. `(...) * x__i32F4` — multiplication of two `i32F4` values. Since each has 4 fractional bits, the product has 8 fractional bits. This is standard fixed-point multiplication behavior.
3. `i32F4_to__i32(...)` — arithmetic right-shift by 4 (`FRACTIONAL_PERCISION_4__BIT_SIZE`), reducing the product from 8 fractional bits back to 4 fractional bits. This correctly converts the product to the same fixed-point scale as `one` and `two`.
4. `one__i32F4 + ...` — fixed-point addition, yielding a result with 4 fractional bits, matching the `i32F4` return type.

The implementation is identical in structure to the `lerp__i32F8` variant (lines 553–555), which uses the same pattern with `i32F8_to__i32` (8-bit shift) instead. This confirms the pattern is intentional and consistent across fixed-point precisions.

The `i32F4_to__i32` conversion uses the `ARITHMETRIC_R_SHIFT` macro, which correctly handles negative numbers by negating, shifting, and re-negating. This avoids the compiler-specific behavior of right-shifting negative values directly.

## 7. Implementation Correctness

- **Type compatibility:** All types involved are `int32_t` (`i32F4`, `Signed_Index__i32`, and `int32_t` are all the same underlying type). The expression `one__i32F4 + i32F4_to__i32(...)` is `int32_t + int32_t`, and the result is returned as `i32F4` (`int32_t`). No implicit conversions, truncations, or sign mismatches occur.

- **Undefined behavior:** No undefined behavior is present. There are no pointer dereferences, no array indexing, and no null checks needed (all parameters are passed by value). The `ARITHMETRIC_R_SHIFT` macro avoids the undefined/implementation-defined behavior of right-shifting negative integers by using explicit negation.

- **Validation:** No input validation is performed, but this is appropriate for the function's role as a low-level numerics utility. The codebase's `multiply__i32F4` function (lines 587–590) follows the same convention: it performs no overflow checking and instead documents valid input ranges via comments. Overflow prevention is the caller's responsibility.

## 8. Side Effects

No side effects. The function is pure: it reads its three by-value arguments, performs arithmetic computation, and returns a computed `i32F4` value. No memory is read or written, no global state is modified, and no external functions are called (the `i32F4_to__i32` helper is also a pure inline function).
