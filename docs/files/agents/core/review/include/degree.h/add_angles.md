# Function Review: add_angles

## 1. Header

- **Function name:** `add_angles`
- **File of origin:** `core/include/degree.h`

## 2. Semantic

Adds two `Degree__u9` angles and wraps the result around the full 360° circle (modulo 512, since the degree system uses 512 units per revolution).

## 3. Pre-conditions

1. `angle_1` must be a valid `Degree__u9` value in the range `[ANGLE__0, ANGLE__360 - 1]`, i.e., `[0, 511]`. If `angle_1 >= 512` the result will be meaningless.
2. `angle_2` must be a valid `Degree__u9` value in the range `[0, 511]` for the same reason.
3. Bounds checking is **not** performed inside the function; callers are expected to validate inputs using `is_degree_u9__out_of_bounds(angle)` beforehand (consistent with the rest of the `degree.h` API surface, e.g., `subtract_angles` follows the same convention).

## 4. Post-conditions

- Returns a `Degree__u9` value in the range `[0, 511]` representing `(angle_1 + angle_2) mod 512` — **but only if `ANGLE__MASK` were correctly defined as `MASK(9)` (= 511)**. In the current implementation the returned value is `(angle_1 + angle_2) & 31`, which is in the range `[0, 31]` and does **not** represent the intended modular sum.
- The inputs `angle_1` and `angle_2` are passed by value and are not modified.

## 5. Correctness Verdict

**Incorrect**

The function is intended to add two angles and wrap modulo 512 (one full circle), but `ANGLE__MASK` is defined as `MASK(5)` (= 31), which only preserves the lowest 5 bits of the sum. For any sum >= 32 the higher bits are silently discarded, producing a value that bears no meaningful relationship to the intended modular sum.

For example:
- `add_angles(ANGLE__90, ANGLE__90)` = `(128 + 128) & 31` = `256 & 31` = `0` — but 90° + 90° should be 180° (`ANGLE__180` = 256).
- `add_angles(ANGLE__45, ANGLE__45)` = `(64 + 64) & 31` = `128 & 31` = `0` — but 45° + 45° should be 90° (`ANGLE__90` = 128).
- `add_angles(ANGLE__180, ANGLE__180)` = `(256 + 256) & 31` = `512 & 31` = `0` — this happens to be correct (360° wraps to 0°) **by coincidence**.

The correct mask for a 512-unit circle is `MASK(9)` (= 511), which would make `(angle_1 + angle_2) & 511` equivalent to `(angle_1 + angle_2) mod 512`.

The sibling function `subtract_angles` (same file, lines 34–42) correctly wraps at `ANGLE__360` (512) for its wrap-around branch. This inconsistency is documented in `agents/core/modules/math.md` (line 11): *"add masks with `ANGLE__MASK` (= 31), so it wraps at 45° — an inconsistency, not 360°."*

## 6. Semantic Alignment

**Does not fulfill semantic intent.** The intent — signaled by the function name, the naming convention of the `Degree__u9` type, the 512-unit circle established by `ANGLE__360`, and the wrapping behavior of `subtract_angles` — is to perform modular addition over a full circle. The implementation instead truncates the sum to 5 bits. The arithmetic approach (add then bitwise-AND with a mask) is the *correct* strategy for a power-of-two modulus, but the mask used (`ANGLE__MASK` = 31) is wrong; it should be `MASK(9)` (= 511) to match the 9-bit angle system.

## 7. Implementation Correctness

- **Type compatibility:** `angle_1` and `angle_2` are both `Degree__u9` (`uint16_t`). The expression `angle_1 + angle_2` undergoes integer promotion to `int`, then the `&` with `ANGLE__MASK` (a `u32` literal from the `MASK` macro) promotes the result to `uint32_t`. The final implicit conversion back to `uint16_t` on return is safe because the masked value is small (≤ 511 when correct, currently ≤ 31). No truncation or sign-conversion issues arise.
- **Undefined behavior:** None. There is no pointer dereference, no out-of-bounds array access, no division, and no type punning. The bitwise operations are well-defined for unsigned operands.
- **Validation:** No input validation is performed. This is appropriate for the function's role — it is a lightweight `static inline` helper, and bounds validation is delegated to the caller via the separate `is_degree_u9__out_of_bounds` predicate. This matches the pattern used by every other function in `degree.h`.
- **Note on the root cause:** The defect originates in the definition of `ANGLE__MASK` in `core/include/defines.h` line 106: `#define ANGLE__MASK MASK(5)`. Given that the angle type is `Degree__u9` (9-bit, 512 values) and `ANGLE__360` = 512, the mask should be `MASK(9)` (= 511). `MASK(5)` (= 31) only covers 5 bits (32 values), which is incorrect for this degree system.

## 8. Side Effects

No side effects. The function is pure: it takes two value parameters, performs arithmetic, and returns a computed `Degree__u9` result without reading or modifying any global state, memory, or I/O.
