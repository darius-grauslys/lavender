normalize_i32F4__to_tile_u8 — core/include/world/tile_vectors.h

Converts a 4-bit-fractional fixed-point coordinate (i32F4) to a local tile index within a chunk (0–7), using floor division semantics. The tile size is 8 (TILE__WIDTH_AND__HEIGHT__BIT_SHIFT = 3) and the chunk size is 8 tiles (CHUNK__WIDTH_AND__HEIGHT__BIT_SHIFT = 3), so the correct computation is floor(x / (8 * 16)) mod 8 = floor(x / 128) mod 8, where x is the i32F4 value.

Pre-conditions:
1. x is any valid i32F4 (int32_t) value; no range constraint.

Post-conditions:
1. Returns an Index__u8 (uint8_t) in the range 0–7 representing the local tile index within a chunk.
2. The returned index should equal floor(x / 128) mod 8, where x is interpreted as a fixed-point value with 4 fractional bits.

Correctness Verdict: Incorrect

Semantic Alignment:
The function's intent is to convert a fixed-point coordinate to a local tile index using floor semantics. The implementation has two bugs that cause incorrect results for certain inputs.

**Bug 1 — Incomplete floor correction for fixed-point-to-integer conversion:**
The function calls `i32F4_to__i32(x)`, which uses `ARITHMETRIC_R_SHIFT(x, 4)` to convert the fixed-point value to an integer. This macro performs truncation toward zero (for negative x, it computes `-(((-x)) >> 4)`, which is truncation toward zero, not floor). The correction term `(x < 0 && -x < BIT(FRACTIONAL_PERCISION_4__BIT_SIZE))` subtracts 1 to convert truncation toward zero to floor, but only when x is in the range (-16, 0) — i.e., only for fixed-point values in (-1.0, 0.0). For any other negative fixed-point value with a non-zero fractional part (e.g., -1.5 = -24, -8.5 = -136), the truncation toward zero is not corrected, producing an off-by-one error in the integer conversion.

The correct condition should be `x < 0 && (x & MASK(FRACTIONAL_PERCISION_4__BIT_SIZE))`, which checks whether x is negative and has a non-zero fractional part (lower 4 bits are non-zero). The current condition `x < 0 && -x < BIT(4)` only catches values where the entire magnitude fits in 4 bits, missing all negative fractional values with integer part ≤ -1.

**Bug 2 — Incorrect floor correction in the callee `normalize_i32__to_tile_u8`:**
The function delegates to `normalize_i32__to_tile_u8`, which computes `(trunc(y / 8) - (y < 0)) mod 8`. The `- (y < 0)` term is intended to convert truncation toward zero to floor, but it is applied unconditionally for all negative y. This is only correct when y is not a multiple of 8: for negative multiples of 8, `trunc(y / 8)` already equals `floor(y / 8)`, so subtracting 1 produces `floor(y / 8) - 1` instead of `floor(y / 8)`.

**Combined effect:**
These two bugs interact. For most negative fractional values, Bug 1 leaves the intermediate integer uncorrected, but Bug 2's over-correction happens to compensate, yielding the correct final result. However, for fixed-point values that are exact multiples of 8.0 (e.g., x = -128 representing -8.0, x = -256 representing -16.0), the intermediate integer is a negative multiple of 8, and Bug 2 produces an incorrect result with no compensating effect from Bug 1.

Example trace for x = -128 (fixed-point -8.0):
- `i32F4_to__i32(-128)` = trunc(-8.0) = -8
- Correction: not applied (-x = 128 ≥ 16)
- `normalize_i32__to_tile_u8(-8)`:
  - `ARITHMETRIC_R_SHIFT(-8, 3)` = trunc(-1) = -1
  - `- (x < 0)` = -1 - 1 = -2 (incorrect: should be -1)
  - `ARITHMETRIC_MASK(-2, 7)` = 6
- Result: 6
- Expected: floor(-8.0 / 8) mod 8 = floor(-1.0) mod 8 = 7
- Mismatch confirmed.

Implementation Correctness:
Type compatibility — parameter type i32F4 (int32_t) is compatible with the argument expected by i32F4_to__i32 (i32F4). The boolean expression (x < 0 && -x < ...) evaluates to 0 or 1 (int), which is compatible with subtraction from Signed_Index__i32 (int32_t). The return type Index__u8 (uint8_t) matches the return type of normalize_i32__to_tile_u8. No implicit conversions or truncation issues.
Undefined behavior — no pointer arithmetic, no null dereference, no type punning, no out-of-bounds access. The function is pure.
Validation — no validation is needed; this is a low-level arithmetic utility. The caller is responsible for providing a valid i32F4 value.

Side Effects:
No side effects — the function is pure, performing only arithmetic computation and returning a value.
