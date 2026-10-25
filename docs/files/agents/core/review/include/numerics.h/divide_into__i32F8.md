divide_into__i32F8 — core/include/numerics.h

Divides integer `p` by integer `q`, returning the quotient as an i32F8 fixed-point value (8 fractional bits).

Pre-conditions:
1. `q` must not be zero; division by zero is caller responsibility.
2. `p` and `q` are any valid `i32` (int32_t) values.

Post-conditions:
1. Returns `(p * 256) / q` as an `i32F8`, representing `p / q` with 8 fractional bits of precision.
2. The return value is an `i32F8` (int32_t) in fixed-point format.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly computes `p / q` in i32F8 fixed-point format. It first converts `p` to i32F8 via `i32_to__i32F8` (which left-shifts `p` by 8 bits, scaling it to fixed-point), then divides by `q`. The result `(p << 8) / q` = `(p * 256) / q` correctly represents the quotient `p / q` in i32F8 format.

The sibling function `divide_into__i32F4` has a return type of `i32F8` but converts using `i32_to__i32F4` (4-bit fractional), which is a semantic mismatch. By contrast, `divide_into__i32F8` correctly uses `i32_to__i32F8` (8-bit fractional) with a return type of `i32F8` — types and fractional precision are consistent.

Implementation Correctness:
Type compatibility — `i32_to__i32F8` returns `i32F8` (int32_t), `q` is `i32` (int32_t), and the return type is `i32F8` (int32_t). All types match exactly with no implicit conversions or truncation.
Undefined behavior — the `ARITHMETRIC_L_SHIFT` macro used in `i32_to__i32F8` casts to `u32` before shifting, avoiding the undefined behavior of left-shifting negative integers. No null dereference, no out-of-bounds access, no type punning.
No validation is needed — this is a low-level math helper. The caller is responsible for ensuring `q != 0`.

Side Effects:
No side effects — the function is pure, reading only its parameters and returning a computed value.
