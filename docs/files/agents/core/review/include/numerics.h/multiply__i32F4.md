## multiply__i32F4 — core/include/numerics.h

### Semantic

Multiplies two fixed-point 4-bit fractional (i32F4) values and returns the product in i32F4 format. The multiplication is performed in raw integer space (where each i32F4 value is scaled by 2^4), and the result is right-shifted by 4 bits to restore the correct i32F4 scale.

### Pre-conditions

1. `x` is a valid `i32F4` value (an `int32_t` representing a fixed-point number with 4 fractional bits).
2. `y` is a valid `i32F4` value (an `int32_t` representing a fixed-point number with 4 fractional bits).
3. Per the function's documentation comment, `x` and `y` must each be in the range `0` to `BIT(12).F4` (i.e., real value 0 to 4096, or raw i32F4 value 0 to 65536) to avoid signed integer overflow in the `x * y` multiplication. This is a caller responsibility, not enforced at runtime.

### Post-conditions

1. Returns an `i32F4` value representing the fixed-point product of `x` and `y`. The result is `(x * y) >> 4`, which correctly scales the product back to i32F4 precision (2^4).
2. The return type is `i32F4` (i.e., `int32_t`), matching the function signature.
3. No input parameters are modified; the function is pure.

### Correctness Verdict

Correct

### Semantic Alignment

The implementation correctly performs fixed-point multiplication for i32F4 format. In i32F4 representation, each value is scaled by 2^4 (i.e., the real value is `raw_value / 16`). When two such values are multiplied, the raw product is scaled by 2^8 (since 2^4 × 2^4 = 2^8). The function then applies `i32F4_to__i32`, which right-shifts the product by 4 bits (using `ARITHMETRIC_R_SHIFT` to handle negative values correctly), reducing the scale back to 2^4 and producing a correctly-scaled i32F4 result. This is the standard and correct algorithm for fixed-point multiplication.

The comment "Can only multiply values 0 <-> BIT(12).F4" documents the valid input range to prevent signed integer overflow. If both inputs are at most `BIT(12).F4` (raw value 65536 = 2^16), the raw product `x * y` can reach 2^32, which exceeds `INT32_MAX`. However, this overflow condition is a documented caller responsibility, not a bug in the function itself. The function faithfully implements the documented contract.

### Implementation Correctness

- **Type compatibility**: `x` and `y` are `i32F4` (typedef for `int32_t`). The expression `x * y` is performed in `int32_t` arithmetic. The result is passed to `i32F4_to__i32`, which accepts `i32F4` (i.e., `int32_t`) and returns `Signed_Index__i32` (also `int32_t`). The return type is `i32F4` (i.e., `int32_t`). All types are compatible with no implicit conversions or truncation.
- **Undefined behavior**: No undefined behavior occurs when inputs respect the documented range. The `ARITHMETRIC_R_SHIFT` macro correctly handles right-shifting of negative values (avoiding the implementation-defined behavior of right-shifting negative signed integers in C). If inputs exceed the documented range, signed integer overflow in `x * y` would be undefined behavior, but this is the caller's responsibility per the documentation.
- **Validation**: No runtime validation is performed. This is appropriate for a low-level `static inline` numeric utility — the documented constraint serves as the contract, and enforcing it at runtime would add unnecessary overhead for a performance-sensitive fixed-point math routine.

### Side Effects

No side effects. The function is pure: it reads its two parameters and returns a computed `i32F4` value without modifying any state, memory, or I/O.
